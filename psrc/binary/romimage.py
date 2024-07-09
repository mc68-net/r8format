''' Download and build ROM images.

    This package is designed for use by programs reading command line
    parameters or configuration files specifying how to set up ROM image
    files for emulators or other purposes. It can use existing ROM images
    from files or downloaded from URLs (with optional caching of the
    downloads) and move the data and combine it with other data before
    producing the file ROM file output.

    Generally you will create an initial `RomImage` from an exising file
    containing the ROM data, possibly offset from the original source,
    optionally use `patches()` to apply the relevant patches from a
    sequence of *patchspecs,* and then use `writefile()` or `writefd()` to
    write out the image.
'''

from    pathlib  import Path
from    urllib.request  import HTTPError, urlopen
from    urllib.parse  import urlparse
import  re

class RomImage:
    ''' A `RomImage` is a sequence of bytes always starting at address
        $0000. (That is the first address in the *ROM,* these are not
        necessarily the addresses to which the ROM is mapped in the
        system's memory, if indeed it is mapped into the CPU's address
        space at all.)

        Each RomImage has an optional *loadspec* for loading the initial
        data, and may be patched with additional *patchspecs* that load
        further data.

        A loadspec is a path or URL, called a *source*, optionally prefixed
        by ``@hhhh:`` where *hhhh* is any number of hexadecimal digits
        specifying an offset in this ROM image at which to load the source.

        A patchspec is a loadspec prefixed by ``name=`` where *name*
        matches the name assigned to this RomImage at instantiation, as
        determined by the `matchname()` function. Patches will overwrite
        the existing RomImage data only from the patchspec's start address
        to the length of the retrieved data.
    '''

    def __init__(self, name, cachedir, loadspec=None):
        ''' Create a new `RomImage` named `name`, optionally loading
            `loadspec` into the image.

            If `cachedir` is `None` any URLs given to `load()` or similar
            will always be fetched. Otherwise `cachedir` must be a
            path-like object in which local copies of the downloaded URLs
            will be stored to be read the next time the same URL is
            encountered. (The subdirectories under this will be generated
            with `cache_file(url)`)
        '''
        self.name       = name
        if cachedir is None:    self.cachedir = None
        else:                   self.cachedir = Path(cachedir)
        self.image      = bytearray()
        if loadspec is not None:
            self.load(*self.parse_loadspec(loadspec))

    LOADSPEC = re.compile(r'(@[0-9A-Fa-f]+:)?(.*)')
    SCHEME   = re.compile(r'^[A-Za-z][A-Za-z0-9+.-]*:')

    @staticmethod
    def parse_loadspec(loadspec):
        ''' Given a `loadspec` in the format ``[@hhhh:]path-or-URL``, return
            the startaddr (hex digits _hhhh_ above; $0000 if not present)
            and the path or URL.

            This never fails, though it may return an odd "path" if you
            e.g. include a non-hex-digit in the ``@hhhh:`` part.
        '''
        addr, rhs = RomImage.LOADSPEC.fullmatch(loadspec).group(1, 2)
        if addr:
            return (int(addr[1:-1], 16), rhs)
        else:
            return (0, rhs)

    def cache_file(self, url, mkdir=True):
        ''' Given a URL return a (hopefully) unique filesystem path in which
            to cache the downloaded ROM image.

            There are two instances that can cause collisions that we
            (currently) don't deal with:

            1. We remove any leading and trailing slashes to avoid "blank"
               path components, but this also strips information about
               whether it was a relative or absolute path, which can create
               collisions.

            2. We entirely ignore any URL parameters, and so collide if we
               are downloading something such as ``/rom/foo?ver=1.1``
               versus ``ver=1.2``.

            Both of these problems We ignore for the moment because they
            are difficult to handle and relatively unlikely and hard to
            handle.
        '''
        u = urlparse(url)
        c = [u.scheme, u.hostname ]
        if u.port: c.append(u.port)
        c += u.path.strip('/').split('/')
        p = self.cachedir.joinpath(*c)
        if mkdir:  p.parent.mkdir(exist_ok=True, parents=True)
        return p

    def set_image(self, offset, bs):
        ' Set our in-memory image bytes starting at `offset` to bytes `bs`. '
        if offset > len(self.image):
            self.image += b'\x00' * (offset - len(self.image))
        self.image[offset:offset+len(bs)] = bs

    def writefile(self, path):
        ' Write this binary image to the given filename. '
        with open(path, 'wb') as f:  self.writefd(f)

    def writefd(self, fd):
        ' Write this binary image to the given file descriptor. '
        fd.write(self.image)

    def readfile(self, startaddr, path):
        with open(path, 'rb') as f:  self.set_image(startaddr, f.read())

    def load(self, offset, source):
        ''' Load the data from `source` (a URL or path) into this RomImage,
            at offset `offset`.
        '''
        if not self.SCHEME.match(str(source)):      # is path to a file?
            self.readfile(offset, source)
            return

        if self.cachedir:
            cf = self.cache_file(source)
            if cf.exists():
                self.readfile(offset, cf)
                return

        try:
            with urlopen(source) as response:
                romdata = response.read()
                self.set_image(offset, romdata)
        except HTTPError as ex:
            err(f'{ex} for {source!r}')
        if self.cachedir:
            with open(cf, 'wb') as f: f.write(romdata)

    def matchname(self, name):
        ''' Return `True` if `name` matches this RomImage's name. The the
            match is case-insensitive and the patchspec name need not
            include the file extension, so e.g. ``n80=...`` will match a
            RomImage named ``N80.ROM``.
        '''
        r = self.name.lower()
        return r == name.lower() or r.rsplit('.', 1)[0] == name.lower()

    def matchpatchspec(self, patchspec):
        if not '=' in  patchspec:  return False
        name, _ = patchspec.split('=', 1)
        return self.matchname(name)

    def patches(self, patchspecs):
        ''' This takes a sequence of *patchspecs* in the format
            ``name=[@hhhh:]source`` and applies them to this ROM image. Any
            patchspecs that are applied are removed from the sequence; any
            that don't match this RomImage's name are ignored.
        '''
        matches = [ i for i in range(len(patchspecs))
                      if self.matchpatchspec(patchspecs[i]) ]
        for i in matches:
            name, loadspec = patchspecs.pop(i).split('=', 1)
            self.load(*self.parse_loadspec(loadspec))
