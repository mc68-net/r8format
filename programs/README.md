Sample Programs for bastok
==========================

This directory can be directly accessed from openMSX by starting it
with the `-diska programs` option.

The emulator will truncate filenames to make them fit the MSX 8.3 filename
format, but if filenames collide after truncation, all but the first will
be ignored by the emulator.

Therefore we attempt to stick to the 8.3 format here. The naming
conventions are:
- `*.BAS`: Tokenised BASIC files.
- `*.BA0`: Detokenised BASIC files in non-expanded format.
- `*.BA1`: Detokenised BASIC files in expanded (`detok -e` option) format.
