import  re

def blines(plines, commentchar='‖'):
    ''' Given a list of "physical" lines `plines` from an expanded BASIC
        file, remove all expanded BASIC comments  and join together plines,
        ignoring leading and trailing spaces, that form a single BASIC
        line.

        "Expanded" BASIC comments start at `commentchar` and continue to
        EOL; any spaces in front of them `commentchar` are also removed.

        A pline is considered to start a BASIC line if it starts with a
        decimal number that is followed at least one non-numeric character
        that is not a comma. This allows for continuation lines for DATA
        statements of numeric values, e.g., `DATA 12,` followed by `34` or
        `34, 56`.
    '''

    #   BASIC lines start with a line number followed by a space
    BSTART = re.compile(r'\d+[^,\d]+')

    blines = []; bline = []
    for pline in plines:
        pline = pline.strip()
        if BSTART.match(pline):             # start of new BASIC line?
            blines.append(' '.join(bline))  # emit previous BASIC line
            bline = []                      # clear current BASIC line
        cpos = pline.find(commentchar)      # non-BASIC comment?
        if cpos != -1:
            pline = pline[0:cpos].rstrip()  # remove it
        if pline == '': continue            # blank lines do not insert space
        bline.append(pline)

    blines.append(' '.join(bline))
    return blines[1:]

def stripeol(lines):
    ''' Given a sequence of binary sequences (`bytes` or anything else that
        supports `fromhex()`), each representing a line, return a copy with
        any CR, LF, or CR LF terminators removed from the line ends. If
        the last line is a ^Z (0x1A) alone on the line, which is the CP/M
        and DOS text file terminator, that entire line will be removed.

        It may be possible that with some CP/M saves the EOF terminator
        could be many ^Z characters, filling out the last block, but we've
        not seen that yet, so wait until we do to see if and how it
        actually happens.
    '''
    if len(lines) == 0:
        return []

    LF  = ord(type(lines[0]).fromhex('0A'))
    CR  = ord(type(lines[0]).fromhex('0D'))
    EOF =     type(lines[0]).fromhex('1A')

    res = []
    for l in lines:
        if len(l) > 0 and l[-1] == LF:   l = l[0:-1]
        if len(l) > 0 and l[-1] == CR:   l = l[0:-1]
        res.append(l)
    if res[-1] == EOF:
        res = res[0:-1]
    return res
