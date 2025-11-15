from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
WEB_DIR = BASE_DIR / "web"
STATIC_DIR = WEB_DIR / "static"
TEMPLATES_DIR = WEB_DIR / "templates"
ASSETS_DIR = BASE_DIR / "assets"
DATA_DIR = BASE_DIR / "data"
WORLDS_DIR = DATA_DIR / "worlds"
TILE_CACHE_MAX_AGE = 3600
GENERATE_ZOOM_INTERVAL = 300

MAP_SIZE = 2000
MAP_UPDATE_INTERVAL = 5000
MAP_DEFAULT_WORLD = "Overworld"