from contextlib import contextmanager
import fcntl
import os
from .common import state_dir

@contextmanager
def lock(name):
    fd=os.open(state_dir()/(name+'.lock'),os.O_RDWR|os.O_CREAT|os.O_NOFOLLOW,0o600)
    with os.fdopen(fd,'w') as f:
        fcntl.flock(f,fcntl.LOCK_EX)
        try:yield
        finally:fcntl.flock(f,fcntl.LOCK_UN)
