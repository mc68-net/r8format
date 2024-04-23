How to Release r8format
=======================

These are the instructions for building a new release of r8format and
uploading it to PyPI. This is of interest only to r8format developers;
users of r8format can safely ignore this.

XXX: Some of this should be scripted.

Release Process
---------------

1. Update the following files:
   - `pytest.toml`: Remove the `.devN` suffix from the version number.
     (Lack of a `.devN` suffix indicates that a developer didn't add it
     when making a releasable change; in this case just bump the version
     number.)
   - `doc/CHANGELOG.md`: Rename the 'dev' section to the new version number
     and date of release, and add a new (empty) 'dev' section to the top of
     the list of releases.
   - Commit these changes, but do not push them to `main` yet. Probably the
     commit should not include any other changes, and the message can be
     just 'Release 0.x.x'.

2. Build and check the release.
   - Change the current working directory to the project root.
   - Activate the virtualenv: `source .build/virtalenv/bin/activate`.
   - `pip install build twine`.
   - `rm -f dist/*`
   - `pyproject-build`.
   - `twine check dist/*`
   - Fix anything broken.

3. Do the release
   - `git tag v0.x.x`
   - `git push main tag v0.x.x`
   - `twine upload dist/*` (ensure you have your API token handy)
