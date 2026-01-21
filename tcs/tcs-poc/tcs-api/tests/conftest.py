"""Pytest configuration and shared fixtures."""

import os
from hypothesis import settings, Verbosity


# Register Hypothesis profiles for different testing scenarios
settings.register_profile(
    "quick",
    max_examples=10,
    deadline=500
)

settings.register_profile(
    "thorough",
    max_examples=1000,
    deadline=2000
)

settings.register_profile(
    "debug",
    max_examples=10,
    verbosity=Verbosity.verbose
)

# Load profile from environment or default to quick
settings.load_profile(os.getenv("HYPOTHESIS_PROFILE", "quick"))