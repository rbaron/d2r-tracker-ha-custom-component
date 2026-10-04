"""Constants for the Diablo 2 Resurrected integration."""

DOMAIN = "d2r_tracker"

ORIGIN_D2RUNEWIZARD = "d2runewizard.com"
ORIGIN_DIABLO2IO = "diablo2.io"
CONF_CONTACT_EMAIL = "Contact Email"
CONF_ORIGIN = "Origin"
CONF_GAME_VERSION = "Game Version"

# Reign of the Warlock and Lord of Destruction run on separate realms, so DClone
# progress is tracked independently for each. Terror zones are shared.
GAME_VERSION_ROTW = "rotw"
GAME_VERSION_LOD = "lod"
GAME_VERSION_LABELS = {
    GAME_VERSION_ROTW: "Reign of the Warlock",
    GAME_VERSION_LOD: "Lord of Destruction",
}
