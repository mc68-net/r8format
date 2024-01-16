''' Pytest plugin to find/execute .pt files as tests

    This plugin adds a new collection hook that recognizes files
    ending in ``.pt`` and loads them as test files. The ``python_files``
    `configuration option`_ need not be changed to include ``*.pt``.

    This will work only in Python ≥3.5 because it uses new importlib
    routines. Further, it does not (as traditional pytest did) change
    the import path per ``--import-mode`` to add the directory in
    which the file resides, since this was needed only with the older
    import routines and caused its own set of problems. If you are
    importing from paths that were automatically added, you will need
    to change your test framework configuration to explicitly add the
    necessary paths.

    The module name for file ``foo.pt`` will be ``foo_pt``. This is
    done only to make test framework debugging easier; since these
    modules are not added to `sys.modules`, there should be no problem
    with collisions as there is in standard pytest loading system,
    which is not yet able to use the ``py`` package's
    ``ensuresyspath='importlib'`` option on `pyimport()`.

    Filename collisions in ``__pycache__/`` between pytest-compiled
    and standard-compiled files are not an issue (pytest appends
    ``-pytest-M.N.P.pyc`` to the bytecode filename) but collisions can
    happen if you create both ``foo.pt`` and ``foo_pt.py`` files and
    ask pytest to run both as tests, so don't do that.

    .. _configuration option: https://docs.pytest.org/en/latest/reference.html#hook-reference

    This code is dedicated to the public domain under CC0.
    http://creativecommons.org/publicdomain/zero/1.0/legalcode
'''

import  contextlib, sys
import  importlib, importlib.machinery
from    importlib.util  import spec_from_file_location
import  pytest, _pytest
from    _pytest.assertion.rewrite import assertstate_key

#   Typing imports
from    pathlib  import Path
from    typing  import Optional
from    _pytest.config  import Config
from    _pytest.nodes  import Collector

#   We have to do some version-specific imports depending on which version
#   of pytest we're running. We can't use `pytest.version_tuple` because
#   that doesn't exist in pytest 5, so we just hack the version string.
#   Note that we also do further version-specific assignments at the
#   end of this file.
ptver = int(pytest.__version__.split('.')[0])
if ptver == 5:
    from    py._path.local import LocalPath
elif ptver == 7:
    from    _pytest  import nodes
    from    _pytest.pathlib  import module_name_from_path, insert_missing_modules

####################################################################
#   pytest 5.x

PYTEST_CONFIG = None

def pt5_pytest_configure(config):
    ''' Cache a copy of the pytest configuration.

        The configuration is needed by our collect_file hook to get a
        reference to pytest's special assertion-rewriting loader, if
        we're using it.
    '''
    global PYTEST_CONFIG
    PYTEST_CONFIG = config

def pt5_pyimport(self, modname=None, ensuresyspath=True):
    ''' This replaces the pyimport() method on an instance of
        LocalPath. This version loads modules from files that the
        standard loading mechanim doesn't recognize as containing
        pytest (or even Python) code. It also tweaks the module name
        appropriately.

        Replace `pyimport()` in an instance ``lp`` with
        ``lp.pyimport = pt5_pyimport.__get__(lp, LocalPath)``.
    '''

    #   Here we add `_pt` just to help with test framework debugging.
    #   There won't be any collisions in `sys.modules` becuase we
    #   never add the modules we load to it.
    modname = self.purebasename + '_pt'
    path = str(self)

    #   If we are configured to use the assertion-rewriting loader
    #   (_pytest.assertion.rewrite.AssertionRewritingHook), use that
    #   to load the test code. Otherwise use the standard Python loader.
    loader = None
    assertstate = PYTEST_CONFIG._store.get(assertstate_key, None)
    if assertstate:
        loader = PYTEST_CONFIG._store[assertstate_key].hook
    if loader is None:
        loader = importlib.machinery.SourceFileLoader(modname, path)

    spec = spec_from_file_location(modname, path, loader=loader)
    if spec is None:
        #   This should never happen; if it does most likely we mucked up
        #   our loader setup or something like that.
        raise ImportError(
            "Can't create spec for module %s at location %s" % (modname, path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def pt5_pytest_collect_file(path, parent):
    #   We handle only files with our custom extension, otherwise we
    #   return `None` to let something else handle it (or not).
    if path.ext != '.pt':
        return None

    #   Replace this LocalPath's `pyimport()` with our custom code.
    path.pyimport = pt5_pyimport.__get__(path, LocalPath)

    #   Continue collection exactly as pytest normally does.
    ihook = parent.session.gethookproxy(path)
    return pytest.Module.from_parent(parent, fspath=path)

####################################################################
#   pytest 7.x

'''
    pytest 7 offers the `pytest_pycollect_makemodule()` hook_, but we can't
    just use this because the `_pytest.python.pytest_collect_file()`
    function that calls the hook ignores any files without suffix ``.py``.

    .. _hook: https://docs.pytest.org/en/7.1.x/how-to/writing_hook_functions.html
'''

def pt7_pytest_collect_file(file_path:Path, parent:Collector) -> Optional["Module"]:
    ''' Handle ``.pt`` files with our slightly special module load
        routine; all other files get passed on to any other collectors
        that wish to handle them.

        WARNING: This does not check/use the `pytest_pycollect_makemodule()`
        hook.
    '''
    if file_path.suffix != '.pt':  return None

    #   XXX should be be trying to check for a hook if present? This would
    #   allow the end-user to override our PtModule creation. But we'd
    #   somehow need to set the default to our import_pt_module().
    #ihook = parent.session.gethookproxy(file_path)
    #module = ihook.pytest_pycollect_makemodule(
    #       module_path=file_path, parent=parent)

    module:Module = PtModule.from_parent(parent, path=file_path)
    return module

class PtModule(_pytest.python.Module):
    def _getobj(self):
        ''' Call our custom import routine for ``.pt`` files; this replaces
            the standard `_pytest.python.Module` call to the ``.py`` file
            importer, `_pytest.python.importtestmodule()`.
        '''
        return import_pt_module(self.path, self.config)

def import_pt_module(file_path:Path, config:Config):
    ''' This does a job kind of along the lines of
        `_pytest.python.importtestmodule()`, except with much less in the
        way of customised error messages for various exceptions, which we
        should add. This also does the work that
        `_pytest.pathlib.import_path()` does, except in a mostly simpler
        way since ``.pt`` files always are loaded with what is effectively
        importmode=importlib.
    '''
    #   XXX Add better messages like importestmodule() has?

    #   We generate a name for this module guaranteed not to conflict with
    #   any module names generated by the standard import mechanism by
    #   appending ``~pt`` to it, allowing us to enter it into
    #   `sys.modules`. This means we can't use an `import` statement to
    #   import it, but that's fine as it shouldn't be imported. (Any
    #   shared tests should be in .py files that are imported by the
    #   .pt file.)
    module_name = module_name_from_path(file_path, config.rootdir) + '~pt'

    #   If this is called a second time on the same file, we simply return
    #   the Module we earlier deposited in sys.modules.
    #   XXX Can this also return the wrong module on a name collision?
    with contextlib.suppress(KeyError):
        return sys.modules[module_name]

    #   If we are configured to use the assertion-rewriting loader
    #   (_pytest.assertion.rewrite.AssertionRewritingHook), use that
    #   to load the test code. Otherwise use the standard Python loader.
    loader = None
    assertstate = config._store.get(assertstate_key, None)
    if assertstate:
        loader = config._store[assertstate_key].hook
    if loader is None:
        loader = importlib.machinery.SourceFileLoader(modname, path)

    spec = spec_from_file_location(module_name, str(file_path), loader=loader)
    if spec is None:  raise ImportError(    # f-strings available since 3.6
        f"Can't find module {module_name} at location {file_path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    #   Ensure our module has an unbroken chain of parents in sys.modules.
    insert_missing_modules(sys.modules, module_name)
    return module

####################################################################
#   Select version

if ptver == 5:
    pytest_collect_file = pt5_pytest_collect_file
    pytest_configure = pt5_pytest_configure
elif ptver == 7:
    pytest_collect_file = pt7_pytest_collect_file
else:
    raise NotImplementedError(
        'pytest_pt does not support pytest version {}'.format(ptver))
