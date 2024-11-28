Changelog
=========

This file follows most, but not all, of the conventions described at
[keepachangelog.com]. Especially we always use [ISO dates]. Subsections or
notations for changes may include Added, Changed, Deprecated, Fixed,
Removed, and Security.

Release version numbers follow the [Python packaging
specifications][pyver], which are generally consistent with [semantic
versioning][semver]: are _major.minor.patch_ Development versions use the
version number of the _next_ release with _.devN_ appended; `1.2.3.dev4` is
considered to be earlier than `1.2.3`.

On any change to the programs or libraries (not, generally, the tests), the
previous release version number is bumped and `.devN` is appended to it, if
this hasn't already been done. A `.devN` suffix will stay until the next
release, though its _N_ need not be bumped unless the developer feels the
need.

Releases are usually tagged with `vN.N.N`. Potentially not all releases
will be tagged, but specific releases can also be fetched via the Git
commit ID.

For release instructions, see [cynic-net/pypi-release] on GitHub.

### dev
- Changed: `MemImage` now automatically recalculates `startaddr` and
  `endaddr` when a record is added, and these can be overridden afterwards
  by the user.
- Added: `p2b` program to generate generate Apple II "B" type and and KC85
  .CO program files from ASL .p files.

### 0.0.7 (2024-09-22)
- Fixed: `RomImage.patches()` now works if more than one patchspec matches.
- Fixed: `RomImage` now considers `C:…` to be a path instead of a URL,
  for compatibility with Windows file paths.
- Test framework: `Test` accepts `-c` as well as `-C` to do clean build.

### 0.0.6 (2024-07-30)
- Added: A `binary.romimage.RomImage` can now be cleared (set to length 0)
  with loadspec of `--`. This is useful to "disable" a default RomImage.
- Fixed: `binary.romimage` no longer catches `HTTPError` where it tried
  (but failed) to print a message and exit.

### 0.0.5 (2024-07-15)
- Added: `binary.romimage`, a package to download/build/patch ROM images.
- Changed: `binary.tool.asl` produces better messages when failing to parse
  symbol values in ASL listing/map files. (This better exposes an ASL bug.)

### 0.0.4 (2024-07-14)
- (Not released)

### 0.0.3 (2024-04-25)
- Added: missing `pytest_pt` top-level module now present.
  (t8dev and other repos using their own copy now no longer need to do so.)

#### 0.0.2 (2024-04-23)
- Initial release.



<!-------------------------------------------------------------------->
[ISO dates]: https://xkcd.com/1179/
[cynic-net/pypi-release]: https://github.com/cynic-net/pypi-release
[keepachangelog.com]: https://keepachangelog.com/
[pyver]: https://packaging.python.org/en/latest/specifications/version-specifiers/#version-specifiers
[semver]: https://en.wikipedia.org/wiki/Software_versioning#Semantic_versioning
