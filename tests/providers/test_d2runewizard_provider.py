from unittest.mock import patch, MagicMock
import json

import pytest

from custom_components.d2r_tracker.const import GAME_VERSION_LOD, GAME_VERSION_ROTW
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


@pytest.fixture
def mock_dclone_response_with_rotw():
    return json.loads("""
{
  "servers": [
    {
      "server": "nonLadderSoftcoreAsia",
      "progress": 2,
      "message": "Terror approaches Sanctuary",
      "ladder": false,
      "hardcore": false,
      "rotw": false,
      "region": "Asia",
      "lastUpdate": {
        "seconds": 1790913227
      },
      "lastWalk": {
        "seconds": 1788084886
      }
    },
    {
      "server": "nonLadderHardcoreAsia",
      "progress": 2,
      "message": "Terror approaches Sanctuary",
      "ladder": false,
      "hardcore": true,
      "rotw": false,
      "region": "Asia",
      "lastUpdate": {
        "seconds": 1790749968
      },
      "lastWalk": {
        "seconds": 1790749804
      }
    },
    {
      "server": "ladderSoftcoreAsia",
      "progress": 3,
      "message": "Terror begins to form within Sanctuary",
      "ladder": true,
      "hardcore": false,
      "rotw": false,
      "region": "Asia",
      "lastUpdate": {
        "seconds": 1790749968
      },
      "lastWalk": {
        "seconds": 1790749804
      }
    },
    {
      "server": "ladderHardcoreAsia",
      "progress": 2,
      "message": "Terror approaches Sanctuary",
      "ladder": true,
      "hardcore": true,
      "rotw": false,
      "region": "Asia",
      "lastUpdate": {
        "seconds": 1790749968
      },
      "lastWalk": {
        "seconds": 1790749804
      }
    },
    {
      "server": "nonLadderSoftcoreAmericas",
      "progress": 5,
      "message": "Terror is about to be unleashed upon Sanctuary",
      "ladder": false,
      "hardcore": false,
      "rotw": false,
      "region": "Americas",
      "lastUpdate": {
        "seconds": 1787873565
      },
      "lastWalk": {
        "seconds": 1787550973
      }
    },
    {
      "server": "nonLadderHardcoreAmericas",
      "progress": 2,
      "message": "Terror approaches Sanctuary",
      "ladder": false,
      "hardcore": true,
      "rotw": false,
      "region": "Americas",
      "lastUpdate": {
        "seconds": 1788903005
      },
      "lastWalk": {
        "seconds": 1788902861
      }
    },
    {
      "server": "ladderSoftcoreAmericas",
      "progress": 1,
      "message": "Terror gazes upon Sanctuary",
      "ladder": true,
      "hardcore": false,
      "rotw": false,
      "region": "Americas",
      "lastUpdate": {
        "seconds": 1782503071
      },
      "lastWalk": {
        "seconds": 1777294954
      }
    },
    {
      "server": "ladderHardcoreAmericas",
      "progress": 4,
      "message": "Terror spreads across Sanctuary",
      "ladder": true,
      "hardcore": true,
      "rotw": false,
      "region": "Americas",
      "lastUpdate": {
        "seconds": 1788903005
      },
      "lastWalk": {
        "seconds": 1788902861
      }
    },
    {
      "server": "nonLadderSoftcoreEurope",
      "progress": 5,
      "message": "Terror is about to be unleashed upon Sanctuary",
      "ladder": false,
      "hardcore": false,
      "rotw": false,
      "region": "Europe",
      "lastUpdate": {
        "seconds": 1790872804
      },
      "lastWalk": {
        "seconds": 1786850169
      }
    },
    {
      "server": "nonLadderHardcoreEurope",
      "progress": 3,
      "message": "Terror begins to form within Sanctuary",
      "ladder": false,
      "hardcore": true,
      "rotw": false,
      "region": "Europe",
      "lastUpdate": {
        "seconds": 1786850220
      },
      "lastWalk": {
        "seconds": 1786850169
      }
    },
    {
      "server": "ladderSoftcoreEurope",
      "progress": 1,
      "message": "Terror gazes upon Sanctuary",
      "ladder": true,
      "hardcore": false,
      "rotw": false,
      "region": "Europe",
      "lastUpdate": {
        "seconds": 1782502970
      },
      "lastWalk": {
        "seconds": 1779713736
      }
    },
    {
      "server": "ladderHardcoreEurope",
      "progress": 4,
      "message": "Terror spreads across Sanctuary",
      "ladder": true,
      "hardcore": true,
      "rotw": false,
      "region": "Europe",
      "lastUpdate": {
        "seconds": 1786850220
      },
      "lastWalk": {
        "seconds": 1786850169
      }
    },
    {
      "server": "nonLadderSoftcoreAsiaRotw",
      "progress": 2,
      "message": "Terror approaches Sanctuary",
      "ladder": false,
      "hardcore": false,
      "rotw": true,
      "region": "AsiaRotw",
      "lastUpdate": {
        "seconds": 1790416153
      },
      "lastWalk": {
        "seconds": 1789818097
      }
    },
    {
      "server": "nonLadderHardcoreAsiaRotw",
      "progress": 1,
      "message": "Terror gazes upon Sanctuary",
      "ladder": false,
      "hardcore": true,
      "rotw": true,
      "region": "AsiaRotw",
      "lastUpdate": {
        "seconds": 1783396054
      },
      "lastWalk": {
        "seconds": 1776585618
      }
    },
    {
      "server": "ladderSoftcoreAsiaRotw",
      "progress": 1,
      "message": "Terror gazes upon Sanctuary",
      "ladder": true,
      "hardcore": false,
      "rotw": true,
      "region": "AsiaRotw",
      "lastUpdate": {
        "seconds": 1790773445
      },
      "lastWalk": {
        "seconds": 1790773445
      }
    },
    {
      "server": "ladderHardcoreAsiaRotw",
      "progress": 1,
      "message": "Terror gazes upon Sanctuary",
      "ladder": true,
      "hardcore": true,
      "rotw": true,
      "region": "AsiaRotw",
      "lastUpdate": {
        "seconds": 1783396054
      },
      "lastWalk": {
        "seconds": 0
      }
    },
    {
      "server": "nonLadderSoftcoreAmericasRotw",
      "progress": 1,
      "message": "Terror gazes upon Sanctuary",
      "ladder": false,
      "hardcore": false,
      "rotw": true,
      "region": "AmericasRotw",
      "lastUpdate": {
        "seconds": 1790903461
      },
      "lastWalk": {
        "seconds": 1790903461
      }
    },
    {
      "server": "nonLadderHardcoreAmericasRotw",
      "progress": 1,
      "message": "Terror gazes upon Sanctuary",
      "ladder": false,
      "hardcore": true,
      "rotw": true,
      "region": "AmericasRotw",
      "lastUpdate": {
        "seconds": 1782503071
      },
      "lastWalk": {
        "seconds": 1776578428
      }
    },
    {
      "server": "ladderSoftcoreAmericasRotw",
      "progress": 1,
      "message": "Terror gazes upon Sanctuary",
      "ladder": true,
      "hardcore": false,
      "rotw": true,
      "region": "AmericasRotw",
      "lastUpdate": {
        "seconds": 1790946223
      },
      "lastWalk": {
        "seconds": 1790946223
      }
    },
    {
      "server": "ladderHardcoreAmericasRotw",
      "progress": 1,
      "message": "Terror gazes upon Sanctuary",
      "ladder": true,
      "hardcore": true,
      "rotw": true,
      "region": "AmericasRotw",
      "lastUpdate": {
        "seconds": 1789909383
      },
      "lastWalk": {
        "seconds": 1789909383
      }
    },
    {
      "server": "nonLadderSoftcoreEuropeRotw",
      "progress": 2,
      "message": "Terror approaches Sanctuary",
      "ladder": false,
      "hardcore": false,
      "rotw": true,
      "region": "EuropeRotw",
      "lastUpdate": {
        "seconds": 1790690033
      },
      "lastWalk": {
        "seconds": 1789761394
      }
    },
    {
      "server": "nonLadderHardcoreEuropeRotw",
      "progress": 2,
      "message": "Terror approaches Sanctuary",
      "ladder": false,
      "hardcore": true,
      "rotw": true,
      "region": "EuropeRotw",
      "lastUpdate": {
        "seconds": 1788020216
      },
      "lastWalk": {
        "seconds": 1776582024
      }
    },
    {
      "server": "ladderSoftcoreEuropeRotw",
      "progress": 4,
      "message": "Terror spreads across Sanctuary",
      "ladder": true,
      "hardcore": false,
      "rotw": true,
      "region": "EuropeRotw",
      "lastUpdate": {
        "seconds": 1791121456
      },
      "lastWalk": {
        "seconds": 1791031226
      }
    },
    {
      "server": "ladderHardcoreEuropeRotw",
      "progress": 1,
      "message": "Terror gazes upon Sanctuary",
      "ladder": true,
      "hardcore": true,
      "rotw": true,
      "region": "EuropeRotw",
      "lastUpdate": {
        "seconds": 1787888430
      },
      "lastWalk": {
        "seconds": 1787888430
      }
    }
  ]
}
    """)


@pytest.mark.parametrize(
    "game_version,expected",
    [
        (
            GAME_VERSION_LOD,
            DCloneProgress(
                Americas=DCloneLadderProgress(
                    L=DCloneCoreProgress(HC=Progress(4), SC=Progress(1)),
                    NL=DCloneCoreProgress(HC=Progress(2), SC=Progress(5)),
                ),
                Europe=DCloneLadderProgress(
                    L=DCloneCoreProgress(HC=Progress(4), SC=Progress(1)),
                    NL=DCloneCoreProgress(HC=Progress(3), SC=Progress(5)),
                ),
                Asia=DCloneLadderProgress(
                    L=DCloneCoreProgress(HC=Progress(2), SC=Progress(3)),
                    NL=DCloneCoreProgress(HC=Progress(2), SC=Progress(2)),
                ),
                China=None,
            ),
        ),
        (
            GAME_VERSION_ROTW,
            DCloneProgress(
                Americas=DCloneLadderProgress(
                    L=DCloneCoreProgress(HC=Progress(1), SC=Progress(1)),
                    NL=DCloneCoreProgress(HC=Progress(1), SC=Progress(1)),
                ),
                Europe=DCloneLadderProgress(
                    L=DCloneCoreProgress(HC=Progress(1), SC=Progress(4)),
                    NL=DCloneCoreProgress(HC=Progress(2), SC=Progress(2)),
                ),
                Asia=DCloneLadderProgress(
                    L=DCloneCoreProgress(HC=Progress(1), SC=Progress(1)),
                    NL=DCloneCoreProgress(HC=Progress(1), SC=Progress(2)),
                ),
                China=None,
            ),
        ),
    ],
)
@patch(
    "custom_components.d2r_tracker.providers.d2runewizard.get_d2runewizard_api_response"
)
def test_get_dclone_progress_by_game_version(
    mock_api_response, mock_dclone_response_with_rotw, game_version, expected
):
    """Test that only servers for the configured game version are used."""
    mock_api_response.return_value = mock_dclone_response_with_rotw

    provider = D2RuneWizardProvider(
        api_key="test_key",
        contact_email="test@example.com",
        game_version=game_version,
    )

    assert provider.get_dclone_progress() == expected


@patch(
    "custom_components.d2r_tracker.providers.d2runewizard.get_d2runewizard_api_response"
)
def test_get_dclone_progress(mock_api_response, mock_dclone_response):
    """Test that get_dclone_progress correctly processes API response."""
    mock_api_response.return_value = mock_dclone_response

    provider = D2RuneWizardProvider(
        api_key="test_key",
        contact_email="test@example.com",
        game_version=GAME_VERSION_LOD,
    )

    progress = provider.get_dclone_progress()

    mock_api_response.assert_called_once_with(
        "https://d2runewizard.com/api/trackers/diablo-clone",
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
        api_key="test_key",
        contact_email="test@example.com",
        game_version=GAME_VERSION_LOD,
    )

    _ = provider.get_dclone_progress()

    # Check requests.get args.
    mock_requests_get.assert_called_once()
    args, kwargs = mock_requests_get.call_args

    assert args[0] == "https://d2runewizard.com/api/trackers/diablo-clone"
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
        api_key="test_key",
        contact_email="test@example.com",
        game_version=GAME_VERSION_LOD,
    )

    res = provider.get_terror_zone()

    # Check requests.get args.
    mock_requests_get.assert_called_once()
    args, kwargs = mock_requests_get.call_args

    assert args[0] == "https://d2runewizard.com/api/trackers/terror-zone"
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
        api_key="test_key",
        contact_email="test@example.com",
        game_version=GAME_VERSION_LOD,
    )
    assert provider.NAME == "d2runewizard.com"
    assert provider.get_attribution() == "Data courtesy of d2runewizard.com"
