Sample Programs for bastok
==========================

These programs are used for `bastok` functional tests (in the [top-level
`/Test`](../Test) script) and manual testing. This directory can be read
and written in openMSX by starting it with the `-diska programs` option.

### Test Data

- These are not expected to test every edge case; the unit tests generally
  do that.
- Extra spaces are deliberate; they test that the parser does not remove
  the programmer's formatting (unless required with the `-s` option).

### Line Numbers

The first line is generally `1 'SAVE"..."` to make saving under the right
filename more reliable after a load and edit.

Test data lines are generally numbered from 43250 incrementing by 256;
43520, 43536, 43552, ... in decimal produces the pattern
`00 AA … 10 AA … 20 AA …` in the binary file which is easy to find. ($AA is
relatively rare in tokenised BASIC: it's in the `RENUM` and `CVD` tokens
and is the `こ` character.) The numbering can be done automatically with:

    RENUM 43520,2,16

### Filenames

Filenames are in the format `NNcc-sss.ext` where:
- `NN` is a decimal number. This is used by `Test` to detect the files
  for tests and determines the order in which the tests are run.
- `cc` is the (lower-case) charset to be used for detokenising and retokenising.
- `-` is just for readability.
- `sss` is a name to help humans remember what this file is testing.
  It may be longer (or shorter) than 3 characters, but only the first
  three will be visible in openMSX.¹ Generally it should be lower-case,
  though the emulator will convert this to upper case.
- `ext` is the extension.

Filename extensions encode the following meanings about file contents:
- `*.bas`: ² Tokenised BASIC files as saved by MSX `SAVE "..."`.
- `*.baa`: ² ASCII BASIC files as saved by MSX `SAVE "...",A`
- `*.ba0`: ³ Detokenised BASIC files in non-expanded format.
- `*.ba1`: ³ Detokenised BASIC files in expanded (`detok -e` option) format.
- `*.ba2`: ³ Detokenised BASIC files in expanded format with additional
             (human-supplied) comments and formatting, and alternate forms
             that MSX-BASIC reads but does not generate (e.g., `1.0`
             instead of `1!`). These are optional and tested only when
             they exist.

Files matching `programs/[0-9][0-9]*.bas` are tested within a standard loop
that expects the above formats with the following additional restrictions:
- The `.bas` and `.baa` in fully "squeezed" format, with no unnecessary
  whitespace.
- The `.ba0` is the `detok` (without expansion) of the `.bas`
- The `.ba1` is the `detok --expand` of the `.bas`.
- All of the above files are required except the `.ba2` file; the test to
  tokenise that is skipped if it's not present. (Nothing is detokenised to
  try to produce the `.ba2`, so this may have any extra formatting and
  comments in it you like.

Notes:
- ¹ The emulator will truncate long filenames to make them fit the MSX 8.3
  filename format. If filenames collide in the (case-insensitive) first
  eight characters of the filename _and_ the first three characters of the
  extension, all but the first file will be ignored by the emulator.
- ² `.bas` and `.baa` files use MSX-BASIC encoding the MSX character set of
  the system that saved them (`int`, `ja`, etc.). `.baa` uses CR-LF line
  endings and have a ^Z as the last character of the file.
- ³ `.ba[012]` files use UTF-8 encoding of Unicode and Unix LF line endings,
  with an LF as the last character of the file.
