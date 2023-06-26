from    bastok.tlines  import TLines
from    bastok.parser  import Parser, toksort
from    bastok.msx2  import TOKENS, NEGATIVE
from    struct  import pack
import  re

ENCTOKENS = toksort(TOKENS, 1, 0)

def tokenize(charmap, lines, txttab=0x8001):
    ''' Tokenise a sequence of lines of BASIC code, returning them in
        a `TLines` object with a start address of `txttab`.
    '''
    tl = TLines(txttab)
    for l in lines:
        #   XXX check for duplicate line no?
        ln, tokens = tokline(charmap, l)
        from sys import stderr
        tl.setline(ln, tokens)
    return tl

def tokline(charmap, line):
    ''' Tokenize a line of BASIC. Return an `(int, bytes)` tuple with
        the line number and tokenized line data or raise a `ParseError`
        if parsing fails.
    '''
    #   Possibly we want to change this API so that we can tokenize line
    #   fragments that do not start with a line number.
    p = Parser(line, charmap)
    ln = linenum(p, gen=False, err='line number')
    space(p, False)
    while not p.finished():
        #   Start by checking for a token, since any string matching a
        #   token takes priority over anything else.
        t = toktrans(p, ENCTOKENS)
        if t is not None:
            #   Tokens that consume and generate the remainder of the line.
            if t == 'REM':  chars(p)
            if t == "'":    chars(p)
            if t == 'DATA': chars(p)    # XXX no space compression yet!
            #   Tokens that take special arguments.
            if t == 'GOTO' or t == 'GOSUB':
                spaces(p); linenum(p, err='line number after GOTO')
            if t == 'THEN':
                spaces(p); linenum(p)   # linenum or other tokens
            continue
        #   If not a token, we try to match the various other constants.
        if string_literal(p)    is not None: continue
        if ampersand_literal(p) is not None: continue
        if digits(p)            is not None: continue
        #   Failing that, read and generate the next byte.
        byte(p, genf=lambda c: bytes([ord(c)]))

    return (ln, p.output())

class EncodingError(ValueError): pass

def data(p):
    p.error('XXX Write DATA parser!')

def digits(p, gen=True, err=None):
    ''' Convert digits to an appropriate internal representation.

        This is more complex than it seems becuase the type cannot be
        determined syntactically: the size of the number and presence of an
        exponent may change the type, sometimes even overriding the
        trailing type character.
    '''
    d = match_digits(p)
    if d is None: return
    consume, neg, i, f, te = d

    def genint(neg, i):
        ''' BASIC 16-bit int format is always non-negative 0-32767, with
            a prefixed `NEGATIVE` token if negative. For convenience this
            returns i, made negative if `neg`.
        '''
        if neg: p.generate(NEGATIVE)
        if i > 32767:
            #   XXX Sadly, the number was consumed by match_digits() so our
            #   parse pointer is wrong, and the 'after' part in the message
            #   doesn't cover the whole int for reasons that need to be
            #   investigated. Not clear how to fix this yet.
            p.error('int Overflow: {}'.format(i))
        if i < 10:
            p.generate(bytes([0x11 + i]))
        elif i < 256:
            p.generate(pack('<BB', 0x0F, i))
        else:
            p.generate(pack('<BH', 0x1C, i))
        p.consume(consume)
        if neg: return -i
        else:   return i

    if te == '%':   #   Forcing int with % truncates any fractional part.
        return genint(neg, int(i))
    if f is None and te is None:
        return genint(neg, int(i))

    p.error('XXX write me')

    #   MSX-BASIC numeric representations are always positive, so generate
    #   a leading ``-`` token for negative numbers and the proceed with the
    #   positive version.
    if i < 0:
        p.generate(NEGATIVE)
        i = abs(i)

    # print(i,f,e,t) # XXX
    if i >= 32768 or e is not None or t in ['!', '#']:
        if e is None: e = 0
        if f is None: f = 0
        #   XXX need D vs. E here for 1.2d3! → "\x1F…!"
        #   XXX also remember: 1e0% → "\x1D…%"
        return None

#   XXX This should also be documented in programs/*?
''' Numbers are parsed as follows:
    1. Optional leading `-` sign; always encodes as token $F2.
    2. Integer portion, at least 1 digit required if no fractional
       portion. (The regexp does not handle this latter requirement.)
    3. Optional fractional portion: `.` followed by 0 or more digits.
    4. Optional type or exponent, but never both.
       - Type is one of ``[%!#]``. (`%` truncates fractional portion.)
       - Exponent is one of ``[dDeE]``, an optional minus sign, and
         optional digits. Note that the ``D`` and ``E`` are considered
         equivalent: BASIC always uses single precision if the
         significand will fit, otherwise double precision with truncation.
'''
MATCH_DIGITS = re.compile(r'(-)?(\d*)(\.\d*)?([%!#]|[dDeE]-?\d*)?')

def match_digits(p):
    ''' Parse basic syntax of number formats for all types of numbers
        into a 5-tuple. Since parsing can still fail after this, nothing
        is consumed but the number of characters to consume on success
        is returned.

        This is parsed based on a match of `MATCH_DIGITS` above. Failure
        to match returns `None`. Otherwise a the 5-tuple is the following:

        0. Number of chars matched, which should be consumed if the parse
           is successful.

        1. Negative: `int` of 0 (positive) or -1 (negative).

        2. Integer portion: `str` of 0 or more ASCII digits. Always present.

        3. Fractional portion: `None` if not present, or a `str` of zero or
           more ASCII digits if present. (A decimal point with no following
           digits produces an empty `str` as a trailing `.` makes the number
           parse as a float.)

        4. Type or exponent portion:
           - Not present: `None`
           - Type: `str` of ``'%'``, ``'!'`` or ``'#'``.
           - Exponent: `int` (positive or negative).
             (This must be biased by the caller before tokenisation.)
    '''
    m = MATCH_DIGITS.match(p.remain())
    if m is None: return None

    neg = -1 if m.group(1) else 0
    i = m.group(2); f = m.group(3);
    if (i == '') and (f is None):
        return None
    if f is not None: f = f[1:]
    te = m.group(4)
    if (te is not None) and (te not in ('%', '!', '#')):
        if len(te) == 1: te += '0'  # D/E alone indicates exponent of 0
        te = int(te[1:])
    #print('neg:', repr(neg), 'i:', repr(i), 'f:', repr(f), 'te:', repr(te))

    return (m.end(), neg, i, f, te)

AMPERSAND_PREFIXES = set([ '&H', '&h', '&O', '&o', '&B', '&b'])
BINDIGITS = ('0', '1')
OCTDIGITS = BINDIGITS + ('2', '3', '4', '5', '6', '7')
HEXDIGITS = OCTDIGITS \
    + ('8', '9', 'A', 'a', 'B', 'b', 'C', 'c', 'D', 'd', 'E', 'e', 'F', 'f')

def ampersand_literal(p):
    ''' Read and consume ``&Hnnnn``, ``&Onnnn`` and ``&Bnnnn`` integer
        literals. Raises a `ParseError` saying "Overflow" if the number
        exceeds 2^16.
    '''
    if p.remain()[0:2] not in AMPERSAND_PREFIXES:
        return None
    #   If we have the prefix, we have the number; lack of valid digits
    #   after the prefix just means that the number is 0.

    def read(base, basedigits):
        i = 2; s = ''
        while p.remain()[i:].startswith(basedigits):
            s += p.remain()[i]; i += 1
        if s == '':
            p.consume(2)
            return 0
        else:
            n = int(s, base)
            if n > 0xFFFF:
                p.error('Overflow'.format(base, s))
            p.consume(2 + len(s))
            return n

    base = p.remain()[1].upper()
    if base == 'H':
        return read(16, HEXDIGITS)
    elif base == 'O':
        return read(8, OCTDIGITS)
    elif base == 'B':
        return read(2, BINDIGITS)
    raise RuntimeError('Internal error: bug!')

def linenum(p, gen=True, err=None):
    ''' Consume the ASCII representation of a line number and return it as
        an `int`. Like the MS tokeniser, this accepts negative line numbers
        even though the interpreter will throw a 'Syntax error' when it
        tries to execute them.

        If `gen` is true, generate the MSX-BASIC tokenised representation
        of the number: $0E followed by a little-endian word. (Prefixed
        by a syntactically incorrect `NEGATIVE` token if the number
        started with ``-``.)

        If `err` is `None`, return `None` on failure, otherwise raise a
        `ParseError` with message 'expecting `err`' if the number was
        unparsable, or 'outside linenum range' if the number was parsed
        but is < 0 or > 65529.
    '''
    def fail():
        if err is None: return None
        p.error('expected ' + err)

    p.start()

    neg = False
    if p.string('-'): neg = True

    ds = ''
    while True:
        d = p.decdigit()
        print('{}+{}'.format(ds, d))
        if d is None:
            break
        else:
            ds += d
    if ds == '':
        if err is None: return None
        p.error('no linenum found')
    n = int(str(ds))
    if n > 65529:   # XXX probably should not be hard-coded!
        p.error('{} outside linenum range'.format(n))
    uint_16 = pack('<H', n)
    if gen:
        if neg: p.generate(NEGATIVE)
        p.generate(b'\x0E' + uint_16)
    p.confirm()
    return -n if neg else n

def string_literal(p, err=None):
    ''' Consume a string literal starting with `"` and ending with the next
        `"` or end of input, generating its Parser.charset conversion and
        MSX-BASIC encoding. The intial and final quotes are not
        charset-converted.

        Return the consumed input string, including quotes.
    '''
    DQUOTE = '"'
    s = ''
    if p.peek() != DQUOTE:
        if err is None: return None
        raise p.ParseError('{}: {}'.format(err, repr(p.peek())))
    byte(p); p.generate(b'"'); s += DQUOTE
    while True:
        c = p.peek()
        if c == None: return s
        if c == DQUOTE: byte(p); p.generate(b'"'); return s + DQUOTE
        s += char(p)

def space(p, generate=True):
    ' Consume a single space, if present. '
    if p.peek() in (' ', ord(' ')):
        if generate: char(p)
        else:        p.consume()

def spaces(p, generate=True):
    ''' Consume zero or more Unicode space characters.

        If `generate` is `True` these will be generated into the output
        (using the usual Unicode to native translation), otherwise they
        will be silenty consumed.
    '''
    while p.peek() in (' ', ord(' ')):
        if generate: char(p)
        else:        p.consume()

def chars(p):
    ' Do char() until EOF. '
    while char(p, err=None): pass

def char(p, err='unexpected end of input'):
    ''' Consume a Unicode character from the input, translate it to an
        native character using the `PState` `p`'s `charmap`, generate the
        native character to the output using MSX encoding, and return the
        Unicode character read.

        If no character is available from the input a `ParseError` with
        message `err` will be raised. `err` may be set to `None` to instead
        fail by returning `None`.

        MSX code points are encoded as follows:
        - 0x20-0x7E, 0x80-0xFF: One byte containing the code point.
        - 0x00-0x1F: 0x01 byte followed a byte with the code point + 0x40.
        - 0x7F: Cannot be encoded; raises `EncodingError`.
    '''
    c = byte(p, err=err)
    if c is None: return None

    if not p.charset:
        p.error('No charset provided for translation')
    else:
        n = p.charset.native(c)
    if n == 0x7F:
        raise EncodingError('cannot encode char 0x7F')
    if n < 0x20:
        encoded = bytes([0x01, n+0x40])
    else:
        encoded = bytes([n])
    p.generate(encoded)
    return c
