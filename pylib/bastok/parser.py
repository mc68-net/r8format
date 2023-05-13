''' Parser Framework.

    The `Parser` class contains parser and output generation state and
    generic functions for operating on these. (More application-specific
    functions are provded by the caller or subclasses.)
'''

import  re
import  struct

class Parser:
    ''' A parser with mutable state consisting of:

        - An `input` sequence (never mutated) of application-dependent type
          (usually `str` or `bytes`) that is _consumed_ by the parser.
          Individual items in this sequence are called _elements._ Note
          that the element data type is not necessarily the same as the
          sequence data type. (It is for `str`, but that's because Python
          is odd in having no character type.) The `strinput` instance
          variable is `True` if the input sequence type is `str`,
          indicating that Unicode input is being parsed.
        - Two current parse positions in the input: `pos_committed` and
          `pos_pending` (see below for more details).
        - An optional `charset` for translating between Unicode and the
          `input` type when `input` is not a `str`. This should follow the
          `Charset` interface: `trans(n)` for native code point to `str`,
          and `native(s)` for a single Unicode char to native. XXX This
          should actually be a codec and deal with encoding as well as code
          points?
        - Two output lists, `olist_committed` and `olist_pending`. (See
          below for more on committed vs. pending.) These contain list
          fragements that when joined together are the output of the
          parser. `generate()` adds new fragments to the ouptut list.

        Additional data that may be supplied are:
        - `tokens`, a sequence of ``(token_text, tokenized)`` pairs used
          by `token()`.

        `Parser` use constant data that depends on the input sequence and
        element types that can be expensive to initialise; the
        `reset(input)` function is provided to allow re-using the `Parser`
        instance for new input.

        Methods (Functions)
        -------------------

        The public methods supplied by this class fall the following
        categories. (Methods starting with ``_`` are not intended to be
        part of the public API.)

        1. Parser status and control. These do not depend on the types of
           the input or output lists. `reset()`, `inputtype`, `strinput`,
           `start()`, `commit()`, `finished()`, `remain()`, `uncommitted()`.

        2. Error handling and display. `ParseError`, `error()`,
           `__str__()`.

        3. Output generation. These are the only methods that generate
           output. Note that a few parser status and control methods also
           handle the output list, but have no dependency on the output
           list type or output list element type. `generate()`, `output()`,
           `output_pending()`.

        4. Encoding-related methods, mainly used by parsing methods.
           `encode_elem()`, `encode_seq()`.

        5. Parsing methods. These are the only methods that attempt to
           match and consume elements in the input. Any text to match
           is always of `str` type; if the input type is not `str` the
           Parser attempts to convert the `str` parameter(s) to the input
           type.

           If a parsing method fails to match, it generally returns `None`
           and consumes nothing. (Some parsing methods may instead throw a
           `ParseError`.)  Otherwise it returns a truthy value (usually a
           sequence of the matching input elements) and updates the
           _pending_ parse point. (These methods never call `start()` or
           `commit()`.)

           When elements of the input are returned, they are of the same
           type as the input. For non-`str` inputs, you may need to pass
           these return values to `str()` or do other appropriate processing
           before before doing further work with them.

           These methods include `peek()`, `consume(count)`, `string(s)`,
           `string_in(strs)`, `re_compile()`, `re_match()`, `digit()`,
           `digits()`, `token()`.

        Committed and Pending Parse Points and Output Lists
        ---------------------------------------------------

        The parser has two parse points and output lists: "committed" and
        "pending."
        - `start()` sets the pending parse point to the committed parse
          point; and clears any pending output. This should be used by a
          routine that is not yet sure that it's going to consume the
          following text without an error.
        - Matching routines such as `string()`:
          - On success advance the pending parse point and return the input
            that matched or a value derived from it.
          - On failure leave the pending parse point unchanged and return
            `None`.
          - Note that parsing routines supplied in this class never
            `start()` or `commit()`, as they're intended to be used as
            components within a larger parser.
        - `commit()` sets the committed parse point to the pending parse
          point and appends all pending output to the committed output.

        Thus, your parsing routines should `start()` and then either:
        - Parse until they've succeeded, generating output as they go
          along, and then call `commit()`, or
        - Parse unti they've failed and just return.

        XXX `start()`/`commit()` possibly should be re-entrant, using
        a stack of committed and pending parse points.
    '''

    def __init__(self, input, charset=None, tokens=None):
        self.input      = input
        self._strinput  = None
        self.charset    = charset
        self.tokens     = tokens
        self.reset(input)

        #   Constants used by parsing routines. Any constants that rely
        #   on the charset being able to convert Unicode chars they need
        #   to native chars must be lazily initialised, so that the Parser
        #   works for Charsets that cannot do that conversion so long as
        #   the methods that need them are not called.
        self.DIGITS     = dict()    # base → set of digits in that base
        self.toktab     = None      # sorted token table

    ####################################################################
    #   Parser status and control

    def reset(self, input=None):
        ''' Reset the parser to the initial state, possibly with new input.
            If new input is provided, the input sequence type and element
            type must be the same as the original types with which the
            `Parser` was instantiated.
        '''
        def err(name, newtype, oldtype):
            raise ValueError('reset: new input {} type {} ' \
                'not instance of old input {} type {}' \
                .format(name, newtype, name, oldtype))

        if input is not None:
            seq_type = type(self.input)
            if not isinstance(input, seq_type):
                err('sequence', type(input), seq_type)
            if len(input) > 0 and len(self.input) > 0:
                elem_type = type(self.input[0])
                if not isinstance(input[0], elem_type):
                    err('element', type(input[0]), elem_type)
            self.input = input
            self._inputtype = type(self.input)
            self._strinput = isinstance(self.input, str)

        self.transaction_pending = False
        self.pos_committed      = 0
        self.pos_pending        = 0
        self.olist_committed    = []
        self.olist_pending      = []

    @property
    def inputtype(self):
        ' Return the type/constructor for the input type. '
        return self._inputtype

    @property
    def strinput(self):
        ''' `True` if the input sequence type is `str` (and thus the input
            element type, too), indicating we're parsing Unicode input.
            This indicates that parsing functions taking `str` will not
            need to do conversion on them, and any that return values of
            the input type will also return `str`.

            `False` if the input sequence and element types are anything
            other than `str`.
        '''
        return self._strinput

    def pending(self):
        ''' Return True if there are any uncommitted consumed characters
            or any uncommited output. This is not the same thing as being
            in a transaction since, even if we've not explicitly started
            a transaction all consumption and output routines are pending
            consumption and output until `commit()` is called.
        '''
        return self.pos_pending != self.pos_committed \
            or len(self.olist_pending) > 0

    def rollback(self):
        ' Set pending parse point back to the committed parse point. '
        self.transaction_pending = False
        self.pos_pending = self.pos_committed
        self.olist_pending = []

    def commit(self):
        ''' Move committed parse point forward to the pending parse point
            and add all pending output to the committed output list.
        '''
        self.pos_committed = self.pos_pending
        self.olist_committed.extend(self.olist_pending)
        self.olist_pending = []
        self.transaction_pending = False

    def finished(self):
        ''' Return `True` if the _pending_ parse point is at the end
            of the input.
        '''
        return self.pos_pending >= len(self.input)

    def remain(self):
        ' Return what remains after the _pending_ parse point. '
        return self.input[self.pos_pending:]

    def uncommitted(self):
        ''' Return what remains after the _committed_ parse point.

            This is normally used only for testing, error information or
            other unusual situations.
        '''
        return self.input[self.pos_committed:]

    def transactional(f):
        def wrap(p, *args, **kwargs):
            if p.pending():
                raise RuntimeError('Cannot start transaction with pending'
                    ' consumption ({}) or output ({})'.format(
                        repr(p.input[p.pos_committed:p.pos_pending]),
                        repr(p.output_pending())))
            if p.transaction_pending:
                raise RuntimeError('Illegal attempt to nest transactions')
            p.transaction_pending = True
            wrapped_return = f(p, *args, **kwargs)
            if isinstance(wrapped_return, Parser.FAILURE):
                return None
            if isinstance(wrapped_return, Parser.SUCCESS):
                if wrapped_return.retval is not None:
                    return wrapped_return.retval
                else:
                    raise RuntimeError('Parser.success() cannot return None')
            raise RuntimeError(
                'transactional parser did not return success or failure')
        return wrap

    class FAILURE:  pass
    class SUCCESS:
        def __init__(self, retval): self.retval = retval

    def success(self, retval):
        self.commit()
        return self.SUCCESS(retval)

    def failure(self):
        self.rollback()
        return self.FAILURE()

    ####################################################################
    #   Error handling and display

    class ParseError(ValueError): pass

    def error(self, message):
        raise self.ParseError(message + ' ' + str(self))

    def __str__(self):
        p           = self.pos_pending
        ucp         = p - self.pos_committed
        pos_text    = repr(self.input[p:p+12])
        prev_text   = repr(self.input[ max(p-12,0) : p ])
        output      = (self.olist_committed + self.olist_pending)[-4:]
        return 'at {}:{} after …{} (pending={} output …{})' \
            .format(p, pos_text, prev_text, ucp, output)

    ####################################################################
    #   Generation Methods

    def generate(self, x):
        ''' Append an output element to the pending output list.
            These elements will not be moved to the committed output list
            until `commit()` is called.

            All elements in the list must be the same type or a subtype of
            the first element added or a `ParseError` will be raised.
        '''
        prev = self.olist_committed[0:1] + self.olist_pending[0:1]
        if len(prev) == 0 or isinstance(x, type(prev[0])):
            self.olist_pending.append(x)
        else:
            self.error('Cannot generate {}: {} not an instance of {}.' \
                .format(repr(x), type(x), type(prev[0])))

    def _output(self, olist):
        if len(olist) == 0:
            return None
        cls = type(olist[0])
        return cls().join(olist)

    def output(self, uncommitedAllowed=False):
        ''' Return the joined-together committed output list.

            The object used for joining will be a new instance of the class
            of the first object in the list. E.g., if the first object is
            `b'0x01'`, `bytes().join(olist_committed)` will be called.

            This will throw a `RuntimeError` if there is uncommited output
            available as that's almost certainly a sign that you forgot a
            `commit()` or `start()` (the latter to roll back) somewhere.
            You can disable this check by setting `uncommitedAllowed` to
            `True`.
        '''
        if not uncommitedAllowed and self.olist_pending != []:
            raise RuntimeError('attempt to get output when uncommited output'
                ' not committed or rolled back: {}'.format(self.olist_pending))
        return self._output(self.olist_committed)

    def output_pending(self):
        return self._output(self.olist_pending)


    ####################################################################
    #   Encoding-related methods

    def encode_elem(self, s):
        ''' Convert `str` `s`, which must be of length 1, to the input
            sequence element data type.
            (This is a no-op when the input sequence is a `str`.)

            This is normally used only by certain parsing routines in this
            class that take arguments giving text to match; those arguments
            are always `str` and the Parser deals with any conversion
            necesssary. Depending on the input sequence element type,
            conversion may not be possible, in which case those parsing
            methods that need to convert an argument cannot be used with
            that input sequence element type.
        '''
        #   Though native() should raise an Error of some sort if we pass
        #   it a str of length ≠ 1, we do our own check so that we produce
        #   a consistent error.
        if len(s) != 1:
            raise ValueError('encode_elem argument length {} != 1 for {}' \
                .format(len(s), repr(s)))
        if self.strinput:
            return s
        elif self.charset is None:
            raise TypeError('Parser of input {} must have a charset' \
                .format(type(self.input)))
        else:
            return self.charset.native(s)

    def encode_seq(self, s):
        ''' Convert each element of `str` `s` to the input sequence
            element data type, and return those elements as the input
            sequence type.
            (This is a no-op when the input sequence is a `str`.)

            This is normally used only by certain parsing routines in this
            class that take arguments giving text to match. See the header
            comment for `encode_all` for further information.
        '''
        if self.strinput:
            return s
        elif self.charset is None:
            raise TypeError('Parser of input {} must have a charset' \
                .format(type(self.input)))
        else:
            return self.inputtype(map(self.charset.native, s))

    ####################################################################
    #   Parsing Methods

    def peek(self):
        ''' Without consuming anything, return next input element at the
            _pending_ parse point, or `None` if at end of input.
        '''
        if self.pos_pending >= len(self.input):
            return None
        else:
            return self.input[self.pos_pending]

    def consume(self, count=1):
        ''' Consume and return the next `count` elements of the input
            (default 1). Raise a `ParseError` if we try to consume past
            end of input.
        '''
        if self.pos_pending + count > len(self.input):
            self.error('Unexpected end of input: {} > {}' \
                .format(self.pos_pending + count, len(self.input)))
        elems = self.input[self.pos_pending : self.pos_pending + count]
        self.pos_pending += len(elems)
        return elems

    def string(self, s):
        ' Consume and return elements matching the constant string `s`. '
        expected = self.encode_seq(s)
        next = self.input[self.pos_pending:self.pos_pending+len(expected)]
        if expected == next:
            return self.consume(len(expected))

    def string_in(self, strs):
        for s in strs:
            ret = self.string(s)
            if ret is not None:
                return ret
        return None

    def re_compile(self, s):
        ''' Compile a regexp given in `str` `s` to an `re.Pattern` regular
            expression object in the input type that can be passed to
            `re_match()`.
        '''
        return re.compile(self.encode_seq(s))

    def re_match(self, regexp):
        ''' Try to match `re` against the input and return a `Match` object
            if successful, consuming the matched input.

            This does not consume the matched text; the caller should
            ``consume(match.end())`` with the returned `Match` if it
            accepts the contents of the matched expression.

            The groups in the `Match` object will be of the input type.
            XXX not clear if we should try to convert back. Probably not?
        '''
        if not isinstance(regexp, re.Pattern):
            regexp = self.encode_seq(regexp)
        m = re.match(regexp, self.remain())
        return m

    def digit(self, base=10):
        ''' Return the next input element if it is a digit in the given
            `base` (default 10).

            If the input sequence is not a `str`, the `charset` must have
            native representations of the digits for the given base
            (`0`…`9`, `A`…, `a`…).
        '''
        if not base in self.DIGITS:
            digits = basedigits(base)
            digits = set(map(self.encode_elem, digits))
            self.DIGITS[base] = digits

        digits = self.DIGITS[base]
        next = self.peek()
        if next in digits:
            return self.consume(1)

    def digits(self, base=10):
        ds = self.inputtype()
        while True:
            d = self.digit(base)
            if d is not None:
                ds += d
            else:
                break
        if len(ds) > 0: return ds

    #   XXX what should we be doing about lower case in program text?
    #   Maybe add an `insensitive` property to Parser and have parse functions
    #   use that to determine if they're "liberal" in what they accept, e.g.,
    #   toktrans() will do a case-insensitive comparision on strings.

    def token(self):
        ''' Attempt to parse and generate the tokenized version of a token
            text.

            This uses the `tokens` map given to `__init__()`, which is a
            sequence of ``(token_text, tokenized)`` pairs, and tries to
            match the longest possible ``token_text`` from that map.

            On a match, it generates the second ``tokenized`` element and
            returns the ``token_text`` that matched. On no match, this
            returns `None`.
        '''
        if self.toktab is None:
            if self.tokens is None:
                raise ValueError('Parser.token(): no token table supplied')
            self.toktab = tuple(
                (token_text, self.encode_seq(token_text), tokenzied)
                for token_text, tokenzied in toksort(self.tokens, 1, 0)
            )
            #from sys import stderr; print(self.toktab, file=stderr) # XXX

        for token_text, encoded_text, tokenized in self.toktab:
            if self.remain().startswith(encoded_text):
                self.consume(len(encoded_text))
                self.generate(tokenized)
                return token_text
        return None


####################################################################
#   Support routines

ASCII_0 = ord('0')
ASCII_A = ord('A')
ASCII_a = ord('a')

def basedigits(base):
    ''' Return a set of all Unicode characters comprising the digits
        for a given base. This starts with the characters ``'0'``
        through ``'9'``, and proceeds after that from the letters
        ``'A'`` and ``'a'``, returning both upper- and lower-case
        letters in the set.
    '''
    digits = set()
    for i in range(0, min(base, 10)):
        digits.add(chr(ASCII_0 + i))
    for i in range(10, base):
        digits.add(chr(ASCII_A - 10 + i))
        digits.add(chr(ASCII_a - 10 + i))
    return digits

def toksort(toktab, field0=0, field1=1):
    ''' Given a sequence of tuples `toktab`, return a new sequence of
        pairs consisting of index `field0` followed by index `field1`
        of each input tuple, sorted by length of the `field0` entry.

        Regardless of the type of the input sequence and its tuples,
        a `tuple` of `tuple` is always returned.

        This is used to build a token table for use with `toktrans()`
        that matches longer prefixes before shorter.
    '''
    res = [ (f[field0], f[field1]) for f in toktab ]
    return tuple(sorted(res, key=lambda t: len(t[0]), reverse=True))
