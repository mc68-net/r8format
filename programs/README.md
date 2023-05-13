Sample Programs for bastok
==========================

These programs are used for `bastok` functional tests (in the [top-level
`/Test`](../Test) script) and manual testing. This directory can be read
and written in openMSX by starting it with the `-diska programs` option.

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
             (human-supplied) comments and formatting.

For the functional tests, the `*.ba2` file is optional (the test for it
will be skipped if not present); all others are required.

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
