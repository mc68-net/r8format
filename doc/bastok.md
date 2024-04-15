bastok - BASIC Tokenization Tools
=================================

This repository contains a detokenizer, written in Python, for [MSX-BASIC].
It should not be hard to extend to detokenize other Microsoft BASICs, or any
BASICs that use a similar tokenization format. A tokenizer is also planned,
but not currently available.

The primary aim of these tools is to help with reverse-engineering BASIC
programs, especially when dealing with historical and custom character
sets, but they may also be useful for people developing software in BASIC.

#### Files and directories

- `detok`: A command-line detokenization tool. Given an input filename,
  it will read that as a tokenized BASIC file and print the detokenized
  version to stdout in UTF-8 (the user's locale is ignored) or GHB/MSX-BASIC
  (see below) encoding. Give the `-h` option for help.
- `Test`: A Bash script to set up a Python virtual environment and run the
  unit tests. Any parameters passed to this will be passed on to `pytest`.
- `psrc/bastok/`: A Python module containing the (de-)tokenization tools.
- `programs/`: Test programs, both tokenised and ASCII.
- `tool/`: Development tools.


Character Sets
--------------

These tools define [MSX] machines to use two character sets: the "MSX
character set" with 256 code points corresponding to the 256 positions in a
character glyph definition table (known as the [_pattern generator
table_][2t pgtab]) and ASCII with 128 code points corresponding to the
128 ASCII characters.

The standard character set for an MSX machine varies by region; details of
these can be found on the msx.org wiki page [MSX font][font]. Programs may
also define their own character sets.

BASIC program text is always considered to be printable ASCII text (i.e.,
control characters are not allowed) and is converted to its Unicode
equivalent. Since `detok` always generates UTF-8 output when doing
conversion, these parts of the program will always be ASCII as well. BASIC
program text is all text in a BASIC program except for: string constants,
`DATA` statement arguments and what follows `REM`. The quotes surrounding a
string constant and the commas separating `DATA` arguments are part of the
program text and will always be rendered in ASCII.

Within string constants (between double-quotes) `DATA` arguments (whether
quoted or not) and after a `REM` the text is interpreted as the "Graphic
Header Byte" (グラフ ィ ック ヘッダ バイ ト) or "GHB" encoding used by
MSX-BASIC and the BIOS `CNVCHR` ($0AB) routine.

The GHB encoding maps:
- Bytes valued 0x00, 0x02-0x1F and 0x7F to their corresponding ASCII
  control characters. (Some of these are interpreted by print routines as
  cursor movement and other commands; see msx.org wiki page [MSX Characters
  and Control Codes][codes].)
- Bytes valued 0x20-0x7E and 0x80-0xFF to their corresponding MSX character
  set code points.
- Byte sequences matching 0x01 _NN_, where _NN_ is 0x41-0x5F, to MSX
  character set code points _NN-0x41_, i.e. 0x01-0x1F.
- There appears to be no official way to represent code point 0 (always a
  "blank" character, the same as space, in the official character sets),
  but many third-party sources use 0x01 0x00, as does this program.

The detokenizer converts GHB encoded characters to Unicode characters
using a built-in or (soon) user-specified mapping. (You can see the list of
currently known MSX character sets by by giving any unknown character set
name to the `-c` option of a command-line program, e.g., `detok -c - -`.)

The use of ASCII in BASIC program text and an MSX character set in string
constants allows you to edit a BASIC program that uses a custom MSX
character set that remaps printable ASCII characters, while seeing the
BASIC program in ASCII but the strings in the target character set. For
example, if MSX code point 0x50 is changed to `⌘` in a custom character
set, an MSX machine would display that for all uses of `P` in a BASIC
program, or in strings containing that character it would be displayed as
`P`, depending on whether you were displaying the standard or your custom
character set. The detokenizer output, however, would display both
correctly in context.

    10 P$="P"       ← standard character set on MSX
    10 ⌘$="⌘"       ← custom character set on MSX
    10 P$="⌘"       ← detokenizer Unicode output

The detokenizer can also run in a "binary" mode where no conversion is done
and GHB encoding is output directly (the `-b` or `--binary` option).

Support for programs that use kanji ROM characters needs to be investigated.


Formatting
----------

`detok` offers an `--expand`/`-e` option to generate source code in a more
readable format, especially if the program text is "packed" to save space
by minimizing use of spaces. When enabled it will render this:

    10 FORI=16TO40STEP2:IFI<32THENPRINTI:NEXTIELSEPRINTCHR$(I):NEXTI

as:

       10 FOR I=16 TO 40 STEP 2
        : IF I<32 THEN PRINT I
        : NEXT I ELSE PRINT CHR$(I)
        : NEXT I

This is far from perfect (in the above example clearly the line split
should be before the `ELSE`, not the preceeding `: NEXT I`) but since in
most workflows the developer will do further manual reformatting to better
express the code as she reverse-engineers the program, this is fine to
kickstart the process.

The (re-)tokenizer, when written will read programs in the above format and
be able to "compress" them back to a tokenized version without unnecessary
spaces.


Caveats and Todo Items
----------------------

* The only charsets currently implemented are `ja` (MSX2 Japanese) and
  `int` (MSX2 International/European). The others should not be hard
  to implement for those willing to find the matching Unicode chars.

* It might be reasonable to be able to decode native characters, especially
  control sequences, to a multi-character Unicode sequence, e.g., 0x00 to
  `‹00›` and 0x08 to `‹H›` (those characters are are U+2039 and U+203A,
  "single left/right-pointing angle quotation mark; see [[brackets]] for
  some other possibilities), similar to Commdore BASIC control character
  quotation. The effects of introducing multi-byte Unicode sequences in the
  detokenized program text need thought.

* Some programs created with tools other than the MSX BASIC interpreter may
  use binary data, including invalid encoding sequences, in string
  constants and/or REM statements. (This is often to embed binary data or
  machine-language routines into the BASIC program.) Currently bastok does
  not handle this, and how best to handle this is not yet clear. Having
  some examples of large programs that do this would help.

* To assist reverse-engineering, it's planned to add support for a
  multi-line format for the source files generated by the detokenizer and
  processed by the tokenizer, allowing one to place `:`-separated
  statements on separate lines, add comments not inserted into the
  tokenized version of the program, and "compression" (to remove
  unnecessary spaces, etc.) when tokenizing.

* `DEF USRn` with a number _n_ is currently detokenised with a space before
  the number, e.g., `DEF USR 3=&HDE00`. This is an aesthetic issue only; it
  works the same in MSX-BASIC with or without spaces there.


<!-------------------------------------------------------------------->
[2t pgtab]: https://github.com/Konamiman/MSX2-Technical-Handbook/blob/master/md/Chapter4a.md#pattern-generator-table
[codes]: https://www.msx.org/wiki/MSX_Characters_and_Control_Codes
[font]: https://www.msx.org/wiki/MSX_font
[msx-basic]: https://en.wikipedia.org/wiki/MSX_BASIC
[msx]: https://en.wikipedia.org/wiki/MSX

[brackets]: https://en.wikipedia.org/wiki/Bracket#Encoding_in_digital_media
