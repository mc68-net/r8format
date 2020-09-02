import  re

def blines(plines, commentchar='‖'):
    ''' Given a list of "physical" lines `plines` from an expanded BASIC
        file, remove all expanded BASIC comments  and join together plines
        that form a single BASIC line, starting with a line number
        and ending at the next pline that starts with a line number.

        "Expanded" BASIC comments start at `commentchar` and continue to
        EOL; any spaces in front of them `commentchar` are also removed.
    '''
    #   BASIC lines start with a line number followed by a space
    BSTART = re.compile(r'\d+')

    blines = []; bline = []
    for pline in plines:
        pline = pline.strip()
        if BSTART.match(pline):             # start of new BASIC line?
            blines.append(' '.join(bline))  # emit previous BASIC line
            bline = []                      # clear current BASIC line
        cpos = pline.find(commentchar)      # non-BASIC comment?
        if cpos != -1:
            pline = pline[0:cpos].rstrip(' ')# remove it
        if pline == '': continue            # blank lines do not insert space
        bline.append(pline)

    blines.append(' '.join(bline))
    return blines[1:]
