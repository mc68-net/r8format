from    bastok.tlines  import TLines
from    bastok.parser  import *
from    bastok.msx2  import TOKENS

ENCTOKENS = toksort(TOKENS, 1, 0)

def tokline(charmap, line):
    ''' Tokenize a line of BASIC. Return an `(int, bytes)` tuple with
        the line number and tokenized line data or raise a `ParseError`
        if parsing fails.
    '''
    #   Possibly we want to change this API so that we can tokenize line
    #   fragments that do not start with a line number.
    p = PState(line, charmap)
    lineno = decimal(p, err='line number')
    spaces(p)
    while not p.finished():
        t = toktrans(p, ENCTOKENS)
        if t is not None:
            #   Only a few tokens have an argument that needs special parsing.
            if t == 'REM': chars(p) # consume/generate remainder of line
            continue

        #   XXX translate here
        byte(p, genf=lambda c: bytes([ord(c)]))

    return (lineno, p.output())

def tokenize(charmap, lines):
    tl = TLines(0x8001)
    for l in lines:
        #   XXX check for duplicate line no?
        lineno, tokens = tokline(charmap, l)
        tl.setline(lineno, tokens)
    return tl

class EncodingError(ValueError): pass

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

    n = p.charset.native(c)
    if n == 0x7F:
        raise EncodingError('cannot encode char 0x7F')
    if n < 0x20:
        encoded = bytes([0x01, n+0x40])
    else:
        encoded = bytes([n])
    p.olist.append(encoded)
    return c

def chars(p):
    ' Do char() until EOF. '
    while char(p, err=None): pass
