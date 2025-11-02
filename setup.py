"""Setup script for backward compatibility.

Modern Python packaging uses pyproject.toml, but this setup.py provides
backward compatibility for older tooling and workflows.
"""

from setuptools import setup

# All configuration is in pyproject.toml
setup()
