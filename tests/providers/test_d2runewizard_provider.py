from unittest.mock import patch, MagicMock
import json

import pytest

from custom_components.d2r_tracker.providers.d2runewizard import (
    D2RuneWizardProvider,
)
from custom_components.d2r_tracker.providers import (
    DCloneProgress,
    DCloneCoreProgress,
    DCloneLadderProgress,
    Progress,
    TerrorZoneResponse,
)


@pytest.fixture
def mock_terror_zone_response():
    return json.loads("""
{
  "terrorZone": {
    "zone": "Unknown",
    "act": "Unknown",
    "lastReportedBy": "Unknown",
    "reportedZones": {},
    "highestProbabilityZone": {
      "zone": "",
      "act": "",
      "amount": 0,
      "probability": 0
    }
  },
  "nextTerrorZone": {
    "zone": "Cathedral and Catacombs",
    "act": "act1"
  },
  "currentTerrorZone": {
    "zone": "Arcane Sanctuary",
    "act": "act2"
  },
  "providedBy": "https://d2runewizard.com/terror-zone-tracker"
}
    """)


@pytest.fixture
def mock_dclone_response():
    return json.loads("""
{
  "servers": [
    {
      "server": "nonLadderSoftcoreAsia",
      "progress": 2,
      "message": "Terror approaches Sanctuary",
      "ladder": false,
      "hardcore": false,
      "region": "Asia",
      "lastUpdate": {
        "seconds": 1758253449
      }
    },
    {
      "server": "nonLadderHardcoreAsia",
      "progress": 2,
      "message": "Terror approaches Sanctuary",
      "ladder": false,
      "hardcore": true,
      "region": "Asia",
      "lastUpdate": {
        "seconds": 1758183982
      }
    },
    {
      "server": "ladderSoftcoreAsia",
      "progress": 2,
      "message": "Terror approaches Sanctuary",
      "ladder": true,
      "hardcore": false,
      "region": "Asia",
      "lastUpdate": {
        "seconds": 1758253830
      }
    },
    {
      "server": "ladderHardcoreAsia",
      "progress": 1,
      "message": "Terror gazes upon Sanctuary",
      "ladder": true,
      "hardcore": true,
      "region": "Asia"
    },
    {
      "server": "nonLadderSoftcoreAmericas",
      "progress": 1,
      "message": "Terror gazes upon Sanctuary",
      "ladder": false,
      "hardcore": false,
      "region": "Americas"
    },
    {
      "server": "nonLadderHardcoreAmericas",
      "progress": 1,
      "message": "Terror gazes upon Sanctuary",
      "ladder": false,
      "hardcore": true,
      "region": "Americas"
    },
    {
      "server": "ladderSoftcoreAmericas",
      "progress": 1,
      "message": "Terror gazes upon Sanctuary",
      "ladder": true,
      "hardcore": false,
      "region": "Americas"
    },
    {
      "server": "ladderHardcoreAmericas",
      "progress": 1,
      "message": "Terror gazes upon Sanctuary",
      "ladder": true,
      "hardcore": true,
      "region": "Americas"
    },
    {
      "server": "nonLadderSoftcoreEurope",
      "progress": 1,
      "message": "Terror gazes upon Sanctuary",
      "ladder": false,
      "hardcore": false,
      "region": "Europe"
    },
    {
      "server": "nonLadderHardcoreEurope",
      "progress": 1,
      "message": "Terror gazes upon Sanctuary",
      "ladder": false,
      "hardcore": true,
      "region": "Europe"
    },
    {
      "server": "ladderSoftcoreEurope",
      "progress": 4,
      "message": "Terror spreads across Sanctuary",
      "ladder": true,
      "hardcore": false,
      "region": "Europe",
      "lastUpdate": {
        "seconds": 1757559236
      }
    },
    {
      "server": "ladderHardcoreEurope",
      "progress": 1,
      "message": "Terror gazes upon Sanctuary",
      "ladder": true,
      "hardcore": true,
      "region": "Europe"
    }
  ],
  "providedBy": "https://d2runewizard.com/diablo-clone-tracker",
  "version": "2.0"
}
    """)


@patch(
    "custom_components.d2r_tracker.providers.d2runewizard.get_d2runewizard_api_response"
)
def test_get_dclone_progress(mock_api_response, mock_dclone_response):
    """Test that get_dclone_progress correctly processes API response."""
    mock_api_response.return_value = mock_dclone_response

    provider = D2RuneWizardProvider(
        api_key="test_key", contact_email="test@example.com"
    )

    progress = provider.get_dclone_progress()

    mock_api_response.assert_called_once_with(
        "https://d2runewizard.com/api/diablo-clone-progress/all",
        "test_key",
        "test@example.com",
    )

    assert progress == DCloneProgress(
        Americas=DCloneLadderProgress(
            L=DCloneCoreProgress(
                HC=Progress(1),  # ladderHardcoreAmericas
                SC=Progress(1),  # ladderSoftcoreAmericas
            ),
            NL=DCloneCoreProgress(
                HC=Progress(1),  # nonLadderHardcoreAmericas
                SC=Progress(1),  # nonLadderSoftcoreAmericas
            ),
        ),
        Europe=DCloneLadderProgress(
            L=DCloneCoreProgress(
                HC=Progress(1),  # ladderHardcoreEurope
                SC=Progress(4),  # ladderSoftcoreEurope
            ),
            NL=DCloneCoreProgress(
                HC=Progress(1),  # nonLadderHardcoreEurope
                SC=Progress(1),  # nonLadderSoftcoreEurope
            ),
        ),
        Asia=DCloneLadderProgress(
            L=DCloneCoreProgress(
                HC=Progress(1),  # ladderHardcoreAsia
                SC=Progress(2),  # ladderSoftcoreAsia
            ),
            NL=DCloneCoreProgress(
                HC=Progress(2),  # nonLadderHardcoreAsia
                SC=Progress(2),  # nonLadderSoftcoreAsia
            ),
        ),
        China=None,
    )


@patch("requests.get")
def test_api_headers(mock_requests_get, mock_dclone_response):
    """Test that get_d2runewizard_api_response sends correct headers."""
    mock_response = MagicMock()
    mock_response.json.return_value = mock_dclone_response
    mock_requests_get.return_value = mock_response

    provider = D2RuneWizardProvider(
        api_key="test_key", contact_email="test@example.com"
    )

    _ = provider.get_dclone_progress()

    # Check requests.get args.
    mock_requests_get.assert_called_once()
    args, kwargs = mock_requests_get.call_args

    assert args[0] == "https://d2runewizard.com/api/diablo-clone-progress/all"
    assert kwargs["timeout"] == 60

    expected_headers = {
        "D2R-Contact": "test@example.com",
        "D2R-Platform": "Home Assistant -- github.com/rbaron/d2r-tracker-ha-custom-component",
        "D2R-Repo": "https://github.com/rbaron/d2r-tracker-ha-custom-component",
    }
    assert kwargs["headers"] == expected_headers

    assert kwargs["params"] == {"token": "test_key"}


@patch("requests.get")
def test_get_terror_zone_response(mock_requests_get, mock_terror_zone_response):
    """Test that get_d2runewizard_api_response sends correct headers."""
    mock_response = MagicMock()
    mock_response.json.return_value = mock_terror_zone_response
    mock_requests_get.return_value = mock_response

    provider = D2RuneWizardProvider(
        api_key="test_key", contact_email="test@example.com"
    )

    res = provider.get_terror_zone()

    # Check requests.get args.
    mock_requests_get.assert_called_once()
    args, kwargs = mock_requests_get.call_args

    assert args[0] == "https://d2runewizard.com/api/terror-zone"
    assert kwargs["timeout"] == 60

    expected_headers = {
        "D2R-Contact": "test@example.com",
        "D2R-Platform": "Home Assistant -- github.com/rbaron/d2r-tracker-ha-custom-component",
        "D2R-Repo": "https://github.com/rbaron/d2r-tracker-ha-custom-component",
    }
    assert kwargs["headers"] == expected_headers

    assert kwargs["params"] == {"token": "test_key"}

    assert res == TerrorZoneResponse(
        current="Arcane Sanctuary",
        next="Cathedral and Catacombs",
        updated_at=res.updated_at,  # Just check that it's a datetime.
    )


def test_attribution():
    provider = D2RuneWizardProvider(
        api_key="test_key", contact_email="test@example.com"
    )
    assert provider.NAME == "d2runewizard.com"
    assert provider.get_attribution() == "Data courtesy of d2runewizard.com"
