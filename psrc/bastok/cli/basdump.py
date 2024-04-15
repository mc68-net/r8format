#!/usr/bin/env python3
#
#   bashex - hexdump an MS-BASIC program
#
#   This understands the MS-BASIC binary file and in-memory format and
#   splits the lines based on where the BASIC lines start, rather than
#   at arbitrary 16-byte intervals.
#

from    argparse  import ArgumentParser
from    itertools  import islice
from    struct  import unpack
import  sys

from    bastok.tlines  import BASFile


def eprint(*args):
    ' Print without newline at end. '
    print(*args, end='')

def sprint(n):
    ' Print `n` spaces. '
    print(n * ' ', end='')

def aprint(i_addr):
    ' Print address prefix for line. '
    print('{:04X}:'.format(i_addr), end='')

def hprint(bs):
    ' Print hexdump bytes, each prefixed by a space. '
    for b in bs:
        print(' {:02X}'.format(b), end='')

def vprint(bs):
    ' Print "visible" characters. '
    print(''.join(list(map(vis, bs))), end='')

CONTROL_PICS = (
    '␀', '␁', '␂', '␃', '␄', '␅', '␆', '␇',
    '␈', '␉', '␊', '␋', '␌', '␍', '␎', '␏',
    '␐', '␑', '␒', '␓', '␔', '␕', '␖', '␗',
    '␘', '␙', '␚', '␛', '␜', '␝', '␞', '␟'
)
CONTROL_VIS = (
    '₀', '₁', '₂', '₃', '₄', '₅', '₆', '₇',
    '₈', '₉', 'ₐ', '⋅', '⋅', '⋅', 'ₑ', '⋅',
    '¹', '²', '³', '⁴', '⁵', '⁶', '⁷', '⁸',
    '⁹', '⋅', '⋅', '⋅', '⋅', '⋅', '⋅', '⋅'
)

def vis(b):
    ' Return "visible" version of character code `b`. '
    if b  < 0x20:       return CONTROL_VIS[b]
    if b  < 0x7F:       return chr(b)   # printable ASCII: the char itself
    pass;               return '▥'      # token: cross-hatched box

def printbasline(i_addr, bf):
    nextaddr = bf.read(2)
    i_nextaddr = unpack('<H', nextaddr)[0]
    if i_nextaddr == 0:
        aprint(i_addr)
        hprint(nextaddr)
        return None

    lineno = bf.read(2)
    i_lineno = unpack('<H', lineno)[0]
    aprint(i_addr)
    sprint(36)
    hprint(nextaddr)
    hprint(lineno)
    sprint(3)
    fill = '─' * (10 - len(str(i_lineno)))
    print('─── {}: {}'.format(i_lineno, fill))

    linelen = i_nextaddr - i_addr
    line = bf.read(linelen - 4)      # include trailing $00

    n = 16
    chunks = [line[i:i + n] for i in range(0, len(line), n)]

    i_curpos = i_addr + 4
    for chunk in chunks:
        aprint(i_curpos)
        hprint(chunk)
        sprint(3 * (n - len(chunk)))
        sprint(3)
        vprint(chunk)
        print()
        i_curpos += n

    return i_addr + linelen

def parseargs():
    p = ArgumentParser(description='MS-BASIC hexdump')
    arg = p.add_argument
    arg('input', help='input file (required); use `-` for stdin')
    return p.parse_args()

def main():
    args = parseargs()

    if args.input == '-':   f = sys.stdin.buffer
    else:                   f = open(args.input, 'rb')
    bf = BASFile(f.read(), 'MSX')
    f.close()

    eprint('HEAD:')
    hprint(bf.header())
    print()

    #   TODO: The initial current address should be auto-detected from the
    #   next-line address and the first line length, and/or overridden by
    #   a command-line parameter.
    i_addr = bf.addr()
    if i_addr is None:
        i_addr = 0                      # what else can we do?

    #   TODO: This assumes little-endian format. We need to be able to do
    #   big-endian for 6800.
    while True:
        i_nextaddr = printbasline(i_addr, bf)
        if i_nextaddr is None:
            print()
            break
        else:
            i_addr = i_nextaddr
