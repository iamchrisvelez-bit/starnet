from __future__ import annotations

from datetime import datetime, timezone

import pytest

from tf_config.load import FloorConfig, load_floor
from tests.support import make_runtime


@pytest.fixture(scope="session")
def floor() -> FloorConfig:
    return load_floor()


@pytest.fixture
def now() -> datetime:
    return datetime(2026, 11, 2, 18, 0, tzinfo=timezone.utc)


@pytest.fixture
def runtime(floor: FloorConfig, now: datetime):
    return make_runtime(floor, now)
