# filepath: /workspaces/d2r-tracker-ha-custom-component/tests/providers/test_cached_provider.py
from unittest.mock import patch
from datetime import datetime, timedelta
import pytest

from custom_components.d2r_tracker.providers.cached import CachedProvider
from custom_components.d2r_tracker.providers import (
    DCloneProgress,
    DCloneCoreProgress,
    DCloneLadderProgress,
    Progress,
    ProviderBase,
    TerrorZoneResponse,
)


class MockProvider(ProviderBase):
    NAME = "mock_provider"

    def __init__(self):
        self.get_dclone_progress_call_count = 0
        self.get_terror_zone_call_count = 0

    def get_attribution(self) -> str:
        return "Mock Provider Data"

    def get_dclone_progress(self) -> DCloneProgress:
        self.get_dclone_progress_call_count += 1
        return DCloneProgress(
            Americas=DCloneLadderProgress(
                L=DCloneCoreProgress(HC=Progress(1), SC=Progress(2)),
                NL=DCloneCoreProgress(HC=Progress(3), SC=Progress(4)),
            ),
            Europe=DCloneLadderProgress(
                L=DCloneCoreProgress(HC=Progress(1), SC=Progress(2)),
                NL=DCloneCoreProgress(HC=Progress(3), SC=Progress(4)),
            ),
            Asia=DCloneLadderProgress(
                L=DCloneCoreProgress(HC=Progress(1), SC=Progress(2)),
                NL=DCloneCoreProgress(HC=Progress(3), SC=Progress(4)),
            ),
            China=None,
        )

    def get_terror_zone(self) -> TerrorZoneResponse:
        self.get_terror_zone_call_count += 1
        return TerrorZoneResponse(
            current="Test Zone",
            next="Next Test Zone",
            updated_at=datetime.now(),
        )


@pytest.fixture
def mock_provider():
    return MockProvider()


@pytest.fixture
def cached_provider(mock_provider):
    return CachedProvider(mock_provider)


def test_get_attribution(cached_provider, mock_provider):
    assert cached_provider.get_attribution() == mock_provider.get_attribution()


def test_name(cached_provider, mock_provider):
    assert cached_provider.NAME == mock_provider.NAME


def test_get_dclone_progress_caching(cached_provider, mock_provider):
    """Test that get_dclone_progress caches results for 60 seconds."""
    # First call should hit the provider.
    result1 = cached_provider.get_dclone_progress()
    assert mock_provider.get_dclone_progress_call_count == 1

    # Second call should use cache.
    result2 = cached_provider.get_dclone_progress()
    assert mock_provider.get_dclone_progress_call_count == 1

    assert result1 is result2


@patch("custom_components.d2r_tracker.providers.cached.dt")
def test_get_terror_zone_fast_caching(mock_dt, cached_provider, mock_provider):
    """Test that get_terror_zone caches results for 1 minute in the first few minutes of the hour."""
    # Set current time to 10:01 AM.
    initial_time = datetime(2025, 1, 1, 10, 1, 0)
    mock_dt.now.return_value = initial_time

    result1 = cached_provider.get_terror_zone()
    assert mock_provider.get_terror_zone_call_count == 1

    # Call after 30 seconds (still within the same minute) should hit the cache.
    mock_dt.now.return_value = initial_time + timedelta(seconds=30)
    result2 = cached_provider.get_terror_zone()
    assert mock_provider.get_terror_zone_call_count == 1
    assert result1 is result2

    # Call after 61 seconds should refresh the cache.
    mock_dt.now.return_value = initial_time + timedelta(seconds=61)
    result3 = cached_provider.get_terror_zone()
    assert mock_provider.get_terror_zone_call_count == 2
    assert result1 is not result3


@patch("custom_components.d2r_tracker.providers.cached.dt")
def test_get_terror_zone_slow_caching(mock_dt, cached_provider, mock_provider):
    """Test that get_terror_zone caches results for until next whole hour after 5 minutes."""
    # Set current time to 10:10 AM.
    initial_time = datetime(2025, 1, 1, 10, 10, 0)
    mock_dt.now.return_value = initial_time

    result1 = cached_provider.get_terror_zone()
    assert mock_provider.get_terror_zone_call_count == 1

    # Call at 10:59 (still before next hour) should hit the cache.
    mock_dt.now.return_value = datetime(2025, 1, 1, 10, 59, 0)
    result2 = cached_provider.get_terror_zone()
    assert mock_provider.get_terror_zone_call_count == 1
    assert result1 is result2

    # Call at 11:00 should refresh the cache.
    mock_dt.now.return_value = datetime(2025, 1, 1, 11, 0, 0)
    result3 = cached_provider.get_terror_zone()
    assert mock_provider.get_terror_zone_call_count == 2
    assert result1 is not result3
