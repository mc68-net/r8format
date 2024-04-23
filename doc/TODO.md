r8format TODO List
==================

High priority:
- `psrc/pytest_pt.py` is not included in the built package (the wheel), and
  thus users of t8dev must still use a Git submodule. This probably wants
  to be moved down into one of the packages (though none of `binary`,
  `cmtconv` and `bastok` seem obviously suitable) to avoid polluting the
  top-level namespace. Perhaps the name is unique enough that we should
  leave it at the top level and figure out some way for it to be included
  in the package?
- Document in the README the top-level import packages in this distribution
  package. (Currently only the bin/* files are documented.)

Low priority:
- Consider whether the command-line programs should have a `--version`
  option. If we do this, we need somehow to synchronise the version between
  `pyproject.toml` and the programs.
