#!/usr/bin/env python3

''' blines - produce text BASIC lines from "expanded" BASIC source

    The "expand" option of the detokenizer generates a multiline (per
    BASIC line) format to which developers typically add comments.
    This program partially undoes that, removing comments and
    producing a single line for each BASIC line. Since it generates
    text output this can be used with any BASIC that numbers each
    line, even if we have no tokenizer for it.

    As with all programs in this suite, it expects that "expanded"
    BASIC is always in UTF-8 encoding. However, the output of this
    program is in the current locale's encoding so that it can be used
    to generate untokenized BASIC programs to be read by other systems
    that use other encodings known to Python. (XXX But possibly this
    should be using conversion tables instead.)

    This does not remove any "expansion" within the lines (such as
    additional spaces); use the retokenizer to do that.
'''

from    sys import argv
from    bastok.blines  import blines

def main():
    with open(argv[1], encoding='UTF-8') as f:
        for l in blines(f.readlines()): print(l)
