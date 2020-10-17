from gillespy2.core.gillespyError import BuildError, SolverError
import os
import inspect
import subprocess
import shutil

import gillespy2
from gillespy2.core import log

GILLESPY_DIR = os.path.dirname(inspect.getfile(gillespy2))
GILLESPY_C_DIR = os.path.join(GILLESPY_DIR, 'solvers/cpp/c_base')
MAKE_FILE = os.path.dirname(os.path.abspath(__file__))+'/c_base/makefile'

CACHE_DIR = os.path.join(GILLESPY_DIR, 'build_cache/')
CACHE_FILES = ["ssa.o", "model.o"]

class CPPCompiler():
    def build(self, output_dir, rebuild_cache = False):
        if not os.path.isdir(output_dir):
            raise BuildError("Output dir does not exist, stopping compilation.")

        if rebuild_cache or not self.cache_exists() :
            log.warning("Simulation cache does not exist, recompiling...")
            self.compile_cache()

        # Link the cache files with the new build directory.
        for file in CACHE_FILES:
            os.symlink(os.path.join(CACHE_DIR, file), os.path.join(output_dir, file))

        # Compile the template.
        self.__make_wrapper(["-C", output_dir, "-f", MAKE_FILE])

    def build_cache(self):
        if not os.path.isdir(CACHE_DIR):
            os.makedirs(CACHE_DIR)

        # Compile just the solvers using the makefile.
        self.__make_wrapper(["-C", GILLESPY_C_DIR, "-f", MAKE_FILE, "assembleSolvers"])

        # Move the cache files into the cache.
        for file in CACHE_FILES:
            shutil.move(os.path.join(GILLESPY_C_DIR, file), os.path.join(CACHE_DIR, file))

    def clean_cache(self):
        if self.cache_exists():
            os.rmdir(CACHE_DIR)

    def cache_exists(self):
        if not os.path.isdir(CACHE_DIR):
            return False

        for file in CACHE_FILES:
            if not os.path.isfile(os.path.join(CACHE_DIR, file)):
                return False

        return True

    def __make_wrapper(self, args):
        try:
            make_status = subprocess.run(["make"] + args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        except KeyboardInterrupt:
            log.warning(
                "Solver has been interrupted during compile time, unexpected behavior may occur.")

        return make_status
