import os
import inspect
import gillespy2
import subprocess

GILLESPY_PATH = os.path.dirname(inspect.getfile(gillespy2))
GILLESPY_C_DIRECTORY = os.path.join(GILLESPY_PATH, 'solvers/cpp/c_base')
MAKE_FILE = os.path.dirname(os.path.abspath(__file__))+'/c_base/makefile'
BUILD_CACHE_DIR = os.path.join(GILLESPY_PATH, 'build_cache/')

def make_cache():
    # Check if the build cache directory exists. If not, make it.
    if not os.path.isdir(BUILD_CACHE_DIR):
        os.makedir(BUILD_CACHE_DIR)

    make_status = subprocess.run(["make", "-C", BUILD_CACHE_DIR, "-f", MAKE_FILE, "CompileSolvers"], 
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
def cache_exists():
    return

def clean_cache():
    return

