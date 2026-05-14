"""Fixture bridge: expose JSON data fixtures to pytest by importing them into
a conftest.py located where pytest will auto-load it.
"""
from tests.fixtures.data_fixtures import sample_users, sample_cards

# re-export names so pytest discovers them as fixtures
__all__ = ["sample_users", "sample_cards"]
