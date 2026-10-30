"""
storage.py - saving and loading bookings as a JSON file.

BookingStore keeps the bookings file in a folder the user can change from the
Storage page. The chosen folder is remembered in a small settings.json file.
"""
from __future__ import annotations

import json
import os
import time
from dataclasses import asdict
from pathlib import Path

from models import Booking


def app_data_dir() -> Path:
    """Default per-user folder for the application's data (works on Windows and Linux)."""
    base = os.environ.get("LOCALAPPDATA") or os.environ.get("XDG_DATA_HOME") or str(Path.home() / ".local" / "share")
    return Path(base) / "WeAreCars"


class BookingStore:
    """JSON persistence with atomic writes and a user-selectable storage folder."""

    def __init__(self) -> None:
        self.config_dir = app_data_dir()                       # where settings.json lives
        self.config_file = self.config_dir / "settings.json"
        self.directory = self.config_dir                       # folder holding bookings.json
        self.load_warning = ""                                 # set if the file was corrupt

    @property
    def file(self) -> Path:
        """Full path of the bookings file."""
        return self.directory / "bookings.json"

    def load(self) -> list[Booking]:
        """Read the saved folder setting, then load all bookings from that folder."""
        try:
            settings = json.loads(self.config_file.read_text(encoding="utf-8"))
            if settings.get("folder"):
                self.directory = Path(settings["folder"])
        except (OSError, ValueError):
            pass  # no settings file yet (first run) or unreadable - use the default folder
        return self._read(self.file)

    def _read(self, path: Path) -> list[Booking]:
        """Read bookings from a JSON file; a corrupt file is renamed, not deleted."""
        if not path.exists():
            return []
        try:
            return [Booking(**row) for row in json.loads(path.read_text(encoding="utf-8"))]
        except (ValueError, TypeError, OSError) as error:
            # Keep the damaged file as a backup so no data is lost, then start empty.
            backup = path.with_suffix(f".corrupt-{int(time.time())}.json")
            try:
                path.replace(backup)
                self.load_warning = f"The booking file could not be read ({error}). It was kept as {backup.name}."
            except OSError:
                self.load_warning = f"The booking file could not be read ({error})."
            return []

    def save(self, bookings: list[Booking]) -> None:
        """Write all bookings. Writes to a temp file first, then swaps it in, so a
        crash part-way through can never leave a half-written bookings file."""
        self.directory.mkdir(parents=True, exist_ok=True)
        temp_file = self.file.with_suffix(".tmp")
        temp_file.write_text(json.dumps([asdict(booking) for booking in bookings], indent=2), encoding="utf-8")
        temp_file.replace(self.file)

    def change_directory(self, new_dir: Path, current: list[Booking]) -> list[Booking]:
        """Switch to a new folder, merging in any bookings already stored there.

        Returns the merged list. Bookings are matched by reference so nothing is duplicated.
        """
        new_dir.mkdir(parents=True, exist_ok=True)
        merged = list(current)
        known_references = {booking.reference for booking in merged}
        for booking in self._read(new_dir / "bookings.json"):
            if booking.reference not in known_references:
                merged.append(booking)
        self.directory = new_dir
        self.save(merged)
        # Remember the chosen folder for next time the app starts.
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config_file.write_text(json.dumps({"folder": str(new_dir)}), encoding="utf-8")
        return merged
