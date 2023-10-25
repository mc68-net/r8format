from    struct  import unpack

#   Token values mostly from MSX2 Technical Handbook, table 2.20.
#   https://github.com/Konamiman/MSX2-Technical-Handbook/blob/master/md/Chapter2.md/#table-220--list-of-intermediate-codes

TOKENS = (
    (b':\xA1',      'ELSE',         ),
    (b':\x8F\xE6',  "'",            ),  # alternative form of REM
    (b'\x81',       'END',          ),
    (b'\x82',       'FOR',          ),
    (b'\x83',       'NEXT',         ),
    (b'\x84',       'DATA',         ),
    (b'\x85',       'INPUT',        ),
    (b'\x86',       'DIM',          ),
    (b'\x87',       'READ',         ),
    (b'\x88',       'LET',          ),
    (b'\x89',       'GOTO',         ),
    (b'\x8A',       'RUN',          ),
    (b'\x8B',       'IF',           ),
    (b'\x8C',       'RESTORE',      ),
    (b'\x8D',       'GOSUB',        ),
    (b'\x8E',       'RETURN',       ),
    (b'\x8F',       'REM',          ),
    (b'\x90',       'STOP',         ),
    (b'\x91',       'PRINT',        ),
    (b'\x92',       'CLEAR',        ),
    (b'\x93',       'LIST',         ),
    (b'\x94',       'NEW',          ),
    (b'\x95',       'ON',           ),
    (b'\x96',       'WAIT',         ),
    (b'\x97',       'DEF',          ),
    (b'\x98',       'POKE',         ),
    (b'\x99',       'CONT',         ),
    (b'\x9A',       'CSAVE',        ),
    (b'\x9B',       'CLOAD',        ),
    (b'\x9C',       'OUT',          ),
    (b'\x9D',       'LPRINT',       ),
    (b'\x9E',       'LLIST',        ),
    (b'\x9F',       'CLS',          ),
    (b'\xA0',       'WIDTH',        ),
    (b'\xA2',       'TRON',         ),
    (b'\xA3',       'TROFF',        ),
    (b'\xA4',       'SWAP',         ),
    (b'\xA5',       'ERASE',        ),
    (b'\xA6',       'ERROR',        ),
    (b'\xA7',       'RESUME',       ),
    (b'\xA8',       'DELETE',       ),
    (b'\xA9',       'AUTO',         ),
    (b'\xAA',       'RENUM',        ),
    (b'\xAB',       'DEFSTR',       ),
    (b'\xAC',       'DEFINT',       ),
    (b'\xAD',       'DEFSNG',       ),
    (b'\xAE',       'DEFDBL',       ),
    (b'\xAF',       'LINE',         ),
    (b'\xB0',       'OPEN',         ),
    (b'\xB1',       'FIELD',        ),
    (b'\xB2',       'GET',          ),
    (b'\xB3',       'PUT',          ),
    (b'\xB4',       'CLOSE',        ),
    (b'\xB5',       'LOAD',         ),
    (b'\xB6',       'MERGE',        ),
    (b'\xB7',       'FILES',        ),
    (b'\xB8',       'LSET',         ),
    (b'\xB9',       'RSET',         ),
    (b'\xBA',       'SAVE',         ),
    (b'\xBB',       'LFILES',       ),
    (b'\xBC',       'CIRCLE',       ),
    (b'\xBD',       'COLOR',        ),
    (b'\xBE',       'DRAW',         ),
    (b'\xBF',       'PAINT',        ),
    (b'\xC0',       'BEEP',         ),
    (b'\xC1',       'PLAY',         ),
    (b'\xC2',       'PSET',         ),
    (b'\xC3',       'PRESET',       ),
    (b'\xC4',       'SOUND',        ),
    (b'\xC5',       'SCREEN',       ),
    (b'\xC6',       'VPOKE',        ),
    (b'\xC7',       'SPRITE',       ),
    (b'\xC8',       'VDP',          ),
    (b'\xC9',       'BASE',         ),
    (b'\xCA',       'CALL',         ),
    (b'\xCB',       'TIME',         ),
    (b'\xCC',       'KEY',          ),
    (b'\xCD',       'MAX',          ),
    (b'\xCE',       'MOTOR',        ),
    (b'\xCF',       'BLOAD',        ),
    (b'\xD0',       'BSAVE',        ),
    (b'\xD1',       'DSKO$',        ),
    (b'\xD2',       'SET',          ),
    (b'\xD3',       'NAME',         ),
    (b'\xD4',       'KILL',         ),
    (b'\xD5',       'IPL',          ),
    (b'\xD6',       'COPY',         ),
    (b'\xD7',       'CMD',          ),
    (b'\xD8',       'LOCATE',       ),
    (b'\xD9',       'TO',           ),
    (b'\xDA',       'THEN',         ),
    (b'\xDB',       'TAB(',         ),
    (b'\xDC',       'STEP',         ),
    (b'\xDD',       'USR',          ),
    (b'\xDE',       'FN',           ),
    (b'\xDF',       'SPC(',         ),
    (b'\xE0',       'NOT',          ),
    (b'\xE1',       'ERL',          ),
    (b'\xE2',       'ERR',          ),
    (b'\xE3',       'STRING$',      ),
    (b'\xE4',       'USING',        ),
    (b'\xE5',       'INSTR',        ),
    (b'\xE7',       'VARPTR',       ),
    (b'\xE8',       'CSRLIN',       ),
    (b'\xE9',       'ATTR$',        ),
    (b'\xEA',       'DSKI$',        ),
    (b'\xEB',       'OFF',          ),
    (b'\xEC',       'INKEY$',       ),
    (b'\xED',       'POINT',        ),
    (b'\xEE',       '>',            ),
    (b'\xEF',       '=',            ),
    (b'\xF0',       '<',            ),
    (b'\xF1',       '+',            ),
    (b'\xF2',       '-',            ),
    (b'\xF3',       '*',            ),
    (b'\xF4',       '/',            ),
    (b'\xF5',       '^',            ),
    (b'\xF6',       'AND',          ),
    (b'\xF7',       'OR',           ),
    (b'\xF8',       'XOR',          ),
    (b'\xF9',       'EQV',          ),
    (b'\xFA',       'IMP',          ),
    (b'\xFB',       'MOD',          ),
    (b'\xFC',       '\\',           ),
    (b'\xFF\x81',   'LEFT$',        ),
    (b'\xFF\x82',   'RIGHT$',       ),
    (b'\xFF\x83',   'MID$',         ),
    (b'\xFF\x84',   'SGN',          ),
    (b'\xFF\x85',   'INT',          ),
    (b'\xFF\x86',   'ABS',          ),
    (b'\xFF\x87',   'SQR',          ),
    (b'\xFF\x88',   'RND',          ),
    (b'\xFF\x89',   'SIN',          ),
    (b'\xFF\x8A',   'LOG',          ),
    (b'\xFF\x8B',   'EXP',          ),
    (b'\xFF\x8C',   'COS',          ),
    (b'\xFF\x8D',   'TAN',          ),
    (b'\xFF\x8E',   'ATN',          ),
    (b'\xFF\x8F',   'FRE',          ),
    (b'\xFF\x90',   'INP',          ),
    (b'\xFF\x91',   'POS',          ),
    (b'\xFF\x92',   'LEN',          ),
    (b'\xFF\x93',   'STR$',         ),
    (b'\xFF\x94',   'VAL',          ),
    (b'\xFF\x95',   'ASC',          ),
    (b'\xFF\x96',   'CHR$',         ),
    (b'\xFF\x97',   'PEEK',         ),
    (b'\xFF\x98',   'VPEEK',        ),
    (b'\xFF\x99',   'SPACE$',       ),
    (b'\xFF\x9A',   'OCT$',         ),
    (b'\xFF\x9B',   'HEX$',         ),
    (b'\xFF\x9C',   'LPOS',         ),
    (b'\xFF\x9D',   'BIN$',         ),
    (b'\xFF\x9E',   'CINT',         ),
    (b'\xFF\x9F',   'CSNG',         ),
    (b'\xFF\xA0',   'CDBL',         ),
    (b'\xFF\xA1',   'FIX',          ),
    (b'\xFF\xA2',   'STICK',        ),
    (b'\xFF\xA3',   'STRIG',        ),
    (b'\xFF\xA4',   'PDL',          ),
    (b'\xFF\xA5',   'PAD',          ),
    (b'\xFF\xA6',   'DSKF',         ),
    (b'\xFF\xA7',   'FPOS',         ),
    (b'\xFF\xA8',   'CVI',          ),
    (b'\xFF\xA9',   'CVS',          ),
    (b'\xFF\xAA',   'CVD',          ),
    (b'\xFF\xAB',   'EOF',          ),
    (b'\xFF\xAC',   'LOC',          ),
    (b'\xFF\xAD',   'LOF',          ),
    (b'\xFF\xAE',   'MKI$',         ),
    (b'\xFF\xAF',   'MKS$',         ),
    (b'\xFF\xB0',   'MKD$',         ),

    #   Some keywords are "tokenized" with a series of tokens and ASCII
    #   letters. We make these separate entries so we can match them in
    #   full, ensuring we don't ever split the keywords with spaces or
    #   anything like that.
    (b'\xFF\x85' b'ER' b'\xFF\x94', 'INTERVAL', ),
)

#   Tokens sorted by decending length, so that we can walk through this
#   as a list of alternatives, ensuring that a word will match before
#   its prefix.
DETOKENS = sorted(TOKENS, key=lambda t: len(t[0]), reverse=True)

def tokbytes(s):
    ''' Return the bytes (1 or more) of the token for the given keyword `s`.
        The token must exist in the table or LookupError will be thrown.
    '''
    bytes_list = [ t for t, k in TOKENS if k == s ]
    if len(bytes_list) != 1:
        raise LookupError(
            'Internal token table error: {} has {} entries: {}' \
            .format(s, len(bytes_list), bytes_list))
    return bytes_list[0]

SPACE   = ord(' ')
DQUOTE  = ord('"')
COMMA   = ord(',')
COLON   = ord(':')
T_DATA  = tokbytes('DATA')[0]
T_REM   = tokbytes('REM')[0]
T_QREM1 = tokbytes("'")[1]      # tokens for the single-quote alternative
T_QREM2 = tokbytes("'")[2]      #   form of REM, without leading ':'
T_ELSE1 = tokbytes('ELSE')[1]   # without leading ':'
T_EQ    = tokbytes('=')[0]
MAX_LINENO = 65529

class Detokenizer:
    ''' A detokenizer for MSX-BASIC. Instantiate this with a tokenized
        line and call `detokenized()` for the detokenized result.
    '''

    ####################################################################
    #   Public API

    def __init__(self, charset, tline, lineno=None, *, expand=False):
        ''' Set up a detokenizer.
            * `charset` is the `Charset` to use for conversion. If `None`,
              charset conversion will not be done and instead `bytes`
              output in MSX-BASIC encoding will be generated.
            * `tline` is a `bytes` containing the tokenized line data, not
              including the line number or trailing 0x00.
            * `lineno`, if present, will prefix the detokenized line and be
              printed in any exceptions raised.
            * `expand` will add spacing to make the output more readable,
              including newlines before ``:``s.
        '''
        if charset is not None:
            assert callable(charset.trans)
        self.charset = charset
        self.tline = tline
        if lineno is None:
            self.lineno = None
        else:
            self.lineno = int(lineno)   # catch bad param early
        self.expand = expand
        self.reset()

    def detokenized(self):
        ''' Return the detokenized version of `tline`. This will return a
            `str` if a ``charset`` was given, or a `bytes` in MSX character
            set otherwise.
        '''
        if not self._output:
            self.parse_tline()
        return self.output()

    class TokenError(ValueError):
        ' Invalid input. '

    class ParseError(RuntimeError):
        ' Probably a bug in our parser. '

    def pstate(self):
        ''' Return a string with information about the current parser state.
            This can be used to debug the parser or badly tokenized BASIC.
        '''
        p = self.p
        consumed = self.tline[:p][-8:]
        next = self.tline[p:p+9]
        return 'lineno={} pos={} consumed=...{} next={}... output=...{}' \
            .format(self.lineno, p, consumed, next, self._output[-4:])

    ####################################################################
    #   The remaining parsing API is generally for internal use,
    #   but may be driven externally for testing or other purposes.
    ####################################################################

    ####################################################################
    #   Low-level output generation routines; these do not read input

    def output(self):
        ''' Return the current generated output as `str` if a ``charset``
            was given, or a `bytes` in MSX character set otherwise.
        '''
        if self.charset is None:
            empty = bytes()
        else:
            empty = str()
        return empty.join(self._output)

    def terror(self):
        ' Throw a tokenization error at the current position. '
        raise self.TokenError('Bad tokenized data: ' + self.pstate())

    def parseerror(self):
        ' Throw a parse error at the current position. '
        raise self.ParseError('Internal error: ' + self.pstate())

    def reset(self):
        ' Clear the output and reset the detokenization pointer to the start. '
        self._output = []
        self.p = 0              # current parse offset in input

    def genasc(self, a):
        ''' Append an ASCII character or characters to the output.

            `a` must be either an `int` from 0x00 to 0x7F, which will
            generate a single ASCII character corresponding to that code,
            or an `str` that contains only ASCII characters.
        '''
        if isinstance(a, int):
            if a < 0 or a > 0x7F:
                raise ValueError('Invalid ASCII code: ' + hex(a))
            if self.charset is None:
                self._output.append(bytes([a]))
            else:
                self._output.append(chr(a))
        else:
            b = bytes(a, 'ASCII')       # raise error if not ASCII
            if self.charset is None:
                self._output.append(b)
            else:
                self._output.append(a)

    def generate(self, c):
        ''' Append object `c` to the output.

            This must be of the correct type: (Unicode) `str` if we
            are doing charset conversion, or `bytes` if we are not.
        '''
        self._output.append(c)

    def expandsp(self):
        ''' If we are in expand mode, generate a space, unless the previous
            or next character is already a space, in which case it's not
            necessary.
        '''
        if not self.expand:             return
        if self._output[-1][-1] == ' ': return  # already printed a space
        if self.peek() == ord(' '):     return  # next char will print a space
        self.genasc(' ')

    def expandnl(self):
        '''' If we are in expand mode, generate a (Unix) newline and indent
            for the continuation line.

            We do not currently support multi-line output in non-Unix
            format since it's expected this will be used only for files
            stored in revision control, where one wants to keep them in a
            single format regardless of platform.
        '''
        if self.expand:
            self.genasc('\n    ')

    ####################################################################
    #   Parsing routines

    def parse_tline(self):
        ''' Generate the detokenized version of the tokenized line,
            prefixed by `lineno` if that was provided.
        '''
        #   Allow use of these without `self.` prefix.
        def genasc(s):      return self.genasc(s)
        def terror():       return self.terror()
        def asc(*args):     return self.asc(*args)
        def int16():        return self.int16()

        self.reset()

        if self.lineno is not None:
            self.genasc('{:{width}}'.format(self.lineno,
               width=5 if self.expand else 0))
            self.genasc(' ')

        while True:
            b = self.peek()
            if b is None:
                break
            elif b <= 0x0A:
                #   MSX-BASIC does not have native chars < 0x20;
                #   those code points are encoded as b'\x01\xNN` sequences.
                terror()
            elif b == 0x0B:
                asc(b, '&O')
                genasc(oct(int16())[2:].upper())
            elif b == 0x0C:
                asc(b, '&H')
                genasc(hex(int16())[2:].upper())
            elif b == 0x0D:
                #   Address in BASIC text area of destination line.
                #   This conversion is done at/during (?) RUN.
                raise RuntimeError('XXX write me: line address')
            elif b == 0x0E:
                asc(b, '')
                i = int16()
                if i > MAX_LINENO: terror()
                genasc(str(i))
            elif b == 0x0F:            # int 10-255 follows token
                asc(b, '')
                i = self.byte()
                if i < 10: terror()
                genasc(str(i))
            elif b <= 0x1A:            # single-digit int
                asc(b, str(b - 0x11))
            elif b == 0x1B:            # unused
                terror()
            elif b == 0x1C:            # two-byte little-endian int 256-32767
                asc(b, '')
                i = int16()
                if i < 256 or i > 32767: terror()
                genasc(str(i))
            elif b == 0x1D:
                asc(b, '')
                self.real(4)
            elif b == 0x1E:
                terror()
            elif b == 0x1F:
                asc(b, '')
                self.real(8)
            elif b < DQUOTE:
                asc(b)
            #   $26 $42: binary numbers use ASCII `&B` followed by digits.
            elif b == DQUOTE:
                asc(b)
                self.quoted()
            elif b == COLON:
                self.colon()
            elif b <= 0x7F:
                asc(b)
            elif b == T_DATA:
                asc(b, 'DATA')
                self.expandsp()
                self.data()
            elif b == T_REM:
                asc(b, 'REM')
                self.remcontents()
                #   No expandsp() here because we support tricks like
                #   `10 REMARKABLE PROGRAM`
            elif self.token():
                pass
            else:
                parseerror()

        return self.output()

    def match(self, bs):
        ' Are the next bytes in the input are `bs`? '
        return self.tline[self.p:].startswith(bs)

    def peek(self):
        ''' Without consuming it, return the next byte in the input
            or `None` if no more input is available.
        '''
        if self.p >= len(self.tline):
            return None
        return self.tline[self.p]

    def byte(self, b=None):
        ''' Consume the next byte in the input and return it as an `int`.
            or `None` if no more input is available. No output is generated.

            If `b` is not `None`, the byte must have `int` value `b`.
        '''
        i = self.peek()
        if b is not None and i != b:
            self.parseerror()
        self.p += 1
        return i

    def asc(self, c=None, a=None):
        ''' Consume an ASCII character and generate output.

            If an `int` `c` is specified, the next byte must have value `c`
            or a `ParseError` will be raised.

            If `a` is not `None`, that `str` (which must be ASCII) will be
            generated, otherwise the consumed byte, which must be an
            ASCII character, will be generated.
        '''
        b = self.byte()
        if c is not None and c != b:
            self.parseerror()
        if a is None:
            a = b
        self.genasc(a)

    def consume(self, bs):
        ''' Consume from the input the bytes in `bs`.
            Raise a ParseError if the input does not match.
        '''
        for b in bs: self.byte(b)

    def remcontents(self):
        ''' Consume the remainder of tline and generate its
            charset-converted contents.
        '''
        while self.peek() is not None:
            self.char()

    def colon(self):
        ''' Colon has some special cases when followed by a particular
            tokenization.
        '''
        b = self.byte()
        if b != COLON: self.terror()
        if self.peek() == T_ELSE1:
            #   ELSE is always encoded as colon followed by the ELSE token
            self.byte()
            self.expandsp(); self.genasc('ELSE'); self.expandsp()
        elif self.peek() == T_QREM1:
            #   May be single-quote alternative to REM
            self.byte();    # regular REM token
            if self.peek() == T_QREM2:
                self.byte(T_QREM2)
                self.genasc("'")
            else:
                self.expandnl()
                self.genasc(':')
                self.expandsp()
                self.genasc('REM')
                #   No expandsp() here because we support tricks like
                #   `10 REMARKABLE PROGRAM`
            self.remcontents()
        else:
            #   It's just a colon.
            self.expandnl(); self.genasc(b); self.expandsp()

    def int16(self):
        ''' Consume two bytes and return them as an unsigned `int`. '''
        i = unpack('<H', self.tline[self.p:self.p+2])[0]
        self.p += 2
        return i

    def bcdstr(self, n):
        ''' Given an unsigned byte value ($00-$FF), convert it to a `string`
            of two decimal digits.
        '''
        lo = n & 0x0F
        hi = (n & 0xF0) >> 4
        if hi > 9 or lo > 9:
            raise ValueError('Bad BCD byte: {:02X}'.format(n))
        return str(hi) + str(lo)

    def real(self, blen):
        ''' Consume `blen` bytes, convert them to a real number and
            generate it as output. `blen` must be 4 for single-precision or
            8 for double-precision. The first byte is be the sign (bit 7)
            and biased exponent (bits 0-6); the remaining bytes are pairs
            of BCD digits.

            Negative constants always store the sign as a ``-`` token ahead
            of a positive constant, so this will raise an error if the sign
            bit in the constant itself is negative.

            Following MSX-BASIC, we print just a significand with a trailing
            ``!`` (single-precision) or ``#`` (double-precision) if the
            exponent is between -2 and +13 (as seen by the user), otherwise
            we print in exponent form without a trailing type character.
            (MSX-BASIC does not allow a trailing type character after an
            exponent.)

            When encoding an nEm format, MS-BASIC chooses single or double
            precision based on the number of sig digs in the significand:
            if it's ≤6 single precision is used; otherwise double precision
            is used. However, with nDm format, MS-BASIC always encodes as
            double precision.

            Unlike MS-BASIC, for an encoded double in exponent form we
            always produce nDm, whereas MS-BASIC uses nEm for ≤6 sig digs
            in the significand. We do this so that we properly round-trip
            tokenised → ASCII → tokenised; MS-BASIC doesn't do this.
            This also helps with readability for humans.
        '''
        bs = self.tline[self.p:self.p+blen]
        self.p += blen

        sign = bs[0] & 0x80
        if sign:
            raise TokenError('tokenized single prec may not be negative')
        if blen == 4:
            precchar = '!'
            expchar  = 'E'
        elif blen == 8:
            precchar = '#'
            expchar  = 'D'
        else:
            raise Exception('Internal error: len {} != 4 or 8'.format(bs))

        #   Special case: all zeros is a zero value.
        if bs == bytes(blen):
            self.genasc('0' + precchar)
            return
        if bs[0] == 0x00:
            #   This form causes the interpreter to wedge when loading the file.
            raise TokenError('zero exponent with non-zero significand')

        #     The exponent is biased by 0x40, so 0x40 is an exponent of 0
        #   with the decimal point in front of all digits of the significand.
        #   In other words, exponent 0x40 is 0.nnnnnn × 10⁰.
        #     But note that in printed form, significand is multiplied by ten,
        #   putting one digit before the decimal point, which requires
        #   reducing the exponent by 1.
        exponent = (bs[0] & 0x7F) - 0x40
        significand = ''.join([self.bcdstr(b) for b in bs[1:]])
        sigdigs = len(significand)
       #print('exp', exponent, 'significand', significand, 'sigdigs', sigdigs)

        #   We must not use Python's floating point here because, being binary
        #   instead of BCD, it will occasionally round differently.
        if exponent > 14 or exponent <= -2:
            #   Exponent form with decimal point shifted one place to the right
            #   for a "human-normalized" significand.
            fraction = significand[1:].rstrip('0')
            if fraction: fraction = '.' + fraction
            self.genasc( '{}{}{}{:+d}'.format(
                significand[0], fraction, expchar, exponent-1))
        elif exponent == -1:
            self.genasc('.0' + significand.rstrip('0') + precchar)
        elif exponent == 0:
            self.genasc('.' + significand.rstrip('0') + precchar)
        elif exponent <= sigdigs:
            #   We may have a decimal fractional part.
            v = significand[0:exponent] + '.' + significand[exponent:]
            self.genasc(v.rstrip('0').rstrip('.') + precchar)
        else:
            self.genasc(str(int(significand) * 10**(exponent-6)) + precchar)

    def char(self):
        ''' If we have a charset, consume a native-encoded char from the
            input and generate it to the output after doing charset
            conversion on it. This will consume one or two bytes, depending
            on if the first byte is 0x01 indicating an "extended" character
            code. Illegal encoding sequences (control characters and
            bad 0x01 0xNN sequences) will raise an exception.

            If we do not have a charset, simply pass the bytes through with
            no checks, i.e., leave them in MSX encoding or whatever someone
            managed to stick in the program.

            This should be used only for strings, not program text.
        '''
        c = self.byte()
        if self.charset is None:
            self.generate(bytes([c]))
        else:
            if c == 0x01:                   # "extended" char code
                c = self.byte()
                if c is None:               self.terror()
                if c < 0x40 or c > 0x5F:    self.terror()
                self.generate(self.charset.trans(c-0x40))
            elif c < 0x20 or c == 0x7F:     # control char
                #   MSX-BASIC should never allow entry of strings with
                #   control characters.
                self.terror()
            else:                           # one-byte char code
                self.generate(self.charset.trans(c))

    def quoted(self):
        ''' Consume and generate a quoted string, including the trailing
            quote if present, but not including the leading quote, which
            is assumed to have been consumed and generated already.
        '''
        while True:
            c = self.peek()
            if c is None:                       # EOL ends quoted string
                return
            elif c == DQUOTE:                   # quote ends quoted string
                self.genasc(self.byte())      # and is not charset-decoded
                return
            else:
                self.char()

    def data(self):
        ''' Consume and generate bytes as a ``DATA`` statement argument.
            If the ``DATA`` statement is terminated by a colon, that will
            be consumed and generated as well.

            Unquoted spaces leading an argument, quotes and a trailing
            (unquoted) colon will be generated as ASCII codes; all the
            remainder will use charset translation.

            Though how exactly quotes are dealt with in DATA statements is
            complex (e.g., a quote *after* another char in a field is a
            literal, not quoting a string) it appears we can ignore this at
            the tokenization level and merely ignore ``:`` chars that are
            in a pair of quotes, otherwise terminating on a ``:`` or EOL.

            This does mean that quotes are always literal, never charset-
            converted, which may cause issues in certain programs, but it's
            not clear at the moment exactly how those programs would be
            written.
        '''
        leading = True
        while True:
            b = self.peek()
            if b is None:
                return  # EOL
            elif leading and b == SPACE:
                self.genasc(self.byte())
            elif b == DQUOTE:
                leading = False
                self.genasc(self.byte())
                self.quoted()
            elif b == COMMA:
                leading = True
                self.genasc(self.byte())
                if self.peek() != SPACE: self.expandsp()
            elif b == COLON:
                self.colon()
                return
            else:
                leading = False
                self.char()

    #   Tokens that are preceeded by a space in expand mode.
    PRESPACE_KEYWORDS = [ 'THEN', 'TO', 'STEP', 'AND', 'OR', 'XOR', ]

    def token(self):
        ''' If the next input is a token, consume it, generate the
            ASCII text for it (with expansion if we're expanding)
            and return `True`. Otherwise return `False`.
        '''
        for t, s in DETOKENS:
            if not self.match(t):
                continue
            self.consume(t)
            if s in self.PRESPACE_KEYWORDS: self.expandsp()
            self.genasc(s)
            next = self.peek()
            if len(s) > 1 and next not in [ None, COLON, ord('('), T_EQ, ]:
                self.expandsp()
            return True
        return False
