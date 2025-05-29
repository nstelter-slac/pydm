# test_terminator.py

import pytest
from qtpy.QtWidgets import QWidget, QVBoxLayout, QMessageBox
from qtpy.QtCore import QEvent, QCoreApplication
from pydm.widgets.terminator import PyDMTerminator

# --------------------
# POSITIVE TEST CASES
# --------------------


def test_construct(qtbot):
    """
    Test basic construction.
    """
    parent = QWidget()
    layout = QVBoxLayout(parent)
    terminator = PyDMTerminator(parent=parent)
    layout.addWidget(terminator)
    qtbot.addWidget(parent)

    assert terminator.timeout == 60
    assert terminator._hook_setup is True
    assert terminator._window == parent
    assert "This screen will close in" in terminator.text()


def test_timeout_property(qtbot):
    """
    Test setting timeout
    """
    terminator = PyDMTerminator(timeout=10)
    qtbot.addWidget(terminator)

    assert terminator.timeout == 10
    assert terminator._time_rem_ms == 10000


@pytest.mark.parametrize(
    "seconds, expected",
    [
        (2, "2 seconds"),
        (61, "2 minutes"),
        (3600, "1 hour"),
        (86400, "1 day"),
        (90000, "2 days"),
    ],
)
def test_get_time_text(seconds, expected):
    """
    Test text formatting for time intervals.
    """
    term = PyDMTerminator()
    result = term._get_time_text(seconds)
    assert expected in result


def test_handle_timeout_closes_window(qtbot, monkeypatch):
    """
    Test timeout, check expected text appears in popup msgbox.
    """
    parent = QWidget()
    terminator = PyDMTerminator(parent=parent, timeout=2)
    qtbot.addWidget(parent)

    # Simulate timeout reached
    terminator._time_rem_ms = 0
    terminator._window = parent

    message_box_text = {}

    def fake_exec_(self):
        # Capture the popup msgbox text
        message_box_text["text"] = self.text()

    monkeypatch.setattr(QMessageBox, "exec_", fake_exec_)

    terminator.handle_timeout()
    assert "was closed due to inactivity" in message_box_text.get("text", "")


def test_start_and_stop(qtbot):
    """
    Test timer starting/stopping.
    """
    terminator = PyDMTerminator(timeout=2)
    qtbot.addWidget(terminator)

    terminator.stop()
    assert not terminator._timer.isActive()

    terminator.start()
    assert terminator._timer.isActive()
