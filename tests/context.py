"""
A file to allow import of the main module by the test suite.

This avoids the need to mount the module to site-packages.
"""
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import aceso # noqa
