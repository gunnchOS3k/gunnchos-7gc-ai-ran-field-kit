#!/usr/bin/env python3
from __future__ import annotations

import sys
from register_external_dataset import main

if __name__ == "__main__":
    argv = ["transform"] + sys.argv[1:]
    raise SystemExit(main(argv))
