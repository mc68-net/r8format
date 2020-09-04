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
      consumed; its return value will be appended to `olist`.
    - `err`: Failure/error flag. When unable to successfully parse the
      input `err=None` will return a failure and anything else will raise
      an error with the that value in the error message/exception.

'''

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
        return self.pos >= len(self.input)

    def output(self):
        ''' Return the joined-together `olist`.

            The object used for joining will be a new instance of the class
            of the first object in the list. E.g., if the first object is
            `b'0x01'`, `bytes().join(olist)` will be called.

            If `olist` is empty, `None will be returned. (XXX This may not
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

def generate(p, x):
    ' Append an output item to `PState.olist`. '
    p.olist.append(x)

def peek(p):
    ''' Return the next item in the input sequence or `None` if there is
        no input left. The parse position is not moved.
    '''
    if p.pos >= len(p.input):
        return None
    else:
        return p.input[p.pos]

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
    x = p.input[p.pos]
    p.pos += 1
    if genf is not None:
        generate(p, genf(x))
    return x

def spaces(p):
    ''' Consume zero or more space characters, generating no output.
        This works on any input containing `str(' ')` or `ord(' ')` values,
        including `str` and `bytes`.
    '''
    while peek(p) in (' ', ord(' ')):
        p.pos += 1

def decimal(p, err=None):
    ''' Consume an unsigned decimal number and return it as an `int`.
        If `err` is `None`, return `None` on failure, otherwise raise a
        `ParseError` with message 'expecting `err`'.
    '''
    def fail():
        if err is None: return None
        p.error('expected ' + err)
    digits = ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9')

    if peek(p) not in digits: return fail()
    s = ''
    while True:
        if peek(p) not in digits: break
        c = byte(p); s = s + c
    return int(s)

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
        if p.input[p.pos:].startswith(x):
            p.pos += len(x)
            generate(p, y)
            return x
    return None
