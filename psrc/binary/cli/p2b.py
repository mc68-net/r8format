' Generate executable files in various formats from ASL .p files. '

from    argparse  import ArgumentParser
from    os.path  import basename
from    struct  import pack
from    sys  import argv, stderr
import  sys

from    binary.tool.asl  import MemImage, parse_obj_fromfile

FORMATS = {
    'a2':   'Apple II DOS type `B` file',
    'kc85': '.CO file for Kyocera 85/Tandy Model 100/NEC PC-8201/etc.',
}

def main():
    args = parseargs()
    #   This is a very quick and dirty way of handling this, but conforms
    #   to our long-term interface.
    if args.format not in FORMATS:
        print(f"p2b: Unknown format: '{args.format} (`-L` to list formats)'",
            file=stderr)
        exit(2)
    pfile = parse_obj_fromfile(args.input)
    bin = globals()['bin_' + args.format](pfile)
    if args.output == '-':
        sys.stdout.buffer.write(bin)
    else:
        with open(args.output, 'wb') as f:  f.write(bin)

def parseargs():
    #   Rather a hack, since it doesn't handle e.g. `--`.
    if '-L' in argv[1:] or '--list-formats' in argv[1:]:
        listformats()

    p = ArgumentParser(description=
        'Generate executable files in various formats from ASL .p files.')
    #   Possibly at some point we want subparsers here if we need to be
    #   able to have options for individual conversion routines.
    a = p.add_argument
    a('-L', '--list-formats', action='store_true',
        help='print list of known output formats')
    a('-v', '--verbose', action='count', default=0,
        help='increase verbosity; may be used multiple times')
    a('format', help="binary format for output; 'list' to see formats")
    a('input', help='path to input .p file')
    a('output', help='path to output file')
    return p.parse_args()

def listformats():
    print(f'{basename(argv[0])} formats:')
    for name, desc in FORMATS.items():
        print(f'  {name:>8}: {desc}')
    exit(0)

####################################################################

def bin_a2(mi:MemImage):
    if mi.entrypoint is not None and mi.entrypoint != mi.startaddr:
        raise ValueError('Start address ${:04X} != ${:04X} entrypoint' \
            .format(mi.startaddr, mi.entrypoint))
    if mi.contiglen() > 0x7FFF:
        #   DOS 3.3 does not support binary files >= 32 KB.
        raise ValueError('Length {:04X} > $7FFF'.format(mi.contiglen()))
    return bytes(b''
        + pack('<H', mi.startaddr)
        + pack('<H', mi.contiglen())
        + mi.contigbytes()
    )

def bin_kc85(mi:MemImage):
    return bytes(b''
        + pack('<H', mi.startaddr)
        + pack('<H', mi.contiglen())
        + pack('<H', mi.entrypoint)
        + mi.contigbytes()
    )
