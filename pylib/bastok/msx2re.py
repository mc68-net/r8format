from    bastok.tlines  import TLines
from    bastok.parser  import *
from    bastok.msx2  import TOKENS

ENCTOKENS = sorted([ (kw,tok) for tok,kw in TOKENS ],
                   key = lambda t: len(t[0]),
                   reverse = True)

def tokline(charmap, line):
    ''' Tokenize a line of BASIC. Return an `(int, bytes)` tuple with
        the line number and tokenized line data or raise a `ParseError`
        if parsing fails.
    '''
    #   Possibly we want to change this API so that we can tokenize line
    #   fragments that do not start with a line number.
    p = PState(line)
    lineno = decimal(p, err='line number')
    spaces(p)
    while not p.finished():
        if toktrans(p, ENCTOKENS) is not None:
            continue
        else:
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
