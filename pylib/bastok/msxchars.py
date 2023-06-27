from    bastok.charset  import *

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
        '☺☻♡♢♣♠•◘○◙♂♀♪♫☼',
        VH_shortH, '┴┬┤├┼│─┌┐└┘╳╱╲', VH_shortV,
        ])

#   There's not complete agreement on what all the Code Page 437 characters
#   are; see the notes at https://en.wikipedia.org/wiki/Code_page_437 .
HI_int = ''.join([
        'ÇüéâäàåçêëèïîìÄÅ',     # 8x row from CP 437
        'ÉæÆôöòûùÿÖÜ¢£¥₧ƒ',     # 9x row from CP 437
        'áíóúñÑªº¿⌐¬½¼¡«»',     # Ax row from CP 437
        'ÃãĨĩÕõŨũĲĳ¾∽◇‰¶§',     # Bx XXX incomplete
        '▂▚▆🮂▬🮅▎▞▊🮇🮊🮙🮘🭭🭯🭬',     # Cx from Wikipedia "MSX Character Set"
        '🭮🮚🮛▘▗▝▖🮖Δ‡ω█▄▌▐▀',     # Dx from Wikipedia "MSX Character Set"
        'αßΓπΣσµτΦΘΩδ∞φ∈∩',     # Ex row from CP 437, possibly excepting 0xEE
        '≡±≥≤⌠⌡÷≈°∙·√ⁿ²■▒',     # Fx row from CP 437, mostly
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
#   Dictionary of all standard charset/Unicode mappings

CHARMAP = {
    'int':  Charset('International (North America/Europe)', C_INT),
    'ja':   Charset('Japanese (MSX2)', C_JA),
    'ja1':  Unimplemented('ja1', 'Japanese (MSX1, different hiragana)'),
    'ar':   Unimplemented('ar', 'Arabic'),
    'pt':   Unimplemented('pt', 'Portuguese (Brazil)'),
    'BR':   Unimplemented('BR', "alias for 'pt'"),
    'ru':   Unimplemented('ru', 'Russian'),
}
