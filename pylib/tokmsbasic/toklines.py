import  struct

class TokLines:
    ''' A sequence of tokenized lines. The data for each line is typically
        tokenized BASIC program text, but may be any sequence of bytes
        (including 0x00 bytes); this class handles only the line numbers
        and offsets.

        Symbol names such as `txttab` are taken from Microsoft or other
        documentation or source code, where possible.

        Attributes:
        - `linemap`: A dictionary mapping `int` line number to the line
          data (without the terminating 0 byte).
        - `orig_text`: The original (pre-parse) text data this instance was
          instantiated with, if any (otherwise `None`). This should be the
          same as the result of `text()` if the original text was valid,
          `txttab` has not been changed from the value discovered by the
          parse, and no lines have been added, deleted or changed.

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

    def __init__(self, txttab, text=None, *, maxlin=NEW_MAXLIN):
        ''' Create a list of tokenized lines starting at address `txttab`.
            if a `bytes` `text` is supplied, it will be parsed with
            `parsetext()`, providing the initial set of lines.
        '''
        self.linemap = {}
        self.maxlin = maxlin

        self.txttab = int(txttab)
        if self.txttab < 0:
            raise ValueError('txttab {} < 0'.format(self.txttab))

        self.orig_text = text
        if text is not None:
             self.parsetext(txttab, text)

    def parsetext(self, txttab, text):
        ''' Parse the given program image `text` into lines, adding them to
            the lines already held by this object. New lines with the same
            line number as an existing line will overwrite the existing line.

            `text` must not include the initial file type byte (usually
            0xFF) that usually starts a saved BASIC image.

            `txttab` must be the correct start address for the system
            that saved the data.

            Each line's data is checked to see that it ends with a 0x00
            termination byte; a `ValueError` will be raised if it does
            not, indicating either bad data or a bug in this function.
        '''
        curaddr = txttab
        while True:
            offset = curaddr - txttab
            naddr = unle(text[offset:])
            if naddr == 0:
                break
            noffset = naddr - txttab
            lineno = unle(text[offset+2:])
            termbyte = text[noffset-1]
            if termbyte != 0:
                raise ValueError(
                    'line {} at addr ${:04X}: unexpected termination byte'
                    ' ${:02X} at ${:04X} (offset ${:04X})'
                    .format(lineno, curaddr, termbyte, naddr-1, noffset-1))
            data = text[offset+4:noffset-1]
            self.setline(lineno, data)
            curaddr = naddr

    def setline(self, lineno, bs):
        ' Set line `lineno` of the text to the data `bs`. '
        if lineno < 0 or lineno > self.maxlin:
            raise ValueError('Line number {} out of range 0-{}'
                .format(lineno, self.maxlin))
        self.linemap[lineno] = bs

    def lines(self):
        ''' Return (`int`, `bytes`) tuples containing the line number
            and its tokenized data in line number order.
        '''
        return ( (l, self.linemap[l]) for l in sorted(self.linemap.keys()) )

    def text(self):
        ''' Return a `bytes` containing the current tokenized text.
            This does not include a leading file type byte.
        '''
        nextaddr = self.txttab
        data = []
        for lineno, linedata in self.lines():
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
