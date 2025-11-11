from pathlib import Path


BASE_DIR = Path(__file__).parent.parent
WEB_DIR = BASE_DIR / "web"
STATIC_DIR = WEB_DIR / "static"
TEMPLATES_DIR = WEB_DIR / "templates"
ASSETS_DIR = BASE_DIR / "assets"
TILES_DIR = ASSETS_DIR / "tiles"

TILE_CACHE_MAX_AGE = 3600

GENERATE_ZOOM_INTERVAL = 300