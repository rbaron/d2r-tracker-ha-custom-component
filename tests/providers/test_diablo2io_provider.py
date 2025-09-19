from unittest.mock import patch, MagicMock
import json

import pytest

from custom_components.d2r_tracker.providers.diablo2io import (
    Diablo2IOProvider,
)
from custom_components.d2r_tracker.providers import (
    DCloneProgress,
    DCloneCoreProgress,
    DCloneLadderProgress,
    Progress,
)


@pytest.fixture
def mock_dclone_response():
    return json.loads("""
[
  {
    "progress": "4",
    "region": "2",
    "ladder": "1",
    "hc": "2",
    "timestamped": "1757559236",
    "reporter_id": "76181"
  },
  {
    "progress": "2",
    "region": "3",
    "ladder": "2",
    "hc": "2",
    "timestamped": "1758253449",
    "reporter_id": "76181"
  },
  {
    "progress": "2",
    "region": "3",
    "ladder": "2",
    "hc": "1",
    "timestamped": "1758183982",
    "reporter_id": "76181"
  },
  {
    "progress": "2",
    "region": "3",
    "ladder": "1",
    "hc": "2",
    "timestamped": "1758253830",
    "reporter_id": "76181"
  },
  {
    "progress": "1",
    "region": "1",
    "ladder": "2",
    "hc": "2",
    "timestamped": "1758249714",
    "reporter_id": "76181"
  },
  {
    "progress": "1",
    "region": "1",
    "ladder": "2",
    "hc": "1",
    "timestamped": "1756604363",
    "reporter_id": "76181"
  },
  {
    "progress": "1",
    "region": "1",
    "ladder": "1",
    "hc": "2",
    "timestamped": "1758105263",
    "reporter_id": "76181"
  },
  {
    "progress": "1",
    "region": "1",
    "ladder": "1",
    "hc": "1",
    "timestamped": "1756604363",
    "reporter_id": "76181"
  },
  {
    "progress": "1",
    "region": "2",
    "ladder": "2",
    "hc": "2",
    "timestamped": "1757632005",
    "reporter_id": "76181"
  },
  {
    "progress": "1",
    "region": "2",
    "ladder": "2",
    "hc": "1",
    "timestamped": "1756604340",
    "reporter_id": "76181"
  },
  {
    "progress": "1",
    "region": "2",
    "ladder": "1",
    "hc": "1",
    "timestamped": "1757606229",
    "reporter_id": "76181"
  },
  {
    "progress": "1",
    "region": "3",
    "ladder": "1",
    "hc": "1",
    "timestamped": "1758183982",
    "reporter_id": "76181"
  }
]
    """)


@patch("requests.get")
def test_get_dclone(mock_requests_get, mock_dclone_response):
    """Test that get_d2runewizard_api_response sends correct headers."""
    mock_response = MagicMock()
    mock_response.json.return_value = mock_dclone_response
    mock_requests_get.return_value = mock_response

    provider = Diablo2IOProvider(api_key="test_key", contact_email="test@example.com")

    response = provider.get_dclone_progress()

    # Check requests.get args.
    mock_requests_get.assert_called_once()
    args, kwargs = mock_requests_get.call_args

    assert args[0] == "https://diablo2.io/dclone_api.php"
    assert kwargs["timeout"] == 60

    expected_headers = {
        "Contact-Email": "test@example.com",
        "From": "Home Assistant integration github.com/rbaron/d2r-tracker-ha-custom-component",
    }
    assert kwargs["headers"] == expected_headers

    assert response == DCloneProgress(
        Americas=DCloneLadderProgress(
            L=DCloneCoreProgress(HC=Progress(1), SC=Progress(1)),
            NL=DCloneCoreProgress(HC=Progress(1), SC=Progress(1)),
        ),
        Europe=DCloneLadderProgress(
            L=DCloneCoreProgress(HC=Progress(1), SC=Progress(4)),
            NL=DCloneCoreProgress(HC=Progress(1), SC=Progress(1)),
        ),
        Asia=DCloneLadderProgress(
            L=DCloneCoreProgress(HC=Progress(1), SC=Progress(2)),
            NL=DCloneCoreProgress(HC=Progress(2), SC=Progress(2)),
        ),
        China=None,
    )


def test_terror_zone_unimplemented():
    """Test that TerrorZone is unimplemented and raises NotImplementedError."""
    provider = Diablo2IOProvider(api_key="test_key", contact_email="test@example.com")
    with pytest.raises(NotImplementedError):
        provider.get_terror_zone()


def test_attribution():
    provider = Diablo2IOProvider(api_key="test_key", contact_email="test@example.com")
    assert provider.NAME == "diablo2.io"
    assert provider.get_attribution() == "Data courtesy of diablo2.io"
