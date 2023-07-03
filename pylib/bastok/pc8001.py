#
# Tokens dumped from N-BASIC v1.1 ROM using `dump-tokens`
#

TOKENS_FROM_ROM = (
                                            # ALPTAB at 0x34C1
                                            # addr=$34F5 'A' table
    (b'\xF8',           'AND',          ),  # addr=$34F5
    (b'\xFF\x86',       'ABS',          ),  # addr=$34F8
    (b'\xFF\x8E',       'ATN',          ),  # addr=$34FB
    (b'\xFF\x95',       'ASC',          ),  # addr=$34FE
    (b'\xA9',           'AUTO',         ),  # addr=$3501
    (b'\xE7',           'ATTR$',        ),  # addr=$3505
                                            # addr=$350B 'B' table
    (b'\xFF\x9E',       'BCD$',         ),  # addr=$350B
    (b'\xB2',           'BEEP',         ),  # addr=$350F
                                            # addr=$3514 'C' table
    (b'\x9F',           'CONSOLE',      ),  # addr=$3514
    (b'\xCA',           'CLOSE',        ),  # addr=$351B
    (b'\x99',           'CONT',         ),  # addr=$3520
    (b'\x92',           'CLEAR',        ),  # addr=$3524
    (b'\x9B',           'CLOAD',        ),  # addr=$3529
    (b'\x9A',           'CSAVE',        ),  # addr=$352E
    (b'\xE6',           'CSRLIN',       ),  # addr=$3533
    (b'\xFF\x9F',       'CINT',         ),  # addr=$3539
    (b'\xFF\xA0',       'CSNG',         ),  # addr=$353D
    (b'\xFF\xA1',       'CDBL',         ),  # addr=$3541
    (b'\xFF\xA3',       'CVI',          ),  # addr=$3545
    (b'\xFF\xA4',       'CVS',          ),  # addr=$3548
    (b'\xFF\xA5',       'CVD',          ),  # addr=$354B
    (b'\xFF\x8C',       'COS',          ),  # addr=$354E
    (b'\xFF\x96',       'CHR$',         ),  # addr=$3551
    (b'\xB8',           'CMD',          ),  # addr=$3555
    (b'\xB5',           'COLOR',        ),  # addr=$3558
                                            # addr=$355E 'D' table
    (b'\x84',           'DATA',         ),  # addr=$355E
    (b'\x86',           'DIM',          ),  # addr=$3562
    (b'\xAB',           'DEFSTR',       ),  # addr=$3565
    (b'\xAC',           'DEFINT',       ),  # addr=$356B
    (b'\xAD',           'DEFSNG',       ),  # addr=$3571
    (b'\xAE',           'DEFDBL',       ),  # addr=$3577
    (b'\xC2',           'DSKO$',        ),  # addr=$357D
    (b'\x97',           'DEF',          ),  # addr=$3582
    (b'\xA8',           'DELETE',       ),  # addr=$3585
    (b'\xE8',           'DSKI$',        ),  # addr=$358B
    (b'\xFF\xA6',       'DSKF',         ),  # addr=$3590
    (b'\xFF\x9D',       'DEC',          ),  # addr=$3594
    (b'\xEB',           'DATE$',        ),  # addr=$3597
                                            # addr=$359D 'E' table
    (b'\x81',           'END',          ),  # addr=$359D
    (b'\xA1',           'ELSE',         ),  # addr=$35A0
    (b'\xA5',           'ERASE',        ),  # addr=$35A4
    (b'\xA6',           'ERROR',        ),  # addr=$35A9
    (b'\xDF',           'ERL',          ),  # addr=$35AE
    (b'\xE0',           'ERR',          ),  # addr=$35B1
    (b'\xFF\x8B',       'EXP',          ),  # addr=$35B4
    (b'\xFF\xA7',       'EOF',          ),  # addr=$35B7
    (b'\xFB',           'EQV',          ),  # addr=$35BA
                                            # addr=$35BE 'F' table
    (b'\xB3',           'FORMAT',       ),  # addr=$35BE
    (b'\x82',           'FOR',          ),  # addr=$35C4
    (b'\xC6',           'FIELD',        ),  # addr=$35C7
    (b'\xCD',           'FILES',        ),  # addr=$35CC
    (b'\xDC',           'FN',           ),  # addr=$35D1
    (b'\xFF\x8F',       'FRE',          ),  # addr=$35D3
    (b'\xFF\xA2',       'FIX',          ),  # addr=$35D6
    (b'\xFF\xAA',       'FPOS',         ),  # addr=$35D9
                                            # addr=$35DE 'G' table
    (b'\x89',           'GOTO',         ),  # addr=$35DE
    (b'\x89',           'GO TO',        ),  # addr=$35E2
    (b'\x8D',           'GOSUB',        ),  # addr=$35E7
    (b'\xC7',           'GET',          ),  # addr=$35EC
                                            # addr=$35F0 'H' table
    (b'\xFF\x9A',       'HEX$',         ),  # addr=$35F0
                                            # addr=$35F5 'I' table
    (b'\x85',           'INPUT',        ),  # addr=$35F5
    (b'\x8B',           'IF',           ),  # addr=$35FA
    (b'\xE3',           'INSTR',        ),  # addr=$35FC
    (b'\xFF\x85',       'INT',          ),  # addr=$3601
    (b'\xFF\x90',       'INP',          ),  # addr=$3604
    (b'\xFC',           'IMP',          ),  # addr=$3607
    (b'\xD4',           'INIT',         ),  # addr=$360A
    (b'\xE9',           'INKEY$',       ),  # addr=$360E
    (b'\xBD',           'ISET',         ),  # addr=$3614
    (b'\xBE',           'IRESET',       ),  # addr=$3618
    (b'\xFF\xEC',       'IEEE',         ),  # addr=$361E
                                            # addr=$3623 'J' table
                                            # addr=$3624 'K' table
    (b'\xCF',           'KILL',         ),  # addr=$3624
    (b'\xB4',           'KEY',          ),  # addr=$3628
                                            # addr=$362C 'L' table
    (b'\x88',           'LET',          ),  # addr=$362C
    (b'\xD5',           'LOCATE',       ),  # addr=$362F
    (b'\xAF',           'LINE',         ),  # addr=$3635
    (b'\xCB',           'LOAD',         ),  # addr=$3639
    (b'\xD0',           'LSET',         ),  # addr=$363D
    (b'\x9D',           'LPRINT',       ),  # addr=$3641
    (b'\x9E',           'LLIST',        ),  # addr=$3647
    (b'\xFF\x9B',       'LPOS',         ),  # addr=$364C
    (b'\xC1',           'LISTEN',       ),  # addr=$3650
    (b'\x93',           'LIST',         ),  # addr=$3656
    (b'\xD3',           'LFILES',       ),  # addr=$365A
    (b'\xFF\x8A',       'LOG',          ),  # addr=$3660
    (b'\xFF\xA8',       'LOC',          ),  # addr=$3663
    (b'\xFF\x92',       'LEN',          ),  # addr=$3666
    (b'\xFF\x81',       'LEFT$',        ),  # addr=$3669
    (b'\xFF\xA9',       'LOF',          ),  # addr=$366E
                                            # addr=$3672 'M' table
    (b'\xC4',           'MOUNT',        ),  # addr=$3672
    (b'\xCC',           'MERGE',        ),  # addr=$3677
    (b'\xFD',           'MOD',          ),  # addr=$367C
    (b'\xFF\xAB',       'MKI$',         ),  # addr=$367F
    (b'\xFF\xAC',       'MKS$',         ),  # addr=$3683
    (b'\xFF\xAD',       'MKD$',         ),  # addr=$3687
    (b'\xFF\x83',       'MID$',         ),  # addr=$368B
    (b'\xB9',           'MOTOR',        ),  # addr=$368F
    (b'\xB7',           'MON',          ),  # addr=$3694
    (b'\xC0',           'MAT',          ),  # addr=$3697
                                            # addr=$369B 'N' table
    (b'\x83',           'NEXT',         ),  # addr=$369B
    (b'\xCE',           'NAME',         ),  # addr=$369F
    (b'\x94',           'NEW',          ),  # addr=$36A3
    (b'\xDE',           'NOT',          ),  # addr=$36A6
                                            # addr=$36AA 'O' table
    (b'\x9C',           'OUT',          ),  # addr=$36AA
    (b'\x95',           'ON',           ),  # addr=$36AD
    (b'\xC5',           'OPEN',         ),  # addr=$36AF
    (b'\xF9',           'OR',           ),  # addr=$36B3
    (b'\xFF\x99',       'OCT$',         ),  # addr=$36B5
                                            # addr=$36BA 'P' table
    (b'\xC8',           'PUT',          ),  # addr=$36BA
    (b'\x98',           'POKE',         ),  # addr=$36BD
    (b'\x91',           'PRINT',        ),  # addr=$36C1
    (b'\xFF\x91',       'POS',          ),  # addr=$36C6
    (b'\xFF\x97',       'PEEK',         ),  # addr=$36C9
    (b'\xFF\x9C',       'PORT',         ),  # addr=$36CD
    (b'\xBA',           'POLL',         ),  # addr=$36D1
    (b'\xB1',           'PSET',         ),  # addr=$36D5
    (b'\xB0',           'PRESET',       ),  # addr=$36D9
    (b'\xEF',           'POINT',        ),  # addr=$36DF
                                            # addr=$36E5 'Q' table
                                            # addr=$36E6 'R' table
    (b'\x87',           'READ',         ),  # addr=$36E6
    (b'\x8A',           'RUN',          ),  # addr=$36EA
    (b'\x8C',           'RESTORE',      ),  # addr=$36ED
    (b'\x8E',           'RETURN',       ),  # addr=$36F4
    (b'\xC3',           'REMOVE',       ),  # addr=$36FA
    (b'\x8F',           'REM',          ),  # addr=$3700
    (b'\xA7',           'RESUME',       ),  # addr=$3703
    (b'\xD1',           'RSET',         ),  # addr=$3709
    (b'\xFF\x82',       'RIGHT$',       ),  # addr=$370D
    (b'\xFF\x88',       'RND',          ),  # addr=$3713
    (b'\xAA',           'RENUM',        ),  # addr=$3716
    (b'\xBB',           'RBYTE',        ),  # addr=$371B
                                            # addr=$3721 'S' table
    (b'\x90',           'STOP',         ),  # addr=$3721
    (b'\xA4',           'SWAP',         ),  # addr=$3725
    (b'\xC9',           'SET',          ),  # addr=$3729
    (b'\xD2',           'SAVE',         ),  # addr=$372C
    (b'\xDD',           'SPC(',         ),  # addr=$3730
    (b'\xDA',           'STEP',         ),  # addr=$3734
    (b'\xFF\x84',       'SGN',          ),  # addr=$3738
    (b'\xFF\x87',       'SQR',          ),  # addr=$373B
    (b'\xFF\x89',       'SIN',          ),  # addr=$373E
    (b'\xFF\x93',       'STR$',         ),  # addr=$3741
    (b'\xE1',           'STRING$',      ),  # addr=$3745
    (b'\xFF\x98',       'SPACE$',       ),  # addr=$374C
    (b'\xEE',           'STATUS',       ),  # addr=$3752
    (b'\xED',           'SRQ',          ),  # addr=$3758
                                            # addr=$375C 'T' table
    (b'\xA2',           'TRON',         ),  # addr=$375C
    (b'\xA3',           'TROFF',        ),  # addr=$3760
    (b'\xD9',           'TAB(',         ),  # addr=$3765
    (b'\xD7',           'TO',           ),  # addr=$3769
    (b'\xD8',           'THEN',         ),  # addr=$376B
    (b'\xFF\x8D',       'TAN',          ),  # addr=$376F
    (b'\xB6',           'TERM',         ),  # addr=$3772
    (b'\xBF',           'TALK',         ),  # addr=$3776
    (b'\xEA',           'TIME$',        ),  # addr=$377A
                                            # addr=$3780 'U' table
    (b'\xE2',           'USING',        ),  # addr=$3780
    (b'\xDB',           'USR',          ),  # addr=$3785
                                            # addr=$3789 'V' table
    (b'\xFF\x94',       'VAL',          ),  # addr=$3789
    (b'\xE5',           'VARPTR',       ),  # addr=$378C
                                            # addr=$3793 'W' table
    (b'\xA0',           'WIDTH',        ),  # addr=$3793
    (b'\x96',           'WAIT',         ),  # addr=$3798
    (b'\xBC',           'WBYTE',        ),  # addr=$379C
                                            # addr=$37A2 'X' table
    (b'\xFA',           'XOR',          ),  # addr=$37A2
                                            # addr=$37A6 'Y' table
                                            # addr=$37A7 'Z' table

)


#
# Tokens not in ROM tables
#
TOKENS_EXTRA = (
    (b':\x8F\xE4',      "'",            ),
    (b':\xA1',          "ELSE",         ),
    
    (b'\xF0',           '>',            ),
    (b'\xF1',           '=',            ),
    (b'\xF2',           '<',            ),
    (b'\xF3',           '+',            ),
    (b'\xF4',           '-',            ),
    (b'\xF5',           '*',            ),
    (b'\xF6',           '/',            ),
    (b'\xF7',           '^',            ),
)

TOKENS=tuple(x for x in TOKENS_FROM_ROM if x[1] != "ELSE") + TOKENS_EXTRA
#TOKENS=tuple(filter(lambda x: (x[1] != "ELSE"), TOKENS_FROM_ROM)) + TOKENS_EXTRA


#
# Manual invesigation
#

#
# A table of BASIC tokens can be found on pages 95 and 96 of
# "パソコンPCシリーズ 8001 6001 ハンドブック"
# by 朝日新聞電気計算器室編, 1982
#
# available at https://archive.org/details/PC8001600100160011982
#

# N-BASIC
#
# N-BASIC レファレンス　カード
#    https://archive.org/details/NBASICRefcard

# N80-BASIC
#
# PC-8001MKII N80-BASIC Reference Manual
#   https://archive.org/details/PC-8001mk-II-n-80-basic-reference-manual

#
# The following BASIC program was run on real h/w to
# determine the token values:
#
#


TOKENS_MANUAL = (
    (b'\xA9',       'AUTO',         ),
    (b'\x9B',       'CLOAD',        ),
    (b'\x99',       'CONT',         ),
    (b'\x9A',       'CSAVE',        ),
    (b'\xA8',       'DELETE',       ),
    (b'\xCD',       'FILES',        ), # d
    (b'\xB3',       'FORMAT',       ), # m
    (b'\x93',       "KEYLIST"       ), # m
    (b'\xD3',       'LFILES',       ), # d
    (b'\x93',       'LIST',         ),
    (b'\x9E',       'LLIST',        ),
    (b'\xCB',       'LOAD',         ), # d
    (b'\xCC',       'MERGE',        ), # d
    (b'\xB7',       'MON',          ), # m
    (b'\xC4',       'MOUNT',        ), # m
    (b'\xCE',       'NAME',         ), # d
    (b'\x94',       'NEW',          ),
    (b'\xAA',       'RENUM',        ),
    (b'\x3A',       'REMOVE',       ), # m
    (b'\x8A',       'RUN',          ),
    (b'\xD2',       'SAVE',         ), # d
    (b'\xC9',       'SET',          ), # d
    (b'\xB6',       'TERM',         ), # m

    (b'\x92',       'CLEAR',        ),
    (b'\x84',       'DATA',         ),
    (b'\x97',       'DEF',          ),
    (b'\xDC',       'FN',           ), # d
    (b'\xDB',       'USR',          ), # d
    (b'\xAE',       'DEFDBL',       ),
    (b'\xAC',       'DEFINT',       ),
    (b'\xAD',       'DEFSNG',       ),
    (b'\xAB',       'DEFSTR',       ),
    (b'\x86',       'DIM',          ),
    (b'\x81',       'END',          ),
    (b'\xA5',       'ERASE',        ),
    (b'\xC6',       'FIELD',        ), # d
    (b'\x82',       'FOR',          ),
    (b'\x8D',       'GOSUB',        ),
    (b'\x89',       'GOTO',         ),
    (b'\x8B',       'IF',           ),
    (b'\x88',       'LET',          ),
    (b'\xD0',       'LSET',         ), # d
    (b'\x83',       'NEXT',         ),
    (b'\x95',       'ON',           ),
    (b'\x87',       'READ',         ),
    (b'\x8F',       'REM',          ),
    (b'\x8C',       'RESTORE',      ),
    (b'\x8E',       'RETURN',       ),
    (b'\xD1',       'RSET',         ), # d
    (b'\x90',       'STOP',         ),
    (b'\xA4',       'SWAP',         ),

    (b'\x3A\xA1',   'ELSE',         ),
)


# FIXME: Need to deal with multiple BASIC versions per platform
# Most likely by separate platform/module - e.g. pc8001_n80