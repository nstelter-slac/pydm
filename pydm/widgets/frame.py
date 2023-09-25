from qtpy.QtWidgets import QFrame
from qtpy.QtCore import Property
from .base import PyDMWidget
from ..utilities import macro

class PyDMFrame(QFrame, PyDMWidget):
    """
    QFrame with support for alarms
    This class inherits from QFrame and PyDMWidget.

    Parameters
    ----------
    parent : QWidget
        The parent widget for the Label
    init_channel : str, optional
        The channel to be used by the widget.
    """

    def __init__(self, parent=None, init_channel=None):
        QFrame.__init__(self, parent)
        PyDMWidget.__init__(self, init_channel=init_channel)
        self._macros = None
        self._disable_on_disconnect = False
        self.alarmSensitiveBorder = False

    @Property(str)
    def macros(self):
        """
        JSON-formatted string containing macro variables to pass to the embedded file.

        Returns
        -------
        str
        """
        if self._macros is None:
            return ""
        return self._macros

    @macros.setter
    def macros(self, new_macros):
        """
        JSON-formatted string containing macro variables to pass to the embedded file.

        .. warning::
        If the macros property is not defined before the filename property,
        The widget will not have any macros defined when it loads the embedded file.
        This behavior will be fixed soon.

        Parameters
        ----------
        new_macros : str
        """
        new_macros = str(new_macros)
        if new_macros != self._macros:
            self._macros = new_macros
           
    @Property(bool)
    def disableOnDisconnect(self):
        """
        Whether or not the PyDMFrame should be disabled in case the
        channel is disconnected.

        Returns
        -------
        disable : bool
            The configured value
        """
        return self._disable_on_disconnect

    @disableOnDisconnect.setter
    def disableOnDisconnect(self, new_val):
        """
        Whether or not the PyDMFrame should be disabled in case the
        channel is disconnected.

        Parameters
        ----------
        new_val : bool
            The new configuration to use
        """
        if self._disable_on_disconnect != bool(new_val):
            self._disable_on_disconnect = new_val
            self.check_enable_state()

    def check_enable_state(self):
        """
        Checks whether or not the widget should be disable.
        This method also disables the widget and add a Tool Tip
        with the reason why it is disabled.
        """
        if hasattr(self, "_disable_on_disconnect") and self._disable_on_disconnect:
            PyDMWidget.check_enable_state(self)
        else:
            self.setEnabled(True)
