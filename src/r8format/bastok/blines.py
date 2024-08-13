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
