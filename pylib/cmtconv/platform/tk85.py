''' cmtconv.platform.tk85
'''
from    enum  import IntEnum
from    itertools  import chain
from    cmtconv.logging  import *
from    cmtconv.audio  import PulseDecoder, PULSE_MARK, PULSE_SPACE, \
        Encoder, silence, sound, ReadError
import  cmtconv.audio

####################################################################

class Block(object):
    ''' TK-85 tape format

        Saves from the TK-85 have no blocking, so we treat them as
        a single "block."

        The lead-in is a long stream of 2400 Hz, stream
        of 2400 Hz. The data follows.

        Mark is     2400Hz for 4 pulses
        Space is    1200Hz for 2 pulses
        Bits are    "reversed" (LSB first)
        Start is    (space,)
        Stop is     (mark, mark)

        A suitable analyze-cmt command line is:
            analyze-cmt -m 2400 --mark-pulses 4 -s 1200 --space-pulses 2 \
                  -B --reverse-bits --start s --stop mm ${input} ${output}

        The format is as follows:
            0x55                    - MAGIC
            (file_no,)              - File number
            (start_hi, start_lo)    - Start address, big endian
            (end_hi, end_lo)        - End address, big endian
            (hdr_chksum,)           - Header checksum
            (data, ...)             - Data
            (data_chksum,)          - Data checksum

    '''

    platform = "NEC TK-85"

    HEADER_BLOCK_LEN = 6

    class BlockType(IntEnum):
        HEADER  = 0x00
        DATA    = 0x01

    @classmethod
    def _calc_checksum(cls, data):
        return (0x100 - (sum(data) % 0x100)) % 0x100

    class ChecksumError(ValueError) : pass

    def __repr__(self):
        return '{}.{}( data={})'.format(
                self.__class__.__module__,
                self.__class__.__name__,
                self._data)

class HeaderBlock(Block):

    MAGIC               = b'\x55'

    @classmethod
    def make_block(cls, file_num, start_addr, end_addr):
        return cls(file_num, start_addr, end_addr)

    def __init__(self, file_num=0x01, start_addr=0x0, end_addr=0x0):
        'For internal use only.'
        self._file_num = file_num
        self._start_addr = start_addr
        self._end_addr = end_addr

    @classmethod
    def _check_magic(cls, bs):
        if bytes(bs[0:len(cls.MAGIC)]) != cls.MAGIC:
            raise ReadError('Bad magic,'
                ' expected={} actual={}'.format(repr(cls.MAGIC), repr(bs)))

    @classmethod
    def from_header(cls, headerbytes):
        cls._check_magic(headerbytes)
        file_num = headerbytes[1]
        start_addr = 256 * headerbytes[2] + headerbytes[3]
        end_addr = 256 * headerbytes[4] + headerbytes[5]
        return cls(file_num, start_addr, end_addr)

    @property
    def isoef(self):
        return False

    @property
    def filenum(self):
        return self._file_name

    @property
    def start_addr(self):
        return self._start_addr

    @property
    def end_addr(self):
        return self._end_addr

    @property
    def checksum(self):
        return self._calc_checksum(self._to_bytes()[1:])

    @property
    def filedata(self):
        return bytearray()

    def _to_bytes(self):
        b = bytearray()
        b.extend(self.MAGIC)
        b.append(self._file_num)
        b.append((self._start_addr >> 8) & 0xff)
        b.append(self._start_addr & 0xff)
        b.append((self._end_addr >> 8) & 0xff)
        b.append(self._end_addr & 0xff)
        return b

    def to_bytes(self):
        b = self._to_bytes()
        b.append(self.checksum)
        return b


class DataBlock(Block):
    '''
    '''

    @classmethod
    def make_block(cls):
        return cls()

    def __init__(self):
        'For internal use only.'

    def setdata(self, data, checksum=None):
        expected_checksum = self._calc_checksum(data)
        if checksum is not None:
            v3('Checksum = {:02X}, Expected = {:02X}', checksum,
                expected_checksum)
        if checksum is not None and expected_checksum != checksum:
            raise self.ChecksumError('expected={:02X}, actual={:02X}'.format(
                expected_checksum, checksum))
        self.data = data

    @property
    def isoef(self):
        return True

    @property
    def checksum(self):
        return self._calc_checksum(self.data)

    @property
    def filedata(self):
        return self.data

    def to_bytes(self):
        b = bytearray()
        b.extend(self.data)
        b.append(self.checksum)
        return b


class FileReader(object):
    'Read TK-85 data from audio'

    def __init__(self):
        self.pd = PulseDecoder(2400, 4, 1200, 2, False, True, (0,), (1,1,),
                                (0.25,0.5))

    def read_leader(self, pulses, i_next):
        '''Detect the next leader, read, confirm then return next pulse'''

        (i_next,_) = self.pd.next_mark(pulses, i_next)
        v3('Leader marks detected at %d - %fs' %
            (i_next, pulses[i_next][0]))
        # read N pulses

        i_next = self.pd.next_space(pulses, i_next, 2)

        v3('End of leader at %d - %fs' % (i_next, pulses[i_next][0]))
        return i_next

    # read a file
    # returns ( int, ( block, ) )
    def read_file(self, pulses, i_next):
        i_next = self.read_leader(pulses, i_next)

        n = Block.HEADER_BLOCK_LEN
        (i_next, bs) = self.pd.read_bytes(pulses, i_next, n)

        hdrblk = HeaderBlock.from_header(bs)
        (i_next, chksum) = self.pd.read_byte(pulses, i_next)
        if chksum != hdrblk.checksum:
            raise Block.ChecksumError('expected={:02X}, actual={:02X}'.format(
                hdrblk.checksum, chksum))

        blk_len = hdrblk.end_addr - hdrblk.start_addr + 1

        # Read blk_len bytes
        (i_next, bs) = self.pd.read_bytes(pulses, i_next, blk_len)
        (i_next, chksum) = self.pd.read_byte(pulses, i_next)
        datablk = DataBlock.make_block()
        datablk.setdata(bs, chksum)
        return (i_next, (hdrblk, datablk))


def read_block_bytestream(stream):
    blocks = []
    blk = None
    bs = stream.read()
    hdrblk = HeaderBlock.from_header(bs[0:Block.HEADER_BLOCK_LEN])
    chksum = bs[Block.HEADER_BLOCK_LEN]
    if chksum != hdrblk.checksum:
        raise Block.ChecksumError('expected={:02X}, actual={:02X}'.format(
            hdrblk.checksum, chksum))
    datablk = DataBlock.make_block()
    datablk.setdata(bs[Block.HEADER_BLOCK_LEN+1:-1], bs[-1])
    return (hdrblk, datablk)

def blocks_from_bin(stream, loadaddr=0x8000, filename=None, filetype=None):
    ''' Read file content bytes from `stream` and create a sequence of tape
        block objects representing that file as data to be loaded
        as it would be saved on a TK-85.

        If `filename` is `None`, a default (perhaps empty) filename
        will be generated. Otherwise `filename` will be parsed as an integer
        and used for the file number.
    '''
    bs = stream.read()
    l = len(bs)
    datablk = DataBlock.make_block()
    datablk.setdata(bs)
    end_addr = loadaddr + l - 1
    # Parse filename
    if filename is None:
        filenum = 0xff
    elif filename.startswith('0x'):
        filenum = int(filename, 16)
    else:
        filenum = int(filename)
    if filenum < 0 or filenum > 255:
        raise ValueError('file number must be in range 0x00 to 0xff')
    hdrblk = HeaderBlock.make_block(filenum, loadaddr, end_addr)
    return (hdrblk, datablk)


####################################################################

class FileEncoder(object):
    def __init__(self):
        self.encoder = Encoder(2400, 4, 1200, 2, False, True, (0,), (1,1))

        #self.file_leader = self.encoder.encode_bit(1) * 256
        self.file_leader = self.encoder.encode_bit(1) * 2000

    #
    # block     : Block
    # ->
    # audio     : [AudioMarker]
    def encode_block(self, blk):
        widths = []
        widths.extend(self.encoder.encode_bytes(blk.to_bytes()))
        return [sound(widths)]

    #
    # blocks    : Block
    # ->
    # audio     : (AudioMarker,)
    #
    def encode_blocks(self, blocks):
        audio = [sound(self.file_leader)]
        for b in blocks:
            audio.extend(self.encode_block(b))
        return tuple(audio)

    def encode_file(self, blocks):
        return self.encode_blocks(blocks)


def write_file_bytestream(blocks, stream):
    bs = bytes(chain(*( b.filedata for b in blocks)))
    stream.write(bs)

def parameters():
    return { 'edge_gradient_factor' : 0.4 }
