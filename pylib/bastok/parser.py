''' Parser Framework.

    This consists of class `PState`, multable instances of which hold
    parser state, and some generic parsing functions that operate on it.
    Typically further special-purpose parsing functions will be added by
    each particular parser.

    Parsing functions always take a `PState` as the first parameter. They
    may do (almost) any combination of the following:
    - *Consume* input, updating `pos` if successful.
    - *Generate* output, appending the output fragment to `PState.olist`.
    - *Return* a value.
    - *Fail*, consuming and generating nothing and returning an indication
      of failure (but not throwing an exception).
    - *Error*, consuming nothing and raising an exception.

    Typical additional parameters that parsing functions may have are:
    - Something to match. The parser will fail or error if the input at the
      current position does not match this parameter.
    - `genf`: A generator function that is passed the data about to be
      consumed; its return value will be appended to `olist`. Nothing
      is generated if ``genf=None``.
    - `err`: Failure/error flag. When unable to successfully parse the
      input `err=None` will return a failure and anything else will raise
      an error with the that value in the error message/exception.

'''

import  struct

class PState:
    ''' A mutable parser state, consisting of:

        - An `input` sequence (never mutated) of parser-dependent type
          (usually `str` or `bytes`) that is *consumed* by the parser.
        - The current parse position in the input, `pos`.
        - A `list` `olist` of fragments of parser-dependent type (usually
          `bytes` or `str`) that when joined together are the output of
          the parser.
        - An optional `Charset` for translating between Unicode and
          native-encoded characters, for those parser functions that
          need to do this.

        To enhance modularity and avoid name conflicts, this class does
        not include any parsing functions, just basic handling of
        state and the ability to raise errors.
    '''

    def __init__(self, input, charset=None):
        self.input = input
        self.pos = 0
        self.olist = []
        self.charset = charset

    def finished(self):
        ' Return `true` if we have consumed all input. '
        return self.pos >= len(self.input)

    def consume(self, n=1):
        ''' Consume _n_ elements of the input (default 1)
            and return the consumed input.
            Raise a `ParseError` if we try to consume past end of input.
        '''
        if self.pos + n > len(self.input):
            self.error('Consumed past end of input: {} > {}' \
                .format(self.pos + n, len(self.input)))
        self.pos += n
        return self.input[self.pos-n:self.pos]

    def peek(self):
        ''' Return the next element of the the input sequence, or `None` if
            there is no input left. The parse position is not moved.

            XXX Should this raise an exception if no more input? Perhaps
            should take param like byte().
        '''
        if self.pos >= len(self.input):
            return None
        else:
            return self.input[self.pos]

    def remain(self):
        ' Return the remaining unconsumed input. '
        return self.input[self.pos:]

    def generate(self, x):
        ''' Append an output element to `olist`.
            All elements in the list must be the same type or a subtype
            of the first element added or a `ParseError` will be raised.
        '''
        if len(self.olist) == 0 or isinstance(x, type(self.olist[0])):
            self.olist.append(x)
        else:
            self.error('Cannot generate {}: {} not an instance of {}.' \
                .format(repr(x), type(x), type(self.olist[0])))

    def output(self):
        ''' Return the joined-together `olist`.

            The object used for joining will be a new instance of the class
            of the first object in the list. E.g., if the first object is
            `b'0x01'`, `bytes().join(olist)` will be called.

            If `olist` is empty, `None` will be returned. (XXX This may not
            be the correct behaviour for this case.)
        '''
        if len(self.olist) == 0:
            return None
        cls = type(self.olist[0])
        return cls().join(self.olist)

    def __str__(self):
        p = self.pos
        return 'at {}:{} after …{} …{}'.format(
            p, repr(self.input[p:p+8]),
            repr(self.input[p-8:p]), self.olist[-4:])

    class ParseError(ValueError): pass

    def error(self, message):
        raise self.ParseError(message + ' ' + str(self))

####################################################################
#   Parsing Functions
#
#   These will operate on any state conforming to the interface above.

def byte(p, *, genf=None, err='unexpected end of input'):
    ''' Return the next item in the input sequence, and advance the parse
        position by 1. Despite the name, the return type is determined by
        the underlying sequence (`int` for `bytes`, `str` for `str`).

        This function can fail only when there is no further input. If
        `err` is `None`, `None` will be returned in this case, otherwise a
        `ParseError` will be raised with `err` as the message.

        By default, no output is generated. If `genf` is given the item
        read will be passed to that function and the returned value will be
        appended to the output.
    '''
    if p.finished():
        if err is None: return None
        p.error(err)
    x = p.consume()[0]
    if genf is not None:
        p.generate(genf(x))
    return x

def uint16(p, gen=True, err=None):
    ''' Consume the ASCII representation of an unsigned 16-bit integer and
        return it as an `int`.

        If `gen` is true, generate the MSX-BASIC tokenised representation
        of the number: $0E followed by a little-endian word.

        If `err` is `None`, return `None` on failure, otherwise raise a
        `ParseError` with message 'expecting `err`' if the number was
        unparsable, or 'too large for uint16' if the number was parsed
        but is < 0 or > 65535.
    '''
    def fail():
        if err is None: return None
        p.error('expected ' + err)
    digits = ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9')

    if p.peek() not in digits: return fail()
    s = ''
    while True:
        if p.peek() not in digits: break
        c = byte(p); s = s + c
    n = int(s)
    try:
        uint_16 = struct.pack('<H', n)
    except struct.error:
        p.error('{} outside uint16 range'.format(n))
    if gen: p.generate(b'\x0E' + uint_16)
    return n

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

def toktrans(p, toktab):
    ''' Given a translation table `toktab` of *(x,y)* pairs, try to match
        each *x* in turn against the input at the current parse position.
        The first *x* that matches will cause the matched input to be
        consumed, *y* to be generated (appended to `olist`) and *x* will be
        returned. If no *x* matches, no input will be consumed, nothing
        will be generated, and `None` will be returned.

        If some *x*s are prefixes of other *x*s, you must sort `toktab`
        to place the longer *x*s before their prefixes if you want all
        *x*s to be able to match.

        The input sequence must support the `startswith` function.
    '''
    for x, y in toktab:
        if p.remain().startswith(x):
            p.consume(len(x))
            p.generate(y)
            return x
    return None
