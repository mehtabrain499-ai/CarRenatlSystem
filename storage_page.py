"""
storage_page.py - the Storage page, where staff can see and change the folder
in which booking records are saved.
"""
from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFileDialog, QVBoxLayout, QWidget

from storage import BookingStore
from widgets import button, card, label, page_header


class StoragePage(QWidget):
    """Shows the current bookings file and a button to choose a different folder."""

    folder_chosen = Signal(Path)   # emitted with the new folder; MainWindow performs the change

    def __init__(self, store: BookingStore) -> None:
        super().__init__()
        self.store = store
        page_layout = QVBoxLayout(self)
        page_layout.setContentsMargins(36, 30, 36, 30)
        page_layout.setSpacing(16)
        page_layout.addLayout(page_header("Storage", "Where booking records are saved on this computer."))
        info_card = card()
        info_layout = QVBoxLayout(info_card)
        info_layout.setContentsMargins(22, 18, 22, 20)
        info_layout.setSpacing(8)
        info_layout.addWidget(label("Current booking file", "h2"))
        self.path_label = label("", wrap=True)
        self.path_label.setTextInteractionFlags(Qt.TextSelectableByMouse)   # lets staff copy the path
        info_layout.addWidget(self.path_label)
        info_layout.addWidget(label("Changing folder copies existing bookings across and merges with any bookings "
                                    "already stored in the new folder.", "muted", wrap=True))
        choose_button = button("Choose folder…", "primary")
        choose_button.clicked.connect(self.choose_folder)
        info_layout.addSpacing(6)
        info_layout.addWidget(choose_button, 0, Qt.AlignLeft)
        page_layout.addWidget(info_card)
        page_layout.addStretch()

    def refresh(self) -> None:
        """Show the current path of the bookings file."""
        self.path_label.setText(str(self.store.file))

    def choose_folder(self) -> None:
        """Let the user pick a folder; do nothing if they cancel the dialog."""
        folder = QFileDialog.getExistingDirectory(self, "Choose booking folder", str(self.store.directory))
        if folder:
            self.folder_chosen.emit(Path(folder))
