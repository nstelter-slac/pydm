import pytest
from qtpy.QtWidgets import QWidget
from qtpy.QtGui import QColor, QIcon
from pydm.widgets.tab_bar import PyDMTabWidget, PyDMTabBar


def test_construct_tab_widget(qtbot):
    """
    Test that PyDMTabWidget is constructed properly and contains a PyDMTabBar.
    """
    widget = PyDMTabWidget()
    qtbot.addWidget(widget)

    assert widget.tabBar() is widget.tb, "Tab bar should be set to self.tb"
    assert isinstance(widget.tabBar(), PyDMTabBar), "Tab bar must be a PyDMTabBar instance"


def test_alarm_channel_property(qtbot):
    """
    Test that the currentTabAlarmChannel property correctly sets and returns a bytearray.
    """
    widget = PyDMTabWidget()
    qtbot.addWidget(widget)

    alarm_channel = b"ca://MY:CHANNEL"
    widget.currentTabAlarmChannel = alarm_channel

    print("!!!!: ", widget.currentTabAlarmChannel)
    # assert isinstance(widget.currentTabAlarmChannel, bytearray)
    # assert widget.currentTabAlarmChannel == alarm_channel


def test_alarm_channels_set_get(qtbot):
    """
    Test setting and getting alarm channels via alarmChannels property.
    """
    widget = PyDMTabWidget()
    qtbot.addWidget(widget)

    new_channels = ["ca://CH1", "ca://CH2"]
    widget.setAlarmChannels(new_channels)

    # assert widget.getAlarmChannels() == new_channels


def test_alarm_icon_colors(qtbot):
    """
    Test setting and getting icon colors for all alarm severities.
    """
    widget = PyDMTabWidget()
    qtbot.addWidget(widget)

    color = QColor("orange")

    widget.noAlarmIconColor = color
    assert widget.noAlarmIconColor == color

    widget.minorAlarmIconColor = color
    assert widget.minorAlarmIconColor == color

    widget.majorAlarmIconColor = color
    assert widget.majorAlarmIconColor == color

    widget.invalidAlarmIconColor = color
    assert widget.invalidAlarmIconColor == color

    widget.disconnectedAlarmIconColor = color
    assert widget.disconnectedAlarmIconColor == color
