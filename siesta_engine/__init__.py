"""
siesta_engine
ASE+Siesta+ML
"""

# Add imports here
from . import calculator
from .calculator import CustomSiesta
# Handle versioneer
from ._version import get_versions
versions = get_versions()
__version__ = versions['version']
__git_revision__ = versions['full-revisionid']
del get_versions, versions
