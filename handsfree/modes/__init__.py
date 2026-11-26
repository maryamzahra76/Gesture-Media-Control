# NOTE: temporary file for testing Media Mode on its own.
# Do NOT copy this file into the team project. The team project has its own
# modes/__init__.py that registers all three modes.
from .media_mode import MediaMode

MODE_CLASSES = {
    "cursor": MediaMode,
    "media": MediaMode,
    "presentation": MediaMode,
}
