import os
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Keep pytest tempfiles on the local filesystem to avoid capture errors.
for env_var in ("TMPDIR", "TMP", "TEMP"):
    os.environ[env_var] = "/tmp"

tempfile.tempdir = "/tmp"
