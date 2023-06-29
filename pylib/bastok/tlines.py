from    io  import BytesIO
import  struct

class TLines:
    ''' A sequence of tokenized BASIC lines.

        Each line has an associated decimal line number and opaque (to this
        class) tokenized data. The data are typical tokenized BASIC program
        text lines, but they may be any sequence of bytes including 0x00
        bytes).

        The sequence also has a `txttab` memory address for the start point
        used when reading or generating a "program image": the binary format
        used in ``.BAS`` save files and in memory starting at ``TXTTAB``.

        Functions:
        - `__init__()`: Create a new sequence, either empty or from a
          program image that will be passed to `parsetext()`.
        - `clearlines()`: Clear all lines and `orig_text`.
        - `parsetext()`: Add lines from a program image to the list.
        - `setline()`: Add a single line to the program image.
        - `lines()`: Return the line numbers and data as a sequence
          of``(int,bytes)`` tuples.
        - `text()`: Generate a program image starting at `txttab`.
        - `write_to()`: Write a filetype byte and program image to a stream.

        Attributes:
        - `linemap`: A dictionary mapping `int` line number to the line
          data (without the terminating 0 byte).
        - `orig_text`: The original (pre-parse) text data this instance was
          instantiated with, if any (otherwise `None`). This should be the
          same as the result of `text()` if the original text was valid,
          `txttab` has not been changed from the value discovered by the
          parse, and no lines have been added, deleted or changed. This
          is not changed once set, except by `clearlines()`.

        Issues:
        - This currently assumes little-endian format, which is fine for
          8080 or 6502, but not for 6800.
        - `maxlin` defaults to 65529, which is correct for MSX-BASIC and
          GW-BASIC, but not for early 6502 BASIC (63999).
    '''

    MAXLIN_5 = 65529        # v5.x: MSX-BASIC, GW-BASIC
    MAXLIN_2 = 63999        # v2.x: Early 6502 BASIC

    TXTTAB_PET      = 0x0401
    TXTTAB_APPLE2   = 0x0801
    TXTTAB_C64      = 0x0801
    TXTTAB_8080     = 0x8001    # Also Z80

    def __init__(self, text=None, *, txttab=None, maxlin=MAXLIN_5):
        ''' Create a list of tokenized lines starting at address `txttab`.
            if a `bytes` `text` is supplied, it will be parsed with
            `parsetext()`, providing the initial set of lines.
        '''
        self.maxlin = maxlin

        #   XXX does not work without txttab right now, but should
        #   use the BASFile trick to figure it out.
        self.txttab = int(txttab)
        if self.txttab < 0:
            raise ValueError('txttab {} < 0'.format(self.txttab))

        self.clearlines()
        if text is not None:
             self.parsetext(text, txttab)

    def clearlines(self):
        ' Clear all lines and `orig_text`. '
        self.orig_text = None
        self.linemap = {}

    def parsetext(self, text, txttab=None):
        ''' Parse the given program image `text` into lines, adding them to
            the lines already held by this object. New lines with the same
            line number as an existing line will overwrite the existing line.

            `text` must not include the initial file type byte (usually
            0xFF) that usually starts a .BAS file.

            `txttab` must be the correct start address for the system
            that saved the data.

            Each line's data is checked to see that it ends with a 0x00
            termination byte; a `ValueError` will be raised if it does
            not, indicating either bad data or a bug in this function.
        '''
        if txttab == None:
            txttab = self.txttab
        if self.orig_text is None:
            self.orig_text = text

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
        ''' Set line `lineno` of the text to the data `bs`. This will
            overwrite an existing line of that number, if present.
        '''
        if lineno < 0 or lineno > self.maxlin:
            raise ValueError('Line number {} out of range 0-{}'
                .format(lineno, self.maxlin))
        self.linemap[lineno] = bs

    def lines(self):
        ''' Return (`int`, `bytes`) tuples containing the line number
            and its tokenized data, in line number order.
        '''
        return ( (l, self.linemap[l]) for l in sorted(self.linemap.keys()) )

    def linenos(self):
        ' Return a sequence of the line numbers, in line number order. '
        return tuple(sorted(self.linemap.keys()))

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

####################################################################
#   Small utility routines

def le(n):
    ' Return _n_ as little-endian unsigned 16-bit int. '
    return struct.pack('<H', n)

def unle(bs):
    ''' Parse the first two bytes of _bs_ as a little-endian unsigned
        16-bit int.
    '''
    return struct.unpack('<H', bs[0:2])[0]

####################################################################
#   BASFile

class BASFile():
    ''' A representation of save of a tokenised BASIC program, i.e., a
        ``.BAS`` file. This distinguishes between the file header
        and the BASIC "text" itself and may be able to guess from
        what system a file was saved.

        `TYPES` is a list of all the filetypes this knows.

        XXX This currently assumes little-endian format.
    '''

    class BadHeader(ValueError):
        pass

    TYPES = [
        'TXTTAB',       # no header
        'MSX',          # Disk MSX-BASIC files
        ]

    def __init__(self, filebytes, filetype):
        ''' Create a BASFile` from `filebytes` containing the contents of a
            ``.BAS`` file (a tokenised save), and the given machine/BASIC
            filetype. If `filetype` is none, this will try to guess the filetype.

            A `BadHeader` will be thrown if the parse fails.
        '''
        self._filebytes = filebytes
        self._filetype  = filetype
        self._header    = None
        self._txttab    = None
        self._bio       = None

        if len(filebytes) < 5:
            raise ValueError(
                'filesbytes len={} too small'.format(len(filebytes)))

        if filetype == 'TXTTAB':
            self._header = b''
            self._txttab = filebytes
        elif filetype == 'MSX':
            self._header, self._txttab = filebytes[0:1], filebytes[1:]
            if self._header != b'\xFF':
                raise self.BadHeader('expected MSX header {}, got {}' \
                    .format(b'\xFF', self._header))
        else:
            raise ValueError('Unknown filetype: {}'.format(self._filetype))

    def filetype(self):     return self._filetype
    def header(self):       return self._header
    def txttab(self):       return self._txttab

    def addr(self):
        ''' Determine the start address of `txttab()`.

            This works only with more than one line: it calculates the
            length of the first line and then subtracts that from the
            start address of the second line.
        '''
        tt = self.txttab()
        p = 4                       # skip 2 bytes addr and 2 bytes lineno

        if unle(tt) == 0:           # only one line in file
            return None
        while True:
            if p > len(tt): return None
            if tt[p] == 0:  break
            p += 1
        return unle(tt) - (p+1)

    def read(self, n=None):
        ' Read bytes from `txttab()` as a stream. '
        if self._bio is None:
            self._bio = BytesIO(self.txttab())
        return self._bio.read(n)
