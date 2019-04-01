"""
Unit and regression test for the siesta_engine package.
"""

# Import package, test suite, and other packages as needed
import siesta_engine
import pytest
import sys

def test_siesta_engine_imported():
    """Sample test, will always pass so long as import statement worked"""
    assert "siesta_engine" in sys.modules
