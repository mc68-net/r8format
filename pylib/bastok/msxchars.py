__all__ = [ 'Charset', 'CHARMAP' ]

####################################################################
#   Characters used for blank glyphs.
#
#   In all standard MSX charsets code 0x00 is a blank glyph, the same as
#   ASCII space, and some charsets have further blank glyphs. To properly
#   round-trip these we must use different Unicode characters for each
#   differently-coded blank.
#
#   The digraphs given below as `dg:XY` are from `RFC 1345`_. The ones
#   given as `sd:XY` are not standard digraphs, but are suggested ones you
#   may add to your editor. In Vim you can press Ctrl-K followed by X and Y
#   to enter a character using a digraph, and you may also define your own
#   digraphs matching `sd:XY` entries. See vim's `:help digraph` for more
#   information on this.
#
#   .. _RFC 1345: https://tools.ietf.org/html/rfc1345

#   Code 0x00. The association should be obvious.
#
C00 = '\u2205'  # ∅ EMPTY SET (dg:0/)

#   Japanese has a blank instead of the white triangle at 0x7F, but since
#   it does not have a white triangle elsewhere, we use it as the
#   placeholder character here. This might, however, be confusing; if it
#   proves to be so we should probably change it to `⠿` BRAILE PATTERN
#   DOTS-123456 (see below for more on this).
#
C7F = '\u25B3'  # △ WHITE UP-POINTING TRIANGLE (dg:uT)

#   We use BRAILLE PATTERN DOTS-nnn for other blank glyphs because these
#   are very obviously not from any standard MSX or Japanese character set
#   and are often part of standard modern character sets.
#
C90 = '\u280F'  # ⠏ DOTS-1234 (sd:b4)
CA0 = '\u2817'  # ⠗ DOTS-1235 (sd:b5)
CFE = '\u2827'  # ⠧ DOTS-1236 (sd:b6)

####################################################################

def chrsub(codechars, replacement):
    ''' Replace a code-character mapping in a list of such mappings.

        `codechars` is a sequence of (`int`,`str`) pairs, each a native
        code point and its associated Unicode character, and `replacement`
        a single pair to replace (at the same position) the pair in
        `codechars` with a matching code point. A new sequence with that
        code pont replaced is returned.

        A `LookupError` will be raised if the replacement code point
        is not found in `codechars`.
    '''
    replaced = False
    ret = []
    for mapping in codechars:
        if mapping[0] == replacement[0]:
            ret.append(replacement)
            replaced = True
        else:
            ret.append(mapping)
    if not replaced:
        raise LookupError('code point {} not replaced'.format(replacement))
    return tuple(ret)

####################################################################
#   ASCII characters
#
#   These are common to all MSX charsets. These codes include neither
#   control chars $00-$1F nor $7F (ASCII DEL), which is a glyph code that
#   varies amongst the MSX character sets.

C_ASCII = tuple([ (c, chr(c)) for c in range(0x20,0x7F) ])

assert len(C_ASCII) == 0x5F, hex(len(C_ASCII))

####################################################################
#   International charset
#
#   Some of this is the same as code page 437, the original IBM PC
#   character set. When in doubt, the character from that has been used.
#
#   0x10 and 0x1F are vertical+horizontal box drawing characters similar to
#   0x15 `┼`, except that they do not extend all the way to the edge of the
#   horizontal resp. vertical edges of the character cell. Unicode box
#   drawing has no equivalants to these, and I doubt that the legacy
#   charset versions are widely available in any commmon fonts, so here we
#   use a couple of obviously different Unicode characters to help avoid
#   confusion. If you do have fonts with these legacy characters, you can
#   redefine these with a custom character mapping.
#
VH_shortH = '\u256A'    # ╪ BOX DRAWINGS VERTICAL SINGLE AND HORIZONTAL DOUBLE
VH_shortV = '\u256B'    # ╫ BOX DRAWINGS VERTICAL DOUBLE AND HORIZONTAL SINGLE

LO_int = ''.join([C00,
        '☺☻♡♢♣♠∙◘○◙♂♀♪♫☼',
        VH_shortH, '┴┬┤├┼│─┌┐└┘╳╱╲', VH_shortV,
        ])

#   There's not complete agreement on what all the Code Page 437 characters
#   are; see the notes at https://en.wikipedia.org/wiki/Code_page_437 .
HI_int = ''.join([
        'ÇüéâäàåçêëèïîìÄÅ',     # row from CP 437
        'ÉæÆôöòûùÿÖÜ¢£¥₧ƒ',     # row from CP 437
        'áíóúñÑªº¿⌐¬½¼¡«»',     # row from CP 437
        'ÃãĨĩÕõŨũ__¾___¶§',     # XXX incomplete
        '________________',     # XXX incomplete
        '________________',     # XXX incomplete
        'αßΓπΣσµτΦΘΩδ∞φ∈∩',     # row from CP 437, possibly excepting 0xEE
        '≡±≥≤⌠⌡÷≈°∙·√ⁿ²■█',     # row from CP 437, mostly
        ])

assert len(LO_int) == 0x20, hex(len(LO_int))
assert len(HI_int) == 0x80, hex(len(HI_int))

C_INT = tuple(zip(range(0x00, 0x20), LO_int)) \
     + C_ASCII + ((0x7F,C7F),) \
     + tuple(zip(range(0x80, 0x100), HI_int)) \
     + ()

####################################################################
#   Japanese charset

LO_ja = ''.join([C00,
        '月火水木金土日年円時分秒百千万',
        'π┴┬┤├┼│─┌┐└┘╳大中小',
        ])
HI_ja = ''.join([
        '♠♡♣♢○●をぁぃぅぇぉゃゅょっ',
        C90, 'あいうえおかきくけこさしすせそ',
        CA0, '。「」、・ヲァィゥェォャュョッ',
        'ーアイウエオカキクケコサシスセソ',
        'タチツテトナニヌネノハヒフヘホマ',
        'ミムメモヤユヨラリルレロワン゛゜',
        'たちつてとなにぬねのはひふへほま',
        'みむめもやゆよらりるれろわん', CFE, '█',
        ])

assert len(LO_ja) == 0x20, hex(len(LO_ja))
assert len(HI_ja) == 0x80, hex(len(HI_ja))

C_JA = tuple(zip(range(0x00, 0x20), LO_ja)) \
     + chrsub(C_ASCII, (0x5C, '¥')) + ((0x7F,C7F),) \
     + tuple(zip(range(0x80, 0x100), HI_ja)) \
     + ()

####################################################################
#   Charset classes

class Charset:
    ''' A mapping between a native character set, encoded as single
        bytes from 0x00 through 0xFF, and an arbitrary set of
        Unicode characters (1-character `str`s).
    '''

    def __init__(self, description, *maps):
        self.description = description
        self._nu = {}   # native (int) to Unicode (str) map
        self._un = {}   # Unicode (str) to native (int) map
        for m in maps: self.setchars(m)
        nlen = len(self._nu); ulen = len(self._un)
        if not (nlen == ulen == 0x100):
            raise RuntimeError(
                'Incomplete Charset: n=0x{:02X} ({}) u=0x{:02X} ({}) chars'
                .format(nlen, nlen, ulen, ulen))

    def _ncheck(self, n):
        ' Raise error if `n` is not a valid native char code. '
        if n < 0 or n > 0xFF:
            raise ValueError('Bad native char code {:02X}'.format(n))

    def _ucheck(self, u):
        ' Raise error if `u` is not a single Unicode character. '
        if not isinstance(u, str):
            raise ValueError('Unicode char not a str: {}'.format(repr(u)))
        if len(u) != 1:
            raise ValueError('str not length 1: {}'.format(repr(u)))

    def setchars(self, map):
        ''' Set character mappings in this Charset. `map` is a collection
            of pairs of (native character code, 1-char (unicode) string).

            This quietly overwrites existing values in order to make it
            easy to create custom charsets by modifying the standard ones.
        '''
        for n, u in map:
            self._ncheck(n); self._ucheck(u)
            #   When debugging you may uncomment this to help find duplicates.
            #if u in self._un: raise RuntimeError('Dup ' + repr(u))
            self._nu[n] = u
            self._un[u] = n

    def uc(self, n):
        ''' Translate native code `n`, an `int` from 0x00 through 0xFF, to
            a single-character Unicode `str`. Note that codes 0x00 through
            0x1F are represented as [0x01, 0x40+`n`] in MSX BASIC.
        '''
        self._ncheck(n)
        return self._nu[n]

    def native(self, u):
        ''' Translate Unicode character `u`, a single-character `str`, to a
            `bytes` containing the MSX-BASIC encoding of that character.
            The result will be a single byte from 0x40 through 0xFF or two
            bytes, 0x01 followed by an "extended" character code from 0x40
            through 0x5F.
        '''
        self._ucheck(u)
        return bytes([self._un[u]])

class Unimplemented:
    def __init__(self, name, description):
        self.name = name
        self.description = description + ' (not yet implemented)'
    def unimpl(self):
        raise NotImplementedError("charset '{}' ".format(self.name))
    def uc(self, n):            self.unimpl()
    def native(self, u):        self.unimpl()

CHARMAP = {
    'int':  #Charset("International (North America/Europe), C_INT), # incomplete
            Unimplemented('int', 'International (North America/Europe)'),
    'ja':   Charset('Japanese (MSX2)', C_JA),
    'ja1':  Unimplemented('ja1', 'Japanese (MSX1, different hiragana)'),
    'ar':   Unimplemented('ar', 'Arabic'),
    'pt':   Unimplemented('pt', 'Portuguese (Brazil)'),
    'BR':   Unimplemented('BR', "alias for 'pt'"),
    'ru':   Unimplemented('ru', 'Russian'),
}
