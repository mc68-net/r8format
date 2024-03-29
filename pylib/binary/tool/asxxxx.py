''' binary.tool.asxxxx - Support for ASxxx_ assembler/linker output

    .. _ASxxxx: http://shop-pdp.net/ashtml/asxdoc.htm
'''

from    collections import namedtuple as ntup
from    struct import unpack_from
import  re

from    binary.memimage   import MemImage
from    binary.symtab   import SymTab

####################################################################

def parse_cocobin_fromfile(path):
    with open(path, 'rb') as stream:
        return parse_cocobin(stream)

def parse_cocobin(bytestream):
    ''' Parse a Tandy/Radio Shack Color Computer DISK Basic
        binary file, returning a `MemImage`.

        This is the ``-t`` output format of ASlink.

        This has poor error-handling; it is intended to be used only
        on files generated by assemblers and linkers that always
        produce valid output.
    '''
    mi = MemImage()
    while True:
        buf = bytestream.read(5)
        type, len, addr = unpack_from('>BHH', buf)
        if type == 0:
            mi.addrec(addr, bytestream.read(len))
        elif type == 0xFF:
            #   len should be 0x0000, but ignore it.
            mi.entrypoint = addr
            return mi
        else:
            raise ValueError('Bad cocobin record ' \
                'type={:02X} len={:04X} addr={:04X} at pos {}' \
                .format(type, len, addr, pos, bytestream.tell()))

####################################################################


class AxSymTab(SymTab):
    ''' The symbol table of an ASxxxx module, including local symbols.

        ASxxxx calls sections "areas"; the `Symbol` section value is
        the area number. The addtional `areas` property is a tuple of
        `Area` objects indexed by area number.

        The source data for the symbols in relocatable sections has
        non-relocated (pre-link) symbol values; the `readsymtabpath()`
        function will call `relocate()` to read the area information
        and modify the symbol values to their relocated values. If
        relocations have been done (using `relocate()`), `relocated`
        will be `True`.

        This is normally generated from symbol and area tables in a
        .sym file or .lst/.rst listing file (both are the same format
        for the symbol table section) using the .map file to path up
        the relocations for relocatable areas. The .map and debugger
        files include only the global symbols that are exported by the
        module, and we want to be able to use local symbols when
        testing.
    '''

    def __init__(self, symbols, areas):
        ''' Takes a container of `Symbol`s and a sequence of `Area`s.
            Each Area's number must also be its index.
        '''
        super().__init__(symbols)
        self.areas = tuple(areas)
        self.relocated = False

    def areanamed(self, name):
        ' Return the area with the given name; throw KeyError if not found. '
        for a in self.areas:
            if a.name == name:
                return a
        raise KeyError("Area named '{}' not found".format(name))

    @staticmethod
    def readsymtabpath(path):
        ''' Given a path, attempt to read the symbol table information
            from that file, falling back to other likely related files
            if that file is not present (e.g., it was given without an
            extension) or does not contain the symbol and area tables.

            This may attempt to read any of the following files for
            the symbol table data it needs:
            - `.sym`: non-relocated local and global symbols from the
              assembler, if this file exists.
            - `.rst`: Generated by the linker from the `.lst` file.
              While the listing has relocated addresses, the symbol
              table, if it was in the `.lst` file, does not.
            - `.lst`: non-relocated local and global symbols from the
              assembler, if a listing but no .sym file was generated.

            It will further always try to read the `.map` file
            generated by the linker, which is the only source of the
            relocation data for the areas in which the symbols reside.

            XXX This currently assumes that the radix is hexadecimal.
            It should at least check the header line to ensure that it
            says 'Hexadecimal [16-bits]'.
        '''
        path = str(path)        # we accept path-like objects
        if path[-4] == '.':
            noext = path[0:-4]
        else:
            noext = path
        symtab = None
        for withext in (path, noext+'.sym', noext+'.rst', noext+'.lst'):
            try:
                with open(withext, 'r') as stream:
                    symtab = AxSymTab.readsymtabstream(stream)
            except FileNotFoundError:
                pass
        if symtab is None:
            raise FileNotFoundError(
                'Could not find .sym .rst or .lst for path ' + path)
        with open(noext+'.map', 'r') as stream:
            symtab.relocate(stream)
            #   This raises FileNotFoundError when we can't read the .map file.
            #   Another option would be to print a warning and continue with
            #   an unrelocated symbol table, but it's more reliable and minimal
            #   extra effort to make the developer always generate a .map file.
        return symtab

    @staticmethod
    def readsymtabstream(stream):
        ''' Read the symbol and area tables from the given input
            stream, which must be ASxxxx .lst, .rst or .sym output.
            `None` is returned if no symbol table is present. The
            symbols in relocatable areas have original, NOT relocated,
            values.

            To patch relocatable values to their proper locations
            based on a .map file, use `relocate()`.
        '''
        symlines, arealines = AxSymTab.symtab_lines(stream)
        if len(symlines) == 0:
            return None

        symbols = tuple(map(AxSymTab.parse_symline, symlines))

        #   It appears that areas within a single module are numbered
        #   consecutively (though not printed in order) with area
        #   numbers local to that module.
        areas = sorted(tuple(map(AxSymTab.parse_arealine, arealines)))
        return AxSymTab(symbols, areas)

    HEADERLINE = re.compile(r'.?ASxxxx Assembler')

    @staticmethod
    def symtab_lines(bytestream):
        ''' From the stream return a pair of arrays, one with the
            symbol table entry lines and one with the area table entry
            lines. All header lines and lines before the symbol table
            are ignored.

            The symbol table entry lines will be split at ``| `` if
            present, thus when reading narrow format we generate two
            output lines for each input line.

            Trailing spaces will be removed.

            XXX This should also read the 'Hexadecimal [16-bits]' or
            other radix information from the header and return it.
        '''
        f = bytestream
        symlines = []; arealines = []
        while True:
            line = f.readline()
            if line == '': return symlines, arealines   # EOF
            if line.strip() == 'Symbol Table': break    # reached Symbol Table
        while True:
            line = f.readline()
            if line == '': break                        # EOF
            if line == '\n': continue                   # blank line
            if line.strip() == 'Area Table': break      # end of symbol table
            if AxSymTab.HEADERLINE.match(line):
                f.readline()                            # skip 2nd header line
            else:
                if '| ' not in line:
                    symlines.append(line.rstrip())
                else:
                    #   Narrow format; split it
                    left, right = line.split('| ')
                    symlines.append(left.rstrip())
                    symlines.append(right.rstrip())
        while True:
            line = f.readline()
            if line == '': break                        # EOF
            if line == '\n': continue                   # blank line
            if line[0] == '[': continue                 # CSEG/DSEG
            if AxSymTab.HEADERLINE.match(line):
                f.readline()                            # skip 2nd header line
            else:
                arealines.append(line.rstrip())

        return symlines, arealines

    @staticmethod
    def parse_symline(line):
        ''' Given a symbol table line (from `symtab_lines()`),
            return a `Symbol` object.

            XXX This does not check to see if the symbol name is
            potentially truncated, though it should do so.
        '''
        if '=' in line:
            #   An equate, which might not have a flags field.
            areanum = None
            fields = line.split()
            name = fields[0]
            value = fields[2]
            flags = fields[3] if len(fields) > 3 else ''
        else:
            areanum, name, value, flags = line.split()
            areanum = int(areanum)
        return SymTab.Symbol(name, int(value, 16), areanum)

    class Area(ntup('Area', 'number, name, flags')):
        def isrelative(self):
            ''' Whether this is a relative or absolute area.
                Flags bit 3 is set for absolute, clear for relative.
            '''
            return (self.flags & 0x08) == 0

    @staticmethod
    def parse_arealine(line):
        num, name, _, size, _, flags = line.split()
        return AxSymTab.Area(int(num), name, int(flags, 16))

    ####################################################################
    #   .map files and relocation

    def relocate(self, stream):
        ''' Read an ASxxxx .map file and relocate the symbols in this
            AxSymTab based on the area addresses in that file.

            This completely ignores bank information.
        '''
        if self.relocated:
            raise TypeError("Already relocated")
        areas = map(AxSymTab.parse_maparealine,
            AxSymTab.mapfile_arealines(stream))
        for name, addr in areas:
            if addr == 0: continue      # No relocation to be done
            areanum = self.areanamed(name).number
            for name, sym in self.symbols.items():
                if areanum == sym.section:
                    self.symbols[name] = sym._replace(value=sym.value+addr)
        #   Even if we did no actual relocations, set this so that clients
        #   know relocation was done and no symbols needed to be updated.
        self.relocated = True

    MAPFILE_AREAHEADER = re.compile(r'^Area *Addr *Size *Decimal *Bytes')

    @staticmethod
    def mapfile_arealines(stream):
        ''' Return a list of area lines from a map file. '''
        areaheader = AxSymTab.MAPFILE_AREAHEADER
        lines = []
        while True:
            line = stream.readline()
            if line == '': return lines         # EOF
            if areaheader.match(line):
                stream.readline()               # skip delimiter line
                lines.append(stream.readline())
                #   There seems to be only ever one area line after
                #   an area line header.
        return lines

    @staticmethod
    def parse_maparealine(line):
        name, addr, _ = line.split(maxsplit=2)
        name = line[0:25].rstrip()
        addr = line[27:39]
        return name, int(addr, 16)

    ####################################################################
    #   Old stuff

    #   XXX do we want to use this instead of our `split()` parsing?
    #   It might work better for determining whether a symbol name has
    #   been truncated.
    @staticmethod
    def old_parse_symline(ent):
        ''' Parse the entry for a symbol from ASxxxx symbol table listing.

            Per §1.3.2, symbols consist of alphanumerics and ``$._``
            only, and may not start with a number. (Reusable symbols
            can start with a number, but they do not appear in the
            symbol table.)

            Per §1.8, the entry in the listing file is:
            1. Program  area  number (none if absolute value or external).
               XXX The value below is relative to the start of this area,
               which needs to be taken from the ``.map`` file. Currently
               we ignore this and produce the wrong symbol value.
               (The symbol values in the ``.map`` file are correct, but
               only global symbols are in that file, and only the first 8
               chars of the symbol name.)
            2. The symbol or label
            3. Optional ``=`` if symbol is directly assigned.
            4. Value in base of the listing or ``****`` if undefined.
            5. Zero or more of ``GLRX`` for global, local, relocatable
               and external symbols.

            Docs at <http://shop-pdp.net/ashtml/asmlnk.htm>.
        '''
        SYMENTRY = re.compile(r'(\d* )?([A-Za-z0-9$._]*) *=? * ([0-9A-F*]*)')
        match = SYMENTRY.match(ent)
        return match.group(2), int(match.group(3), 16)
