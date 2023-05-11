Sample Programs for bastok
==========================

These programs are used for `bastok` functional tests (in the [top-level
`/Test`](../Test) script) and manual testing. This directory can be read
and written in openMSX by starting it with the `-diska programs` option.

File names are always in 8.3 format¹ and lower case.
- Always stick to 8.3 format; use lower-case.
- `*.bas`: ² Tokenised BASIC files as saved by MSX `SAVE "..."`.
- `*.baa`: ² ASCII BASIC files as saved by MSX `SAVE "...",A`
- `*.ba0`: ³ Detokenised BASIC files in non-expanded format.
- `*.ba1`: ³ Detokenised BASIC files in expanded (`detok -e` option) format.
- `*.ba2`: ³ Detokenised BASIC files in expanded format with additional
             (human-supplied) comments and formatting.

Notes:
- ¹ The emulator will truncate long filenames to make them fit the MSX 8.3
  filename format. If filenames collide after truncation, all but the first
  will be ignored by the emulator.
- ² `.bas` and `.baa` files use MSX-BASIC encoding the MSX character set of
  the system that saved them (`int`, `ja`, etc.). `.baa` uses CR-LF line
  endings and have a ^Z as the last character of the file.
- ³ `.ba[012]` files use UTF-8 encoding of Unicode and Unix LF line endings,
  with an LF as the last character of the file.
