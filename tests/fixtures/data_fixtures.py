import json
import os
import pytest


def _load(name):
    path = os.path.join(os.path.dirname(__file__), "..", "data", "fixtures", name)
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


@pytest.fixture(scope="session")
def sample_users():
    return _load("users.json")


@pytest.fixture(scope="session")
def sample_cards():
    return _load("test_cards.json")
