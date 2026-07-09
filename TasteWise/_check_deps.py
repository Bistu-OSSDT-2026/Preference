"""Check if all dependencies in requirements.txt are installed."""
import sys
import importlib
import re

missing = []
with open("requirements.txt") as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        # Extract package name (remove version specifiers)
        name = re.split(r"[<>=~!@#]+", line)[0].strip().lower().replace("-", "_")
        if not name:
            continue
        try:
            importlib.import_module(name)
        except ImportError:
            missing.append(line)

if missing:
    print("Missing packages:")
    for p in missing:
        print(f"  - {p}")
    sys.exit(1)
else:
    print("All dependencies satisfied")
    sys.exit(0)
