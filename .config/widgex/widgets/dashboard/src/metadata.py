import gi
import hashlib
import os
import shutil
import json
from pathlib import Path
from urllib.parse import urlparse, unquote
from urllib.request import urlopen

gi.require_version("Playerctl", "2.0")
from gi.repository import Playerctl, GLib


CONFIG_DIR = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "widgex"
CACHE_DIR = CONFIG_DIR / "spotify_cache"
DEFAULT_IMAGE = "./spotify_cache/default.png"
MAX_ART_CACHE = 8
PLAYER_NAME = "spotify"


def is_spotify_player(name) -> bool:
    player_name = getattr(name, "name", str(name)).lower()
    return player_name == PLAYER_NAME or player_name.startswith(f"{PLAYER_NAME}.")


def metadata_get(metadata, key, default=""):
    try:
        value = metadata[key]
    except (KeyError, TypeError):
        return default
    return value if value is not None else default


def first_artist(value):
    if isinstance(value, (list, tuple)) and value:
        return str(value[0])
    if value:
        return str(value)
    return "Unknown"


def save_image(url):
    if not url:
        return DEFAULT_IMAGE

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    art_hash = hashlib.sha1(url.encode("utf-8")).hexdigest()[:12]
    dst_path = CACHE_DIR / f"album_art_{art_hash}.png"

    if url.startswith("file://"):
        file_path = urlparse(url).path
        file_path = unquote(file_path)
        shutil.copy(file_path, dst_path)
    else:
        with urlopen(url, timeout=10) as response:
            dst_path.write_bytes(response.read())

    latest_path = CACHE_DIR / "album_art.png"
    shutil.copy(dst_path, latest_path)
    cleanup_old_art(dst_path)
    return f"./spotify_cache/{dst_path.name}"


def cleanup_old_art(keep_path):
    cached_art = sorted(
        CACHE_DIR.glob("album_art_*.png"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    for path in cached_art[MAX_ART_CACHE:]:
        if path != keep_path:
            path.unlink(missing_ok=True)


def on_metadata(*args):
    player = args[0]
    if player.props.player_name.lower() != PLAYER_NAME:
        return

    metadata = args[1]
    art_url = metadata_get(metadata, "mpris:artUrl")
    try:
        image_path = save_image(art_url)
    except Exception:
        image_path = DEFAULT_IMAGE

    metadata_new = {
        "url": art_url,
        "image": image_path,
        "tint": "#c6d0f5",
        "dark": "#232634",
        "title": metadata_get(metadata, "xesam:title", "Unknown"),
        "artist": first_artist(metadata_get(metadata, "xesam:artist")),
        "album": metadata_get(metadata, "xesam:album", "Unknown"),
        "current_player": player.props.player_name,
    }
    print(json.dumps(metadata_new), flush=True)


def on_play_pause(player, *_):
    """Callback function to regenerate and print the current state of the
    player when it is paused.

    Arguments:
        player: A Player object.
    """
    on_metadata(player, player.props.metadata)


def print_default_metadata():
    metadata = {
        "url": DEFAULT_IMAGE,
        "image": DEFAULT_IMAGE,
        "tint": "#c6d0f5",
        "dark": "#232634",
        "bright": "#ebdbb2",
        "title": "Unknown",
        "artist": "Unknown",
        "album": "Unknown",
        "current_player": "none",
    }
    print(json.dumps(metadata), flush=True)


def player_null_check(player_manager) -> bool:
    """Checks if there are any players being managed by the manager and print
    the default metadata if there are none.

    Arguments:
        player_manager: A PlayerManager object.

    Returns:
        A bool i.e. True if there are no active players, False otherwise.
    """
    if not len(player_manager.props.player_names):
        print_default_metadata()
        return False
    return True


def on_name_appeared(player_manager, name):
    """Callback function for taking action when a player gets either connected or,
    disconnected from the manager.

    Arguments:
        player_manager: A PlayerManager object.
        name: A PlayerName object.
    """
    if is_spotify_player(name):
        init_player(name)


def on_name_vanished(player_manager, name):
    if is_spotify_player(name) and not any(
        is_spotify_player(player_name) for player_name in player_manager.props.player_names
    ):
        print_default_metadata()
        return
    player_null_check(player_manager)


def init_player(name):
    """Creates a Player object by passing a PlayerName object.
    It basically prepares and equips the player with instructions
    (callbacks) on what to do if a player:
        - receives track metadata
        - if a player is paused
        - if a player is not paused
    Finally it will add it to the PlayerManager object.

    Arguments:
        name: A PlayerName object.
    """
    if not is_spotify_player(name):
        return

    player = Playerctl.Player.new_from_name(name)
    player.connect("metadata", on_metadata, manager)
    player.connect("playback-status::playing", on_play_pause, manager)
    player.connect("playback-status::paused", on_play_pause, manager)
    manager.manage_player(player)
    on_metadata(player, player.props.metadata)


manager = Playerctl.PlayerManager()
manager.connect("name-appeared", on_name_appeared)
manager.connect("name-vanished", on_name_vanished)

# loop through and initialize all registered and active MPRIS player on first run.
[init_player(name) for name in manager.props.player_names if is_spotify_player(name)]
if not any(is_spotify_player(name) for name in manager.props.player_names):
    print_default_metadata()
try:
    loop = GLib.MainLoop()
    loop.run()
except (KeyboardInterrupt, Exception):
    loop.quit()
