Reverse Engineering of MS-BASIC
===============================

The following notes are based on:
- MSX ROM reverse engineering ([Git repo][syssrc]) `base200/bintrp.mac`
- MS BASIC-80 5.2 source code, `BINTRP.MAC`

### Basic Tokenizer

Variables:
- $F41F `KBUFMIN`, `KBUF`: tokenised code buffer
- $F55D `BUFMIN`: ¿end of tokenised code buffer?
- $F665 `DONUM`: number tokenisation: 1=lineno , 0=standard, -1=ASCII
- $F664 `DORES` "not in DATA statement";
  0="crunch reserved words", 1="in DATA stmt"

Routines:

- `CRUNCH`/`C42B2` "encode BASIC line":
  entry point, HL = input line to tokenise
  - init `DONUM` ← 0, `DORES` ← 0
  - call `H.CRUN` hook
  - BC ← 315₁₀ (buflen?), DE ← `KBUF`
  - (HL)==0 || jr `J42D9` to start next round of parse
  - otherwise at EOL and finish up

- `J42D9`: round of parsing
  - `"` && jp `STRNG`/`J4316`
           ;  put into KBUF `"` and all chars that follow until next `"` or EOL
  - ` ` && jr `STUFFH`/`J42E9` ; put in KBUF and continue
  - `DORES`? ("in DATA stmt?") || jr `J4326` ; "no, normal behaviour"
  - DATA parsing, presumably
  - `J4326`

- `J4326`: "normal" behaviour, not in DATA statement

- `KRNSVC`/,`C44DE`: Save `:` to KBUF
- `KRNSAV`/`C44E0`: Save char in A to KBUF, w/check for overflow (err code 25)

DORES,DONUM handling:
- `CRUNCH`: both ← 0
  - `J42F3`/`J4301`: on DATA token, both ← 1
- J42D9: in string; ignore both (STRNG ignores values of both)
- J42F3: both ← 0 whenver we encounter a `:` (not in string or rem)
- `TRYAGA`/`J4365` keyword matching loop: when matches keyword that is a
  function token (`AND`, `ABS`, etc.), DONUM ← 0
- `J43AB`: checks for tokens taking lineno as operand (`GOTO` etc.):
  - yes: `J43C6`: DONUM ← 1
  - no:  `J43C4`: DONUM ← 0
- `J441D`: start parse of non-letter; `J442C` parse number: reads DONUM
  to determine how it parses.
- `KRNSAV` saves byte to KBUF: doesn't touch it
- `J44A2`: not-letter and not-number check: both ← unchanged
- `J44EB`: is-letter and not-keyword routine: always entered with A=0, so
  DEC A gives DONUM ← -1. Space chars never reach this as they were handled
  at the very start of parsing.
- `J44FA`: replace most ctrl chars w/space
  (called from parse not-letter not-number; includes e.g. `,`)
  - `J4509`: if DONUM = -1, set to 0, otherwise retain DONUM value

DONE:
- list of all ~14 tokens with line number as operand: RESTORE AUTO RENUM
  DELETE RESUME ERL ELSE RUN LIST LLIST GOTO RETURN THEN GOSUB
- support for `?` → PRINT but not `_` → CALL (that's 5.x only, not MSX)

TODO:
- Replace ctrl chars w/space excepting TAB and LF
- chars that need to be converted to upper case (beacuse outside of str/rem?)
- consider that `TIME` variable is a tokenised keyword, not same as `TI`
- DONUM handling like MS-BASIC


<!-------------------------------------------------------------------->
[syssrc]: https://git.code.sf.net/p/msxsyssrc/git
