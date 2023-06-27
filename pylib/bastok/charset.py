''' Generic character set support.

    This supports setting up translations between Unicode and native
    character sets that have exactly 256 code points, 0x00-0xFF.

    This does not handle encoding such as MSX's encoding of code point 0x05
    as b'\x01\x45'. Encoding/decoding should be done by the system-specific
    parsing routines.

'''

class Charset:
    ''' A mapping between a native character set (`int` code points 0x00
        through 0xFF) and an arbitrary set of Unicode characters (`str`s of
        length 1).

        Note that this does _not_ handle encodings, which are at the
        level above character sets. For example, MSX-BASIC needs to represent
        all 256 code points in its character set _and_ 31 non-printing
        control characters in strings of 8-bit characters: to do this it
        encodes code points 0x00 through 0x1F as 0x01 followed by the code
        point number plus 0x40. Thus, code point 0x08 (年) is encoded as
        the sequence 0x01 0x48; the single-character sequence 0x08 encodes
        a backspace which, being a non-printing character, has no code
        point in the MSX character set.

        The same is true of Python: Python 3 strings (`str`) are sequences
        of Unicode code points (numbering over a hundred thousand). If you
        want the UTF-8 encoded version of these code points you must
        use an encoding routine such as ``str.encode(encoding='utf-8')``
        (which returns a `bytes`) or a _text_ file object such as returned
        by ``open(filename, mode='wt', encoding='utf-8')``.
    '''

    def __init__(self, description, *maps):
        ''' Create a Charset with human-readable description `description`,
            passing each map in `maps` to `setchars()` and then confirming
            that the charset maps all native codepoints 0x00 through 0xFF.
        '''
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
            of pairs (`int` native codepoint, `str` Unicode character).

            This quietly overwrites existing values in order to make it
            easy to create custom charsets by modifying the standard ones.
        '''
        for n, u in map:
            self._ncheck(n); self._ucheck(u)
           ##   When debugging you may uncomment this to help find duplicates.
           #if u in self._un:
           #    raise RuntimeError(
           #        "Dup char: 0x{:0X}→{} overriding 0x{:0X}→{}" \
           #        .format(ord(u), hex(n), ord(u), hex(self._un[u])))
            self._nu[n] = u
            self._un[u] = n

    def trans(self, n):
        ''' Given a native code point `n` (`int` from 0x00 through 0xFF),
            return the Unicode character (`str` of length 1) to which it is
            mapped.

            Note that this takes and returns _code points,_ not encoded
            characters. See this class' header comment for details.
        '''
        self._ncheck(n)
        return self._nu[n]

    def native(self, u):
        ''' Given a Unicode character `u` (`str` of length 1) return the
            native codeset point (`int` from 0x00 through 0xFF) to which it
            is mapped.

            Note that this takes and returns _code points,_ not encoded
            characters. See this class' header comment for details.
        '''
        self._ucheck(u)
        return self._un[u]

####################################################################
#   Generic charsets for special purposes

class Unimplemented:
    ''' An unimplemented character set. This is useful to document the
        names of character sets whose translation has not yet been
        implemented.
    '''
    def __init__(self, name, description):
        self.name = name
        self.description = description + ' (not yet implemented)'
    def unimpl(self):
        raise NotImplementedError("charset '{}' ".format(self.name))
    def trans(self, n):     self.unimpl()
    def native(self, u):    self.unimpl()

class UTCharset:
    ''' A Charset converter for use by unit tests.

        This maps native codes 0x00 through 0xFF to Unicode code points
        U+F000 through U+F0FF, which are codes in the private use area
        (U+E000 - U+F8FF).

        This intentionally uses only non-ASCII codes on the Unicode side;
        that helps ensure that the CUT is using `str` where it should be.
    '''

    def __init__(self, offset=0xF000):
        self.offset = offset

    def trans(self, n):
        assert n >= 0 and n < 0x100, hex(n)
        return chr(self.offset+n)

    def native(self, u):
        min, max = chr(self.offset), chr(self.offset + 0xFF)
        assert len(u) == 1 and u >= min and u <= max, repr(u)
        return ord(u) - self.offset


####################################################################
#   Utility functions

def chrsub(codechars, replacement):
    ''' Replace a code-character mapping in a list of such mappings.

        `codechars` is a sequence of (`int`,`str`) pairs, each a native
        code point and its associated Unicode character, and `replacement`
        a single pair to replace (at the same position) the pair in
        `codechars` with a matching code point. A new sequence with that
        code pont replaced is returned.

        A `LookupError` will be raised if the replacement code point
        is not found in `codechars`.

        This can be used to help build custom character set mappings
        provided to the `Charset` constructor.
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
