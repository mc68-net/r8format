#!/usr/bin/env python3
''' Disassemble the given file to stdout using z80dasm.

    The input file should be in MSX-BASIC BLOAD format, with an initial
    type byte of $FE followed by the load address, end address and entry
    address. The load address will be used as the start point of the
    disassembly.

    Though an MSX machine will not load past the end address in the header,
    we pass those non-loaded bytes to the disassembler anyway just in case
    there's anything useful in them.

    ./info/ is checked for files with the filename of the input
    file and ``.sym`` and ``.block`` extensions; if these exist they
    will be passed to z80dasm

    z80dasm can be installed with ``apt-get install z80dasm`` on Debian
    and Ubuntu systems; for other systems see:
    https://www.tablix.org/~avian/blog/articles/z80dasm/
'''

from    argparse import ArgumentParser
from    os.path  import basename, exists, join
from    struct  import unpack
from    subprocess  import run
from    tempfile  import TemporaryDirectory
import  sys

def warn(*msgparts):
    print(' '.join(msgparts), file=sys.stderr)

def die(exitcode, *msgparts):
    warn(*msgparts)
    exit(exitcode)

def disasm(args, tmpdir):
    obj = join(tmpdir, 'obj')

    with open(args.input, 'rb') as fin:
        type_byte = fin.read(1)
        if type_byte != b'\xFE':
            die(1, 'Bad type byte', str(type_byte), 'for', args.input)
        load_addr  = unpack('<H', fin.read(2))[0]
        end_addr   = unpack('<H', fin.read(2))[0]
        entry_addr = unpack('<H', fin.read(2))[0]
        with open(obj, 'wb') as fnohdr:
            fnohdr.write(fin.read())

    comment = '; msx-dasm load=${:04X} end=${:04X} entry=${:04X}' \
        .format(load_addr, end_addr, entry_addr)
    print(comment, flush=True)      # assumes no `-o` option to z80dasm

    dasm = ['z80dasm']
    dasm.append('-l')
    dasm.extend(['--origin', hex(load_addr)])

    symfile = join('info', basename(args.input) + '.sym')
    if exists(symfile):
        dasm.extend(['--sym-input', symfile])
    else:
        warn('No symbol info file: {}'.format(symfile))

    blockfile = join('info', basename(args.input) + '.block')
    if exists(blockfile):
        dasm.extend(['--block-def', blockfile])
    else:
        warn('No block info file: {}'.format(blockfile))

    if args.address: dasm.append('-a')
    if args.source: dasm.append('-t')
    dasm.append(obj)
    run(dasm)

def main():
    p = ArgumentParser(description=\
        "Use z80dasm to disassemble an MSX-BASIC 'BLOAD' format file.")
    a = p.add_argument
    a('-a', '--address', action='store_true',
        help='Comment the address for each line')
    a('-t', '--source', action='store_true',
        help='Comment the binary data for each line.')
    a('input', help='input file (required)')
    args = p.parse_args()

    with TemporaryDirectory() as tmpdir:
        disasm(args, tmpdir)
