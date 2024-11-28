from    collections import namedtuple as ntup

class MemImage(list):
    ''' A memory image, usually loaded from an assembler or linker
        output file, consisting of an entrypoint and a list of
        `MemRecord` or similar data records, each with the memory
        address at which it starts and the data.

        The data records may contain additional information, but
        iterating over the sequence will always return ``(addr,data)``
        tuples.

        This is a mutable ordered collection. The records are
        not necessarily in order of address, but `sorted()` will
        return the records ordered by address (assuming any records
        added via `append()` sort properly).

        `startaddr` and `endaddr` are set 
    '''

    def __init__(self, fill=0x00):
        self.startaddr = 0
        self.endaddr = 0
        self.entrypoint = None
        self.fill = 0x00

    class OverlapError(ValueError):
        pass

    MemRecord = ntup('MemRecord', 'addr data')
    MemRecord.__docs__ = \
        ''' A memory record, with an int starting address and sequence
            of byte values that start at that address.
        '''
    def addrec(self, addr, data):
        ''' `append()` a new `MemRecord` to the list of records for this
            image. Additionally, it checks that `data[0]` (if present)
            is an `int`.
        '''
        if len(data) and not isinstance(data[0], int):
            raise TypeError(f'data type {type(data)} not int sequence')
        self.append(MemImage.MemRecord(addr, data))

    def append(self, rec):
        ''' Append an additional data record to the list of records for
            this image. This will update `startaddr` to the start address
            of the lowest record in memory (regardless of where it is in
            the list), and `endaddr` to the highest end address of any
            record (which may not be the end address of the highest record
            if another, lower record extends past it).
        '''
        super().append(rec)
        self.startaddr = self.endaddr = None
        for mr in self:
            if len(mr.data) == 0:
                continue                # Ignore empty records
            if self.startaddr is None or self.startaddr > mr.addr:
                self.startaddr = mr.addr
            recend = mr.addr + len(mr.data)
            if self.endaddr is None or self.endaddr < recend:
                self.endaddr = recend

    def __iter__(self):
        return (self.MemRecord(mr.addr, mr.data) for mr in super().__iter__())

    def contiglen(self):
        ''' Return the number of bytes in this image covers from the
            lowest to highest address. This is the number of bytes
            that will be returned by `contigbytes()`.

            This honours any changes made to `startaddr` and `endaddr`
            made since the last call to `append()` or `addrec()`.

            This does not check to see if the image has overlapping
            records.
        '''
        return self.endaddr - self.startaddr

    def contigbytes(self):
        ''' Return the binary contents of this image as a contiguous
            list of bytes from the lowest address to the highest,
            filling in unset areas with `self.fill`.

            If the image has any overlapping records a `MemOverlap`
            exception will be raised. (Possibly we should add a
            parameter to disable this check.)
        '''
        data = [None] * self.contiglen()
        for mr in self:
            start = mr.addr - self.startaddr
            sl = slice(start, start+len(mr.data))
            for pos, val in enumerate(data[sl], mr.addr):
                if val is not None:
                    raise self.OverlapError(
                        'Data overlap at location ${:04X}'.format(pos))
            data[sl] = list(mr.data)
        self.contig_data = bytes(
            map(lambda x: self.fill if x is None else x, data))
        return self.contig_data
