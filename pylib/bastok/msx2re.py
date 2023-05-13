from    bastok.tlines  import TLines
from    bastok.parser  import *
from    bastok.msx2  import TOKENS

ENCTOKENS = toksort(TOKENS, 1, 0)

def tokenize(charmap, lines, txttab=0x8001):
    ''' Tokenise a sequence of lines of BASIC code, returning them in
        a `TLines` object with a start address of `txttab`.
    '''
    tl = TLines(txttab)
    for l in lines:
        #   XXX check for duplicate line no?
        lineno, tokens = tokline(charmap, l)
        tl.setline(lineno, tokens)
    return tl

def tokline(charmap, line):
    ''' Tokenize a line of BASIC. Return an `(int, bytes)` tuple with
        the line number and tokenized line data or raise a `ParseError`
        if parsing fails.
    '''
    #   Possibly we want to change this API so that we can tokenize line
    #   fragments that do not start with a line number.
    p = PState(line, charmap)
    lineno = uint16(p, gen=False, err='line number')
    spaces(p, False)
    while not p.finished():
        #   Start by checking for a token, since any string matching a
        #   token takes priority over anything else.
        t = toktrans(p, ENCTOKENS)
        if t is not None:
            #   Only a few tokens have an argument that needs special parsing.
            #   These consume and generate the remainder of the line.
            if t == 'REM':  chars(p)
            if t == "'":    chars(p)
            if t == 'DATA': chars(p)    # XXX no space compression yet!
            if t == 'GOTO': spaces(p); uint16(p, err='line number after GOTO')
            continue
        if string_literal(p, err=None) is not None: continue
        byte(p, genf=lambda c: bytes([ord(c)]))

    return (lineno, p.output())

class EncodingError(ValueError): pass

def data(p):
    p.error('XXX Write DATA parser!')

def string_literal(p, err='unexpected input'):
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
