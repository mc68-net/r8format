from    pathlib  import Path

def pylib(*components):
    ''' XXX test data files
    '''
    return Path(__file__).parent.parent.joinpath(*components)
