import pytest

from fury_registry.response import register_namespaces


@pytest.fixture(autouse=True)
def auto_use_ns():
    register_namespaces()
