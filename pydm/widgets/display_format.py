import math
import numpy as np
from typing import Any
import logging
import warnings

from pydm.utilities import ACTIVE_QT_WRAPPER, QtWrapperTypes

logger = logging.getLogger(__name__)


class DisplayFormat(object):
    """Display format for showing data in a PyDM widget."""

    #: The default display format.
    Default = 0
    #: Show the data as a string.
    String = 1
    #: Show numerical values as floating point (base 10, decimal) values.
    Decimal = 2
    #: Show numerical values in scientific / exponential notation.
    Exponential = 3
    #: Show numerical values in base 16 (hexadecimal) notation.
    Hex = 4
    #: Show numerical values in base 2 (binary) notation.
    Binary = 5


if ACTIVE_QT_WRAPPER == QtWrapperTypes.PYSIDE6:
    from PySide6.QtCore import QEnum
    from enum import Enum

    @QEnum
    # overrides prev enum def
    class DisplayFormat(Enum):  # noqa F811
        Default = 0
        String = 1
        Decimal = 2
        Exponential = 3
        Hex = 4
        Binary = 5


def parse_value_for_display(
    value: Any,
    precision: int,
    display_format_type: int = DisplayFormat.Default,
    string_encoding: str = "utf_8",
    widget=None,
):
    """
    Format a value to show it in a widget, based on the display format type.

    Parameters
    ----------
    value : Any
        The value to convert to a string.
    precision : int
        Precision of floating point values to use.
    display_format_type : int, optional
        Display format type to use.
    string_encoding : str, optional
        Encoding to use for strings.
    widget : QtWidgets.QWidget, optional
        Widget to get a name from for conversion errors.

    Returns
    -------
    str
        Formatted version of ``value``.
    """
    if value is None:
        return ""
    try:
        widget_name = widget.objectName()
    except (AttributeError, TypeError):
        widget_name = ""

    if display_format_type == DisplayFormat.Default:
        return value
    elif display_format_type == DisplayFormat.String:
        if isinstance(value, np.ndarray):
            try:
                # Stop at the first zero (EPICS convention)
                # Assume the ndarray is one-dimensional
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    zeros = np.where(value == 0)[0]
                if zeros.size > 0:
                    value = value[: zeros[0]]
                r = value.tobytes().decode(string_encoding)
            except Exception:
                logger.error(
                    "Could not decode {0} using {1} at widget named '{2}'.".format(value, string_encoding, widget_name)
                )
                return value
            return r
        else:
            return value
    elif display_format_type == DisplayFormat.Decimal:
        # This case is taken care by the current string formatting
        # routine
        return value
    elif display_format_type == DisplayFormat.Exponential:
        fmt_string = "{" + ":.{}e".format(precision) + "}"
        try:
            r = fmt_string.format(value)
        except (ValueError, TypeError):
            logger.error(
                "Could not display value '{0}' using displayFormat 'Exponential' at widget named '{1}'.".format(
                    value, widget_name
                )
            )
            r = value
        return r
    elif display_format_type == DisplayFormat.Hex:
        try:
            r = hex(int(math.floor(value)))
        except (ValueError, TypeError):
            logger.error(
                "Could not display value '{0}' using displayFormat 'Hex' at widget named '{1}'.".format(
                    value, widget_name
                )
            )
            r = value
        return r
    elif display_format_type == DisplayFormat.Binary:
        try:
            r = bin(int(math.floor(value)))
        except (ValueError, TypeError):
            logger.error(
                "Could not display value '{0}' using displayFormat 'Binary' at widget named '{1}'.".format(
                    value, widget_name
                )
            )
            r = value
        return r
