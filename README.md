r8format - Tools for Manipulating and Converting Retro-8-bit File Formats
=========================================================================

This repository contains tools (mainly written in Python) and Python
libraries for manipulating and converting some common file formats
used on old 8-bit computers.

#### Installation

This is a [PyPA] package than can be built/installed with any compliant
tool, such as Pip. We suggest you install it in a virtualenv, but this
isn't necessary. Typical methods of installation include:

    #   Install the most recent release from PyPI
    pip install r8format        # https://pypi.org/project/r8format/

    #   Install the latest version directly from GitHub.
    pip install git+https://github.com/mc68-net/r8format.git

    #   Install local copy of the repo in editable form.
    #   You almost certainly want to be using a virtual environment for this.
    pip install -q -e ./r8format

On Linux, the top-level `./Test` script in the repo will run both the
unit and functional (command-line) tests. This has been tested only
under Linux, but will likely work under Windows as well.

If you have a need to run this on a platform that isn't working, please
contact the authors (below) for support.


Programs
--------

#### bastok

[`bastok`][bt] is a system for de-tokenising and re-tokenising MS-BASIC
programs; it currently supports MSX-BASIC 2.0. Its special powers include
user-configurable conversion between MSX character sets/encodings and
Unicode and an "expanded" Unicode file format that allows better formatting
and extra comments while being able to compress this back down to a format
that uses minimal space in microcomputer memory. See [`doc/bastok.md`][bt]
for full documentation.

The command-line programs include:
- `detok`: De-tokenise a BASIC program to Unicode.
- `basdump`: Show a hex dump of tokenised MS-BASIC programs that formats
  the information to make clear the line pointer, line number and tokenised
  text information.
- `blines`: Produce single BASIC lines from ASCII/Unicode BASIC source that
  may split lines using `detok`'s expanded format.

Additional tools for developers under `bin/` in the source repo include:
- `bddiff`: Use `meld` or another diff tool to show the differences between
  the `basdump` output of two tokenised MS-BASIC programs.
- `msxemu`: Start an OpenMSX emulator instance.

#### cmtconv

[`cmtconv`][cc] converts WAV files of cassette tape saves to `.cas` and
other data file formats, and vice versa. It also understands higher-level
formats such as BASIC and machine-language files. See
[`doc/cmtconv.md`][cc] for full documentation.

The command line programs include:
- `cmtconv`: Conversion program. Use `-h` for help.
- `analyze-cmt`: Analysis of (usually unknown) CMT save formats in WAV files.

#### Other Programs

Additional command-line programs include:
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
[PyPA]: https://packaging.python.org/en/latest/specifications/

<!-- Programs -->
[bt]: ./doc/bastok.md
[cc]: ./doc/cmtconv.md

<!-- Support and Authors -->
[0cjs]: https://github.com/0cjs
[`@cjs_cynic`]: https://t.me/cjs_cynic
[croys]: https://github.com/croys
[discord]: https://discord.com
[telegram]: https://telegram.org
