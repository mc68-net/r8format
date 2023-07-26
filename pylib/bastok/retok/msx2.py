from    bastok.tlines  import TLines
from    bastok.parser  import Parser
from    bastok.detok.msx2  import TOKENS, NEGATIVE
from    itertools  import dropwhile
from    struct  import pack
import  re

def DEBUG(*args):
    from sys import stderr
    print('DEBUG:', *args, file=stderr)

def tokenize(charmap, lines, txttab=0x8001):
    ''' Tokenise a sequence of lines of BASIC code, returning them in
        a `TLines` object with a start address of `txttab`.
    '''
    tl = TLines(txttab=txttab)
    if len(lines) == 0:
        return tl
    parser = Parser(lines[0], charmap, TOKENS)
    for l in lines:
        #   XXX check for duplicate line numbers and replace?
        parser.reset(l)
        ln, tokens = tokline(parser)
        tl.setline(ln, tokens)
    #DEBUG('tlines:', repr(tl))
    return tl

def tokline(p):
    ''' Tokenize a line of BASIC in `Parser` `p`. Return an `(int, bytes)`
        tuple with the line number and tokenized line data or raise a
        `ParseError` if parsing fails.
    '''
    #   Possibly we want to change this API so that we can tokenize line
    #   fragments that do not start with a line number.
    ln = linenum(p, gen=False, err='line number')
    space(p, False)
    p.commit()

    #DEBUG('input:', p.input) # XXX
    #   At the start of every iteration, we commit what the previous
    #   iteration consumed and generated.
    while (p.commit() or True) and not p.finished():
        p.commit() # XXX
        #DEBUG('loop: remain={}'.format(repr(p.remain())))
        #   Start by checking for a token, since any string matching a
        #   token takes priority over anything else.
        t = p.token()
        if t is not None:
            #DEBUG('token={}'.format(repr(t)))
            p.commit()  # new start point for attempt to parse any argument
            #   Tokens that consume and generate the remainder of the line.
            if t == 'REM':  chars(p)
            if t == "'":    chars(p)
            if t == 'DATA': chars(p)    # XXX no space compression yet!
            #   Tokens that take special arguments.
            if t == 'GOTO' or t == 'GOSUB':
                spaces(p); linenum(p, err='line number after GOTO')
            if t == 'THEN':
                spaces(p); linenum(p)   # linenum or other tokens
            #DEBUG('handled token={}'.format(t)) # XXX
            continue
        #DEBUG('not token')
        #   If not a token, we try to match the various other constants.
        if string_literal(p)    is not None: continue
        if ampersand_literal(p) is not None: continue
        if number(p)            is not None: continue
        #   Failing that, pass the next byte straight through.
        #   This should _not_ be converted because it's not in a string,
        #   REM or DATA statement, and we simply don't know what it is.
        #   (The BASIC interpreter will deal with it if it's an error.)
        b = p.consume(1); p.generate(bytes([ord(b)]))

    p.commit()
    return (ln, p.output())

class EncodingError(ValueError): pass

def data(p):
    p.error('XXX Write DATA parser!')

def number(p, gen=True, err=None):
    ''' Convert digits to an appropriate internal representation.

        This is more complex than it seems becuase the type cannot be
        determined syntactically: the size of the number and presence of an
        exponent may change the type, sometimes even overriding the
        trailing type character.

        This returns `None` on failure, unless something goes terribly
        wrong in which case it raises a `ParseError`. On success it returns
        the string 'OK', because it's not worth trying to parse the number
        into Python format too when we don't need it and `True` is a bit
        confusing to return because it's also the `int` 1.
    '''
    d = match_number(p)
    if d is None: return None
    consume, neg, i, f, te = d      # `i`, `f` were converted to `str` for us

    #   MSX-BASIC numeric representations are always positive, so generate
    #   a leading ``-`` token for negative numbers and the proceed with the
    #   positive version.
    if neg:
        p.generate(NEGATIVE)

    #   It's an int if forced with `%` (truncating any fractional portion)
    #   or we have no type, no fractional portion and it's < 32768.
    if te == '%' or (f is None and te is None and int(i) < 32768):
        #   BASIC 16-bit int format is always non-negative 0-32767, with a
        #   prefixed `NEGATIVE` token (above) if negative.
        i = int(i)
        if i > 32767:
            p.error('int Overflow: {}'.format(i))
        if i < 10:
            p.generate(bytes([0x11 + i]))
        elif i < 256:
            p.generate(pack('<BB', 0x0F, i))
        else:
            p.generate(pack('<BH', 0x1C, i))

    else:       # Otherwise we must use float representation.
       #DEBUG('number() is float: neg={} i={} f={} te={}' \
       #    .format(neg, repr(i), repr(f), te))

        i = i.lstrip('0')
        if f is None:   f = ''
        if len(i) > 0:
            sigdigs = len(i) + len(f)
        else:
            sigdigs = len(f.lstrip('0'))

        if te == '!' or sigdigs <= 6:
            #   We don't check for an `e`-type exponent because that does not
            #   force 4-byte float; it uses the length of the significand.
            significand_bytes = 3   # 4 bytes - 1 for exponent
            p.generate(b'\x1D')
        else:
            significand_bytes = 7   # 8 bytes - 1 for exponent
            p.generate(b'\x1F')

        #   XXX need to remove leading '0's from `i` and f to go negative!
        i = ''.join(dropwhile(lambda d: d == '0', i))
        exponent = 0x40 + len(i)
        if len(i) == 0:     # no digits in i; we need to make neg exponent
            exponent -= len(f) - len(f.lstrip('0'))
            f = f.lstrip('0')
        p.generate(bytes([exponent]))

        digits = iter(i + f)
        bcd_digits = []
        for i in range(0, significand_bytes * 2):
            c = next(digits, '0')
            d = ord(c) - ord('0')
            bcd_digits.append(d)
            #DEBUG('c={} d={} bcd={}'.format(repr(c), d, bcd_digits))

        #   If we have another unused digit, we round based on that.
        d3 = ord(next(digits, '0')) - ord('0')
        if d3 >= 5:
            #   But first have to decide if we do it correctly
            #   or the Microsoft™ way: 0.99999999! → .1
            pass

        bcd_it = iter(bcd_digits)
        for d1, d2 in zip(bcd_it, bcd_it):
            bcdpair = (d1 << 4) + d2
            p.generate(bytes([bcdpair]))

    p.consume(consume)
    return 'OK'

#   XXX This should also be documented in programs/*?
''' Numbers are parsed as follows:
    1. Optional leading `-` sign; always encodes as token $F2.
    2. Integer portion, at least 1 digit required if no fractional portion.
       (The regexp does not handle this latter requirement.)
    3. Optional fractional portion: `.` followed by 0 or more digits.
    4. Optional type or exponent, but never both.
       - Type is one of ``[%!#]``. (`%` truncates fractional portion.)
       - Exponent is one of ``[dDeE]``, an optional minus sign, and
         optional digits. Note that the ``D`` and ``E`` are considered
         equivalent: BASIC always uses single precision if the
         significand will fit, otherwise double precision with truncation.
'''
MATCH_DIGITS_S = r'(-)?(\d*)(\.\d*)?([%!#]|[dDeE]-?\d*)?'
MATCH_DIGITS = None     # lazy initialisation

def match_number(p):
    ''' Parse basic syntax of number formats for all types of numbers
        into a 5-tuple. Since parsing can still fail after this, nothing
        is consumed but the number of characters to consume on success
        is returned.

        Note that this converted parsed elements to `str`, so the charset
        must have a conversion between input element digits and Unicode
        digits.

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

    #   XXX get rid of p.re_compile() and have p.re_match() compile
    #   and cache the `re.Pattern`
   #global MATCH_DIGITS
   #if MATCH_DIGITS is None:
   #    MATCH_DIGITS = p.re_compile(MATCH_DIGITS_S)

    m = p.re_match(MATCH_DIGITS_S)
    if m is None: return None

    neg = -1 if m.group(1) else 0
    i = m.group(2); f = m.group(3);
    if not p.strinput:
        i = ''.join(map(p.charset.trans, i))
    if (i == '') and (f is None):
        return None
    if f is not None and not p.strinput:
        f = ''.join(map(p.charset.trans, f))
    if f is not None: f = f[1:]
    #   XXX decode TE here if input is not str
    te = m.group(4)
    if not p.strinput and te is not None:
        #   XXX is this correct? Should Parser be doing this translation back?
        te = ''.join(map(p.charset.trans, te))
    if (te is not None) and (te not in ('%', '!', '#')):
        if len(te) == 1: te += '0'  # D/E alone indicates exponent of 0
        te = int(te[1:])
    #print('neg:', repr(neg), 'i:', repr(i), 'f:', repr(f), 'te:', repr(te))

    return (m.end(), neg, i, f, te)

def ampersand_literal(p):
    ''' Read and consume ``&Hnnnn``, ``&Onnnn`` and ``&Bnnnn`` integer
        literals and generate their tokenised version. Raises a
        `ParseError` saying "Overflow" if the number is ≥ 2^16.
    '''
    if p.string_in(['&H', '&h']):
        base = 16; p.generate(b'\x0C')
    elif p.string_in(['&O', '&o']):
        base = 8;  p.generate(b'\x0B')
    elif p.string_in(['&B', '&b']):
        base = 2
    else:
        return None

    digits = p.digits(base)
   #DEBUG('ampersand_literal digits:', repr(digits))
    if base == 2:
        #   Unlike the others, &B has no tokenised version; it's just ASCII.
        p.generate(b'&B')
        if digits is None:
            n = 0
        else:
            if p.strinput:
                p.generate(digits.encode('ASCII'))
            else:
                p.generate(digits)
            n = int(digits, 2)

    else:
        if digits is None:
            #   A prefix not followed by a valid digit assumes a value of 0.
            digits = '0'

        n = int(digits, base)
       #DEBUG('ampersand_literal:', base, digits, n, hex(n)) # XXX
        if n > 0xFFFF:
            p.error('Overflow')
        p.generate(pack('<H', n))

    p.commit()
    return n

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
        but is < 0 or > `TLines.MAXLIN_5`.
    '''
    #DEBUG('linenum() on {}'.format(repr(p.remain()[0:10])))
    p.start()

    neg = False
    if p.string('-'): neg = True

    ds = p.digits()
    if ds is None:
        if err is None: return None
        p.error('expected ' + err)

    #DEBUG('ds:', type(ds), repr(ds))
    if not isinstance(ds, str):
        ds = ''.join(map(p.charset.trans, ds))
    #DEBUG('ds:', type(ds), repr(ds))

    n = int(ds)
    if n > TLines.MAXLIN_5:
        #   We always raise an error here, even if not requested,
        #   because we have a line number but it's not usable.
        p.error('{} outside linenum range'.format(n))
    uint_16 = pack('<H', n)
    if gen:
        if neg: p.generate(NEGATIVE)
        p.generate(b'\x0E' + uint_16)
    p.commit()
    return -n if neg else n

def string_literal(p, err=None):
    ''' Consume a string literal starting with `"` and ending with the next
        `"` or end of input, generating its Parser.charset conversion and
        MSX-BASIC encoding. The intial and final quotes are not
        charset-converted.

        Return the consumed input string, including quotes.
    '''
    DQUOTE = '"'
    if not p.string(DQUOTE):
        if err is None: return None
        raise p.ParseError('{}: {}'.format(err, repr(p.peek())))
    p.generate(b'"')
    while True:
        if p.finished():
            return True
        if p.string(DQUOTE):
            p.generate(b'"')
            return True
        char(p)

def space(p, generate=True):
    ' Consume a single space, if present. '
    if p.peek() in (' ', ord(' ')):
        if generate: char(p)
        else:        p.consume()

def spaces(p, generate=True):
    ''' Consume zero or more space characters.

        If `generate` is `True` these will be generated into the output
        (using the usual Unicode to native translation), otherwise they
        will be silenty consumed.
    '''
    while p.peek() is not None:
        if p.string(' '):
            if generate: p.generate(msx_encode(p, ' '))
        else:
            break
        p.commit()

def chars(p):
    ' Do char() until end of input. '
    while not p.finished():
        char(p)

def char(p):
    #   XXX FIXME The parser knows the charset, but not which of the two
    #             encodings to use!
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
    c = i = p.consume(1)
    if p.strinput:
        i = msx_encode(p, c)
    p.generate(i)
    return c

def msx_encode(p, c):
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
    return encoded
