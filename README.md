r8format - Tools for Manipulating and Converting Retro-8-bit File Formats
=========================================================================

This repository contains tools (mainly written in Python) and Python
libraries for manipulating and converting some common file formats
used on old 8-bit computers.

#### Installation

The tools are run directly from the `bin/` directory; no installation is
required. The libraries are under `pylib/`. All files under `bin/` that
use the libraries find them under the `pylib/` at the same level.

These are tested only under Linux (the top level `./Test` script will run
the unit and functional tests) but probably work under Windows as well,
though this is untested.

A [PyPI] package is planned.

If you have a need to run this on a platform that isn't working, please
contact the authors (below) for support.


Programs
--------

#### bastok

[`bastok`][bt] is a program for de-tokenising and re-tokenising MS-BASIC
programs; it currently supports MSX-BASIC 2.0. Its special powers include
user-configurable conversion between MSX character sets/encodings and
Unicode and an "expanded" Unicode file format that allows better formatting
and extra comments while being able to compress this back down to a format
that uses minimal space in microcomputer memory. See [`doc/bastok.md`][bt]
for full documentation.

The programs under `bin/` include:
- `basdump`: Hex dump of tokenised MS-BASIC programs that formats the
  information to make clear the line pointer, line number and tokenised
  text information.
- `bddiff`: Use `meld` or another diff tool to show the differences between
  the `basdump` output of two tokenised MS-BASIC programs.
- `blines`: Produce single BASIC lines from ASCII/Unicode BASIC source that
  may split lines using `detok`'s expanded format.
- `detok`: De-tokenise a BASIC program to Unicode.

#### cmtconv

[`cmtconv`][cc] converts WAV files of cassette tape saves to `.cas` and
other data file formats, and vice versa. It also understands higher-level
formats such as BASIC and machine-language files. See
[`doc/cmtconv.md`][cc] for full documentation.

The programs under `bin/` include:
- `cmtconv`: Conversion program. Use `-h` for help.
- `analyze-cmt`: Analysis of (usually unknown) CMT save formats in WAV files.

#### Other Programs

The programs under `bin/` include:
- `msx-dasm`: Disassemble an MSX `BSAVE`-format program using `z80dasm`.


Python Libraries
----------------

The following top-level modules are under `pylib`:
- `binary`: Object file and assembler symbol file formats.
- `bastok`: MS-BASIC de- and re-tokenisation.
- `cmtconv`: Microcomputer CMT (cassette tape) image handling.


Support
-------

Contact Curt Sampson (usually known as 'cjs') if you have questions,
comments, feature requests, or just want help using this. The following are
good places to get in touch, more or less in order of preference:
- The "The MSX2 Channel" server on [Discord], in the `#development` group.
  (Feel free to start a thread if the question is not trivially answered.)
- [`@cjs_cynic`] on [Telegram]
- `0cjs` on Discord.
- Email to <cjs@cynic.net>, but a reply from that might take days.

### Authors

- Curt J. Sampson <cjs@cynic.net> (GitHub:[0cjs] Discord:`0cjs`)
- Stuart Croy (GitHub:[croys])



<!-------------------------------------------------------------------->
[PyPI]: https://pypi.org/

<!-- Programs -->
[bt]: ./doc/bastok.md
[cc]: ./doc/cmtconv.md

<!-- Support and Authors -->
[0cjs]: https://github.com/0cjs
[`@cjs_cynic`]: https://t.me/cjs_cynic
[croys]: https://github.com/croys
[discord]: https://discord.com
[telegram]: https://telegram.org
