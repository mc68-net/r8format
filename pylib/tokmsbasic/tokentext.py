class TokenText:
    ''' Tokenized BASIC program text. '''

    def __init__(self, text=None):
        self.orig_text = text

    def text(self):
        ''' Return a `bytes` containing the current tokenized text.
            This does not include a leading file type byte.
        '''

    def write_to(self, stream):
        ''' Write the current tokenized text to `stream`, preceeded by an
            $FF file type byte.
        '''
