from    struct  import unpack

#   Token values mostly from MSX2 Technical Handbook, table 2.20.
#   https://github.com/Konamiman/MSX2-Technical-Handbook/blob/master/md/Chapter2.md/#table-220--list-of-intermediate-codes

TOKENS = (
    (b'\x3A\xA1',   'ELSE',         ),
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
)

TOKTAB = dict(TOKENS)

def toklastbyte(s):
    ' Return the last token byte of tokenized keyword `s`. '
    return [ t for t, k in TOKENS if k == s ][0][-1]

SPACE   = ord(' ')
DQUOTE  = ord('"')
COMMA   = ord(',')
COLON   = ord(':')
T_DATA  = toklastbyte('DATA')
T_REM   = toklastbyte('REM')
T_ELSE1 = toklastbyte('ELSE')   # without leading ':'
MAX_LINENO = 65529

class Detokenizer:
    ''' A detokenizer for MSX-BASIC. Instantiate this with a tokenized
        line and call `detokenize()` for the detokenized result.
    '''

    def __init__(self, charset, tline, lineno=None):
        ''' `charset` is the `Charset` to use for conversion. `tline` is a
            `bytes` containing the tokenized line data, not including the
            line number or trailing 0x00. `lineno`, if present, will prefix
            the detokenized line and be printed in any exceptions raised.
        '''
        assert callable(charset.uc)
        self.charset = charset
        self.tline = tline
        self.lineno = lineno
        self.reset()

    class TokenError(ValueError):
        pass

    def terror(self, offset=0):
        ' Throw a tokenization error at the current position. '
        raise self.TokenError('Bad tokenized data: ' + self.pstate())

    def output(self, s):
        ' Append `str` `s` to the output. '
        self._output.append(s)

    def reset(self):
        ' Clear the output and reset the detokenization pointer to the start. '
        self._output = [];
        self.p = 0              # current parse offset in input

    def pstate(self):
        ''' Return a string with information about the current parser state.
            This can be used to debug the parser or badly tokenized BASIC.
        '''
        p = self.p
        consumed = self.tline[:p][-8:]
        next = self.tline[p:p+9]
        return 'lineno={} pos={} consumed=...{} next={}... output=...{}' \
            .format(self.lineno, p, consumed, next, self._output[-4:])

    def detokenize(self):
        ''' Return a `str` containing the detokenized version of the
            tokenized line, prefixed by `lineno` if that was provided.
        '''
        #   Allow use of these without `self.` prefix.
        def output(s):      return self.output(s)
        def terror():       return self.terror()
        def nchar(*args):   return self.nchar(*args)
        def int16():        return self.int16()

        self.reset()
        while True:
            b = self.peek()
            if b is None:
                break
            elif b <= 0x0A:
                #   MSX-BASIC does not have native chars < 0x20;
                #   those code points are encoded as b'\x01\xNN` sequences.
                terror()
            elif b == 0x0B:
                nchar(b, '&O')
                output(oct(int16())[2:].upper())
            elif b == 0x0C:
                nchar(b, '&H')
                output(hex(int16())[2:].upper())
            elif b == 0x0D:
                raise RuntimeError('XXX write me: line address')
            elif b == 0x0E:
                nchar(b, '')
                i = int16()
                if i > MAX_LINENO: terror()
                output(str(i))
            elif b == 0x0F:            # int 10-255 follows token
                nchar(b, '')
                i = self.byte()
                if i < 10: terror()
                output(str(i))
            elif b <= 0x1A:            # single-digit int
                nchar(b, str(b - 0x11))
            elif b == 0x1B:            # unused
                terror()
            elif b == 0x1C:            # two-byte little-endian int 256-32767
                nchar(b, '')
                i = int16()
                if i < 256 or i > 32767: terror()
                output(str(i))
            elif b == 0x1D:
                nchar(b, '')
                self.real(4)
            elif b == 0x1E:
                terror()
            elif b == 0x1F:
                nchar(b, '')
                self.real(8)
            elif b < DQUOTE:
                nchar(b)
            elif b == DQUOTE:
                nchar(b)
                self.quoted()
            elif b == COLON and self.peek1() == T_ELSE1:
                #   ELSE is a special case; it's always encoded as colon
                #   followed by the ELSE token
                self.nchar(COLON, '')
                self.nchar(T_ELSE1, 'ELSE')
            elif b <= 0x7F:
                nchar(b)
            elif b == T_DATA:
                nchar(b, 'DATA')
                self.data()
            elif b == T_REM:
                nchar(b, 'REM')
                #   Consume the remainder of tline and output its
                #   charset-converted contents.
                while self.peek() is not None:
                    self.char()
            else:
                self.keyword()

        ret = ''.join(self._output)
        if self.lineno:
            ret = str(self.lineno) + ' ' + ret
        return ret

    def peek(self):
        ''' Without consuming it, return the next byte in the input
            or `None` if no more input is available.
        '''
        if self.p >= len(self.tline):
            return None
        return self.tline[self.p]

    def peek1(self):
        ''' Without consuming anything, return the byte *after* the
            next byte of input, or `None` input ends before that.
        '''
        if self.p + 1 >= len(self.tline):
            return None
        return self.tline[self.p + 1]

    def byte(self):
        ''' Consume the next byte in the input and return it as an `int`.
            or `None` if no more input is available. No output is generated.
        '''
        b = self.peek()
        self.p += 1
        return b

    def nchar(self, c=None, output=None):
        ''' Consume char with code `c` (an `int`) or any char if `c` is
            `None`. Output `output` if not `None`, otherwise output the
            native char read.
        '''
        b = self.byte()
        if c is not None and c != b:
            self.terror()
        if output is not None:
            self.output(output)
        else:
            self.output(chr(b))

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
        ''' Consume `blen` bytes, convert them to a real number and append
            it to the output. `blen` must be 4 for single-precision or 8
            for double-precision. The first byte is be the sign (bit 7) and
            biased exponent (bits 0-6); the remaining bytes are pairs of
            BCD digits.

            Negative constants always store the sign as a ``-`` token ahead
            of a positive constant, so this will raise an error if the sign
            bit in the constant itself is negative.

            Following MSX-BASIC, we print just a mantissa with a trailing
            ``!`` (single-precision) or ``#`` (double-precision) if the
            exponent is between -2 and +13 (as seen by the user), otherwise
            we print in exponent form without a trailing type character.
            (MSX-BASIC does not allow a trailing type character after an
            exponent.)

            XXX When tokenizing, it seems that MSX BASIC chooses single or
            double precision based on the number of digits in the mantissa.
        '''
        bs = self.tline[self.p:self.p+blen]
        self.p += blen

        sign = bs[0] & 0x80
        if sign:
            raise TokenError('tokenized single prec may not be negative')
        if blen == 4:
            precchar = '!'
        elif blen == 8:
            precchar = '#'
        else:
            raise Exception('Internal error: len {} != 4 or 8'.format(bs))

        #   Special case: all zeros is a zero value.
        if bs == bytes(blen):
            self.output('0' + precchar)
            return
        if bs[0] == 0x00:
            #   This form causes the interpreter to wedge when loading the file.
            raise TokenError('zero exponent with non-zero mantissa')

        #     The exponent is biased by 0x40, so 0x40 is an exponent of 0
        #   with the decimal point in front of all digits of the mantissa.
        #   In other words, exponent 0x40 is 0.nnnnnn × 10⁰.
        #     But note that in printed form, mantissa is multiplied by ten,
        #   putting one digit before the decimal point, which requires
        #   reducing the exponent by 1.
        exponent = (bs[0] & 0x7F) - 0x40
        mantissa = ''.join([self.bcdstr(b) for b in bs[1:]])
        sigdigs = len(mantissa)
       #print('exp', exponent, 'mantissa', mantissa, 'sigdigs', sigdigs) # XXX

        #   We must not use Python's floating point here because, being binary
        #   instead of BCD, it will occasionally round differently.
        if exponent > 14 or exponent <= -2:
            #   Exponent form with decimal point shifted one place to the right
            #   for a "human-normalized" mantissa.
            fraction = mantissa[1:].rstrip('0')
            if fraction: fraction = '.' + fraction
            self.output('{}{}E{:+d}'.format(mantissa[0], fraction, exponent-1))
        elif exponent == -1:
            self.output('.0' + mantissa.rstrip('0') + precchar)
        elif exponent == 0:
            self.output('.' + mantissa.rstrip('0') + precchar)
        elif exponent <= sigdigs:
            #   We may have a decimal fractional part.
            v = mantissa[0:exponent] + '.' + mantissa[exponent:]
            self.output(v.rstrip('0').rstrip('.') + precchar)
        else:
            self.output(str(int(mantissa) * 10**(exponent-6)) + precchar)

    def char(self):
        ''' Consume a native-encoded char from the input, convert it to
            Unicode via the current converter, and append it to the output.
            This will consume one or two bytes, depending on if the first
            byte is 0x01 indicating an "extended" character code.

            This should be used only for strings, not program text.
        '''
        c = self.byte()
        if c != 0x01 and c < 0x20:  # BASIC should never tokenize these codes
            self.terror()
        elif c != 0x01:             # standard char code
            self.output(self.charset.uc(c))
        else:                       # "extended" char code
            c = self.byte()
            if c is None:               self.terror()
            if c < 0x40 or c > 0x5F:    self.terror()
            self.output(self.charset.uc(c-0x40))

    def quoted(self):
        ''' Consume and output a quoted string, including the trailing
            quote if present, but not including the leading quote, which
            is assumed to have been consumed and output already.
        '''
        while True:
            c = self.peek()
            if c is None:                       # EOL ends quoted string
                return
            elif c == DQUOTE:                   # quote ends quoted string
                self.output(chr(self.byte()))   # and is not charset-decoded
                return
            else:
                self.char()

    def data(self):
        ''' Consume and output bytes as a ``DATA`` statement argument.
            If the ``DATA`` statement is terminated by a colon, that will
            be consumed and output as well.

            Unquoted spaces leading an argument, quotes and a trailing
            (unquoted) colon will be output as ASCII codes; all the
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
                self.output(chr(self.byte()))
            elif b == DQUOTE:
                leading = False
                self.output(chr(self.byte()))
                self.quoted()
            elif b == COMMA:
                leading = True
                self.output(chr(self.byte()))
            elif b == COLON:
                self.output(chr(self.byte()))
                return
            else:
                leading = False
                self.char()

    def keyword(self):
        ''' Consume one or two bytes of tokenized keyword and output
            the keyword.
        '''
        b = self.byte()
        if b == 0xFF:
            kw = TOKTAB.get(bytes([b, self.byte()]))
        else:
            kw = TOKTAB.get(bytes([b]))
        if kw is None:
            self.terror()
        self.output(kw)
