import json
from pathlib import Path

# Get the directory where this config.py file is located
THIS_DIR = Path(__file__).parent
SOUNDS_DIR = THIS_DIR / "sounds"
MAPPING_FILE = THIS_DIR / "mapping.json"

def load_mapping():
    """
    Loads the gesture-to-sound mapping from mapping.json and returns
    a dictionary mapping gesture names to absolute sound file paths.

    Returns:
        dict: Mapping of gestures (e.g., 'L:I') to Path objects for sound files.

    Raises:
        FileNotFoundError: If mapping.json or any sound file is missing.
        json.JSONDecodeError: If mapping.json is malformed.
        ValueError: If any gesture key is incorrectly formatted.
    """
    if not MAPPING_FILE.exists():
        raise FileNotFoundError(f"[ERROR] Mapping file not found: {MAPPING_FILE}")

    with open(MAPPING_FILE, "r") as f:
        raw_mapping = json.load(f)

    mapping = {}
    for gesture, filename in raw_mapping.items():
        if not isinstance(gesture, str) or ":" not in gesture or len(gesture.split(":")) != 2:
            raise ValueError(f"[ERROR] Invalid gesture key format: {gesture}")

        sound_path = SOUNDS_DIR / filename
        if not sound_path.exists():
            raise FileNotFoundError(f"[ERROR] Sound file not found for gesture {gesture}: {sound_path}")

        mapping[gesture] = sound_path

    return mapping

# Optional: For testing from the terminal
if __name__ == "__main__":
    try:
        mapping = load_mapping()
        print("[INFO] Loaded gesture mapping:")
        for gesture, path in mapping.items():
            print(f"  {gesture} -> {path}")
    except Exception as e:
        print(f"[ERROR] {e}")
