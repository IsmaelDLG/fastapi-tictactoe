import pytest


@pytest.fixture
def base_headers():
    return {"Accept": "application/json", "Content-Type": "application/json"}
