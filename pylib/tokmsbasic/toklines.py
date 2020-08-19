import  struct

class TokLines:
    ''' A sequence of tokenized lines. The data for each line is typically
        tokenized BASIC program text, but may be any string without 0x00
        bytes in it; this class handles only the line numbers and offsets.

        Symbol names such as `txttab` are taken from Microsoft or other
        documentation or source code, where possible.

        Attributes:
        - `lines`: A dictionary mapping `int` line number to the line data
           (without the terminating 0 byte).
        - `orig_text`: The original (pre-parse) text data this instance was
          instantiated with, if any (otherwise `None`). This should be the
          same as the result of `text()` if the original text was valid,
          `txttab` has not been changed from the value discovered by the
          parse, and no lines have been added, deleted or changed.
        - `bad_offsets`: A `list` of bad offset values from the last
          `parsetext()` run.

        Issues:
        - This currently assumes little-endian format, which is fine for
          8080 or 6502, but not for 6800.
        - `parsetext()` assumes that an initial 0xFF byte in the data is
          a file type byte from a disk save file. This could also be the
          start of a 250 byte line, but I don't think that any versions of
          MS-BASIC allow a line that long.
        - `maxlin` defaults to 65529, which is correct for MSX-BASIC and
          GW-BASIC, but not for early 6502 BASIC (63999).
    '''

    NEW_MAXLIN = 65529      # MSX-BASIC, GW-BASIC
                            # Early 6502 BASIC used 63999.

    def __init__(self, text=None, *, txttab=None, maxlin=NEW_MAXLIN):
        ''' Initialize this set of lines with program text in in-memory or
            disk save (prefixed by a type byte) format.

            `txttab` is the memory offset at which the lines start. If
            not provided, it will be automatically determined from `text`
            if present, or use a default value of 0x0801.
        '''
        self.maxlin = maxlin
        self.orig_text = text
        self.lines = {}
        if text is None:
            self.txttab = txttab or 0x0801
        else:
            self.txttab = self.parsetext(text)

    def parsetext(self, text):
        ''' Parse the given binary `text` data into lines, adding them to
            the lines already held by this object. New lines with the same
            line number as an existing line will overwrite the existing line.

            This returns the start address of `text` as calculated from
            the data in `txt`; it does not change this instance's `txttab`

            Parsing is done by scanning for the 0x00 terminator byte in the
            line data. Except for the first offset, which is assumed
            correct and used to calculate the starting address `txttab`,
            offset values are ignored. However, they are checked against
            what they're expected to be and a (lineno, expected offset,
            actual offset) tuple is appended to the `bad_offsets` property
            for each line that has an offset value not matching the length
            of the data. (`bad_offsets` is cleared when `parsetext()` is
            called so it will contain the bad offsets from only the most
            recent call.)
        '''
        self.bad_offsets = []

        p = 0
        if text[p] == 0xFF:     # If type byte (XXX or 250 char line!)
            text = text[1:]     # is present, drop it.

        def linelen():
            ' Len of the entire line, including offset, lineno and terminator. '
            return 2 + 2 + text[p+4:].find(b'\x00') + 1

        #   Calculate txttab by subtracting the length of the first line,
        #   calculated by finding its terminating 0x00 byte, from the
        #   offset of the second line at the start of the text.
        txttab = unle(text[p:]) - linelen()

        while True:
            offset = unle(text[p:])
            if offset == 0:
                break
            lineno = unle(text[p+2:])
            data = text[p+4 : p+linelen()-1]
            self.setline(lineno, data)
            p += linelen()
            if p + txttab != offset:
                self.bad_offsets.append((lineno, p+txttab, offset))

        return txttab

    def setline(self, lineno, bs):
        ' Set line `lineno` of the text to the data `bs`. '
        if lineno < 0 or lineno > self.maxlin:
            raise ValueError('Line number {} out of range 0-{}'
                .format(lineno, self.maxlin))
        if b'\x00' in bs:
            raise ValueError(
                'data may not have byte(s) with value 0'
                ' (lineno={} data={})'.format(lineno, repr(bs)))
        self.lines[lineno] = bs

    def text(self):
        ''' Return a `bytes` containing the current tokenized text.
            This does not include a leading file type byte.
        '''
        nextaddr = self.txttab
        data = []
        for lineno in sorted(self.lines.keys()):
            linedata = self.lines[lineno]
            nextaddr = nextaddr + 2 + 2 + len(linedata) + 1
            data.extend([ le(nextaddr), le(lineno), linedata, b'\x00' ])
        data.append(le(0))
        return b''.join(data)

    def write_to(self, stream):
        ''' Write the current tokenized text to `stream`,
            preceeded by a 0xFF file type byte.
        '''
        stream.write(b'\xFF')       # type byte
        stream.write(self.text())

def le(n):
    ' Return _n_ as little-endian unsigned 16-bit int. '
    return struct.pack('<H', n)

def unle(bs):
    ''' Parse the first two bytes of _bs_ as a little-endian unsigned
        16-bit int.
    '''
    return struct.unpack('<H', bs[0:2])[0]
