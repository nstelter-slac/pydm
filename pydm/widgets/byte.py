from qtpy.QtWidgets import QWidget, QTabWidget, QGridLayout, QLabel, QStyle, QStyleOption
from qtpy.QtGui import QColor, QPen, QFontMetrics, QPainter, QPaintEvent, QBrush
from qtpy.QtCore import Property, Qt, QSize, QPoint
from typing import List, Optional
from .base import PyDMWidget


class PyDMBitIndicator(QWidget):
    """
    A QWidget which draws a colored circle or rectangle

    Parameters
    ----------
    parent : QWidget
        The parent widget for the Label

    """
    def __init__(self, parent: Optional[QWidget] = None, circle: bool = False):
        super(PyDMBitIndicator, self).__init__(parent)
        self.circle = circle
        self._painter = QPainter()
        self._brush = QBrush(Qt.SolidPattern)
        self._pen = QPen(Qt.SolidLine)

    def paintEvent(self, event: QPaintEvent) -> None:
        """
        Paint events are sent to widgets that need to update themselves,
        for instance when part of a widget is exposed because a covering
        widget was moved.

        Parameters
        ----------
        event : QPaintEvent
        """
        self._painter.begin(self)
        opt = QStyleOption()
        opt.initFrom(self)
        self.style().drawPrimitive(QStyle.PE_Widget, opt, self._painter, self)
        self._painter.setRenderHint(QPainter.Antialiasing)
        self._painter.setBrush(self._brush)
        self._painter.setPen(self._pen)
        if self.circle:
            rect = self.rect()
            w = rect.width()
            h = rect.height()
            r = int(min(w, h) / 2.0 - 2.0 * max(self._pen.widthF(), 1.0))
            self._painter.drawEllipse(QPoint(w // 2, h // 2), r, r)
        else:
            self._painter.drawRect(self.rect())
        self._painter.end()

    def setColor(self, color: QColor) -> None:
        """
        Property for the color to be used when drawing

        Parameters
        ----------
        QColor
        """
        self._brush.setColor(color)
        self.update()

    def minimumSizeHint(self) -> QSize:
        fm = QFontMetrics(self.font())
        return QSize(fm.height(), fm.height())

class PyDMMultiStateLEDIndicator(QWidget, PyDMWidget):
    """
    Widget for graphical representation of bits from an integer number
    with support for Channels and more from PyDM

    Parameters
    ----------
    parent : QWidget
        The parent widget for the Label
    init_channel : str, optional
        The channel to be used by the widget.
    """
    def __init__(self, parent: Optional[QWidget] = None, init_channel=None):
        QWidget.__init__(self, parent)
        PyDMWidget.__init__(self, init_channel=init_channel)
        self._state_colors = [QColor(Qt.black)] * 16
        self._additional_channels = [''] * 3
        self._painter = QPainter()
        self._brush = QBrush(Qt.SolidPattern)
        self._pen = QPen(Qt.SolidLine)
        self.circle = True
        self._curr_state = 0
    '''
    def connection_changed(self, connected: bool) -> None:
        """
        Callback invoked when the connection state of the Channel is changed.
        This callback acts on the connection state to enable/disable the widget
        and also trigger the change on alarm severity to ALARM_DISCONNECTED.

        Parameters
        ----------
        connected : bool
            When this value is False the channel is disconnected, True otherwise.
        """
        super(PyDMByteIndicator, self).connection_changed(connected)
    '''
    def value_changed(self, new_val: int) -> None:
        """
        Callback invoked when the Channel value is changed.

        Parameters
        ----------
        new_val : int
            The new value from the channel.
        """
        print("updating curr state: ", new_val)
        super(PyDMMultiStateLEDIndicator, self).value_changed(new_val)
        try:
            int(new_val)
            if new_val < 16: # 15 is max since we start counting from 0
                self._curr_state = new_val
                self.update()
        except:
            pass

    @Property(bool)
    def fourChannelInput(self):
        return self.fourChannelInput

    @fourChannelInput.setter
    def fourChannelInput(self, enable_four_channel_input: bool) -> None:
        if enable_four_channel_input != self.fourChannelInput:
            self.fourChannelInput = enable_four_channel_input

    @Property('QStringList', designable=False)
    def fourChannels(self) -> str:
        """
        The color for when widget is in 16th state

        Returns
        -------
        QColor
        """
        return self._additional_channels[0]

    @fourChannels.setter
    def fourChannels(self, new_channel: str) -> None:
        """
        The color for when widget is in 16th state

        Parameters
        ----------
        new_color : QColor
        """
        if new_channel != self._additional_channels[0]:
            self._additional_channels[0] = new_channel

    @Property(QColor)
    def state1Color(self) -> QColor:
        """
        The color for when widget is in 1st state

        Returns
        -------
        QColor
        """
        return self._state_colors[0]

    @state1Color.setter
    def state1Color(self, state_color: QColor) -> None:
        """
        The color for when widget is in 1st state

        Parameters
        ----------
        new_color : QColor
        """
        if state_color != self._state_colors[0]:
            self._state_colors[0] = state_color

    @Property(QColor)
    def state2Color(self) -> QColor:
        """
        The color for when widget is in 2nd state

        Returns
        -------
        QColor
        """
        return self._state_colors[1]

    @state2Color.setter
    def state2Color(self, new_color: QColor) -> None:
        """
        The color for when widget is in 2nd state

        Parameters
        ----------
        new_color : QColor
        """
        if new_color != self._state_colors[1]:
            self._state_colors[1] = new_color

    @Property(QColor)
    def state3Color(self) -> QColor:
        """
        The color for when widget is in 3rd state

        Returns
        -------
        QColor
        """
        return self._state_colors[2]

    @state3Color.setter
    def state3Color(self, new_color: QColor) -> None:
        """
        The color for when widget is in 3rd state

        Parameters
        ----------
        new_color : QColor
        """
        if new_color != self._state_colors[3]:
            self._state_colors[2] = new_color
                        
    @Property(QColor)
    def state4Color(self) -> QColor:
        """
        The color for when widget is in 4th state

        Returns
        -------
        QColor
        """
        return self._state_colors[3]

    @state4Color.setter
    def state4Color(self, new_color: QColor) -> None:
        """
        The color for when widget is in 4th state

        Parameters
        ----------
        new_color : QColor
        """
        if new_color != self._state_colors[4]:
            self._state_colors[3] = new_color
            
    @Property(QColor)
    def state5Color(self) -> QColor:
        """
        The color for when widget is in 5th state

        Returns
        -------
        QColor
        """
        return self._state_colors[4]

    @state5Color.setter
    def state5Color(self, new_color: QColor) -> None:
        """
        The color for when widget is in 5th state

        Parameters
        ----------
        new_color : QColor
        """
        if new_color != self._state_colors[4]:
            self._state_colors[4] = new_color

    @Property(QColor)
    def state6Color(self) -> QColor:
        """
        The color for when widget is in 6th state

        Returns
        -------
        QColor
        """
        return self._state_colors[5]

    @state6Color.setter
    def state6Color(self, new_color: QColor) -> None:
        """
        The color for when widget is in 6th state

        Parameters
        ----------
        new_color : QColor
        """
        if new_color != self._state_colors[5]:
            self._state_colors[5] = new_color
                      
    @Property(QColor)
    def state7Color(self) -> QColor:
        """
        The color for when widget is in 7th state

        Returns
        -------
        QColor
        """
        return self._state_colors[6]

    @state7Color.setter
    def state7Color(self, new_color: QColor) -> None:
        """
        The color for when widget is in 7th state

        Parameters
        ----------
        new_color : QColor
        """
        if new_color != self._state_colors[6]:
            self._state_colors[6] = new_color
            
    @Property(QColor)
    def state8Color(self) -> QColor:
        """
        The color for when widget is in 8th state

        Returns
        -------
        QColor
        """
        return self._state_colors[7]

    @state8Color.setter
    def state8Color(self, new_color: QColor) -> None:
        """
        The color for when widget is in 8th state

        Parameters
        ----------
        new_color : QColor
        """
        if new_color != self._state_colors[7]:
            self._state_colors[7] = new_color

    @Property(QColor)
    def state9Color(self) -> QColor:
        """
        The color for when widget is in 9th state

        Returns
        -------
        QColor
        """
        return self._state_colors[8]

    @state9Color.setter
    def state9Color(self, new_color: QColor) -> None:
        """
        The color for when widget is in 9th state

        Parameters
        ----------
        new_color : QColor
        """
        if new_color != self._state_colors[8]:
            self._state_colors[8] = new_color

    @Property(QColor)
    def state10Color(self) -> QColor:
        """
        The color for when widget is in 10th state

        Returns
        -------
        QColor
        """
        return self._state_colors[9]

    @state10Color.setter
    def state10Color(self, new_color: QColor) -> None:
        """
        The color for when widget is in 10th state

        Parameters
        ----------
        new_color : QColor
        """
        if new_color != self._state_colors[9]:
            self._state_colors[9] = new_color
                        
    @Property(QColor)
    def state11Color(self) -> QColor:
        """
        The color for when widget is in 11th state

        Returns
        -------
        QColor
        """
        return self._state_colors[10]

    @state11Color.setter
    def state11Color(self, new_color: QColor) -> None:
        """
        The color for when widget is in 11th state

        Parameters
        ----------
        new_color : QColor
        """
        if new_color != self._state_colors[10]:
            self._state_colors[10] = new_color
            
    @Property(QColor)
    def state12Color(self) -> QColor:
        """
        The color for when widget is in 12th state

        Returns
        -------
        QColor
        """
        return self._state_colors[11]

    @state12Color.setter
    def state12Color(self, new_color: QColor) -> None:
        """
        The color for when widget is in 12th state

        Parameters
        ----------
        new_color : QColor
        """
        if new_color != self._state_colors[11]:
            self._state_colors[11] = new_color

    @Property(QColor)
    def state13Color(self) -> QColor:
        """
        The color for when widget is in 13th state

        Returns
        -------
        QColor
        """
        return self._state_colors[12]

    @state13Color.setter
    def state13Color(self, new_color: QColor) -> None:
        """
        The color for when widget is in 13th state

        Parameters
        ----------
        new_color : QColor
        """
        if new_color != self._state_colors[12]:
            self._state_colors[12] = new_color
            
    @Property(QColor)
    def state14Color(self) -> QColor:
        """
        The color for when widget is in 14th state

        Returns
        -------
        QColor
        """
        return self._state_colors[13]

    @state14Color.setter
    def state14Color(self, new_color: QColor) -> None:
        """
        The color for when widget is in 14th state

        Parameters
        ----------
        new_color : QColor
        """
        if new_color != self._state_colors[13]:
            self._state_colors[13] = new_color
    
    @Property(QColor)
    def state15Color(self) -> QColor:
        """
        The color for when widget is in 15th state

        Returns
        -------
        QColor
        """
        return self._state_colors[14]

    @state15Color.setter
    def state15Color(self, state_color: QColor) -> None:
        """
        The color for when widget is in 15th state

        Parameters
        ----------
        new_color : QColor
        """
        if state_color != self._state_colors[14]:
            self._state_colors[14] = state_color

    @Property(QColor)
    def state16Color(self) -> QColor:
        """
        The color for when widget is in 16th state

        Returns
        -------
        QColor
        """
        return self._state_colors[15]

    @state16Color.setter
    def state16Color(self, state_color: QColor) -> None:
        """
        The color for when widget is in 16th state

        Parameters
        ----------
        state_color : QColor
        """
        if state_color != self._state_colors[15]:
            self._state_colors[15] = state_color
                        
            
    def paintEvent(self, event: QPaintEvent) -> None:
        """
        Paint events are sent to widgets that need to update themselves,
        for instance when part of a widget is exposed because a covering
        widget was moved.

        At PyDMDrawing this method handles the alarm painting with parameters
        from the stylesheet, configures the brush, pen and calls ```draw_item```
        so the specifics can be performed for each of the drawing classes.

        Parameters
        ----------
        event : QPaintEvent
        """
        #super(PyDMMultiStateLEDIndicator, self).paintEvent(QPaintEvent)

        #print("drawing curr state: ", self._curr_state)
        self._painter.begin(self)
        opt = QStyleOption()
        opt.initFrom(self)
        self.style().drawPrimitive(QStyle.PE_Widget, opt, self._painter, self)
        self._painter.setRenderHint(QPainter.Antialiasing)
        self._painter.setBrush(QBrush(self._state_colors[self._curr_state]))
        self._painter.setPen(QPen(Qt.red))
        if self.circle:
            rect = self.rect()
            w = rect.width()
            h = rect.height()
            r = int(min(w, h) / 2.0 - 2.0 * max(self._pen.widthF(), 1.0))
            self._painter.drawEllipse(QPoint(w // 2, h // 2), r, r)
        else:
            self._painter.drawRect(self.rect())
        self._painter.end()
        
class PyDMByteIndicator(QWidget, PyDMWidget):
    """
    Widget for graphical representation of bits from an integer number
    with support for Channels and more from PyDM

    Parameters
    ----------
    parent : QWidget
        The parent widget for the Label
    init_channel : str, optional
        The channel to be used by the widget.
    """
    def __init__(self, parent: Optional[QWidget] = None, init_channel=None):
        QWidget.__init__(self, parent)
        PyDMWidget.__init__(self, init_channel=init_channel)
        self.value = 0
        self.setLayout(QGridLayout(self))

        self._on_color = QColor(0, 255, 0)
        self._off_color = QColor(100, 100, 100)
        self._disconnected_color = QColor(255, 255, 255)
        self._invalid_color = QColor(255, 0, 255)

        self._pen_style = Qt.SolidLine
        self._line_pen = QPen(self._pen_style)

        self._orientation = Qt.Vertical

        # This is kind of ridiculous, importing QTabWidget just to get a 4-item enum thats usable in Designer.
        # PyQt5 lets you define custom enums that you can use in designer with QtCore.Q_ENUMS(), doesn't exist in PyQt4.
        self._labels = []
        self._show_labels = True
        self._label_position = QTabWidget.East

        self._num_bits = 1

        self._indicators = []
        self._circles = False
        self.set_spacing()
        self.layout().setOriginCorner(Qt.TopLeftCorner)

        self._big_endian = False
        self._shift = 0
        self.numBits = 1  # Need to set the property to initialize
        # _labels and _indicators setting numBits there also performs
        # the first rebuild_layout.

    def init_for_designer(self) -> None:
        """
        Method called after the constructor to tweak configurations for
        when using the widget with the Qt Designer
        """
        self._connected = True
        self.value = 5
        self.update_indicators()

    def connection_changed(self, connected: bool) -> None:
        """
        Callback invoked when the connection state of the Channel is changed.
        This callback acts on the connection state to enable/disable the widget
        and also trigger the change on alarm severity to ALARM_DISCONNECTED.

        Parameters
        ----------
        connected : bool
            When this value is False the channel is disconnected, True otherwise.
        """
        super(PyDMByteIndicator, self).connection_changed(connected)
        self.update_indicators()

    def rebuild_layout(self) -> None:
        """
        Method to reorganize the top-level widget and its contents
        according to the layout property values.
        """
        self.clear()
        pairs = zip(self._labels, self._indicators)
        # Hide labels until they are in the layout
        for label in self._labels:
            label.setVisible(False)
        # This is a horrendous mess of if statements
        # for every possible case.  Ugh.
        # There is probably a more clever way to do this.
        if self.orientation == Qt.Vertical:
            for i, (label, indicator) in enumerate(pairs):
                if self.labelPosition == QTabWidget.East:
                    self.layout().addWidget(indicator, i, 0)
                    self.layout().addWidget(label, i, 1, 1, 1, Qt.AlignVCenter)
                    label.setVisible(self._show_labels)
                elif self.labelPosition == QTabWidget.West:
                    self.layout().addWidget(label, i, 0, 1, 1, Qt.AlignVCenter)
                    self.layout().addWidget(indicator, i, 1)
                    label.setVisible(self._show_labels)
                else:
                    self.layout().addWidget(indicator, i, 0)
                    # Invalid combo of orientation and label position,
                    # so we don't reset label visibility here.
        elif self.orientation == Qt.Horizontal:
            for i, (label, indicator) in enumerate(pairs):
                if self.labelPosition == QTabWidget.North:
                    self.layout().addWidget(label, 0, i, 1, 1, Qt.AlignHCenter)
                    self.layout().addWidget(indicator, 1, i)
                    label.setVisible(self._show_labels)
                elif self.labelPosition == QTabWidget.South:
                    self.layout().addWidget(indicator, 0, i)
                    self.layout().addWidget(label, 1, i, 1, 1, Qt.AlignHCenter)
                    label.setVisible(self._show_labels)
                else:
                    self.layout().addWidget(indicator, 0, i)
                    # Invalid combo of orientation and label position, so
                    # we don't reset label visibility here.
        self.update_indicators()

    def clear(self) -> None:
        """
        Remove all inner widgets from the layout
        """
        for col in range(0, self.layout().columnCount()):
            for row in range(0, self.layout().rowCount()):
                item = self.layout().itemAtPosition(row, col)
                if item is not None:
                    w = item.widget()
                    if w is not None:
                        self.layout().removeWidget(w)

    def update_indicators(self) -> None:
        """
        Update the inner bit indicators accordingly with the new value.
        """
        if self._shift < 0:
            value = int(self.value) << abs(self._shift)
        else:
            value = int(self.value) >> self._shift
        if value < 0:
            value = 0

        bits = [(value >> i) & 1
                for i in range(self._num_bits)]
        for bit, indicator in zip(bits, self._indicators):
            if self._connected:
                if self._alarm_state == 3:
                    c = self._invalid_color
                else:
                    c = self._on_color if bit else self._off_color
            else:
                c = self._disconnected_color
            indicator.setColor(c)

    @Property(QColor)
    def onColor(self) -> QColor:
        """
        The color for a bit in the 'on' state.

        Returns
        -------
        QColor
        """
        return self._on_color

    @onColor.setter
    def onColor(self, new_color: QColor) -> None:
        """
        The color for a bit in the 'on' state.

        Parameters
        ----------
        new_color : QColor
        """
        if new_color != self._on_color:
            self._on_color = new_color
            self.update_indicators()

    @Property(QColor)
    def offColor(self) -> QColor:
        """
        The color for when widget is in 16th state

        Returns
        -------
        QColor
        """
        return self._off_color

    @offColor.setter
    def offColor(self, new_color: QColor) -> None:
        """
        The color for when widget is in 16th state

        Parameters
        ----------
        new_color : QColor
        """
        if new_color != self._off_color:
            self._off_color = new_color
            self.update_indicators()

    @Property(Qt.Orientation)
    def orientation(self) -> Qt.Orientation:
        """
        Whether to lay out the bit indicators vertically or horizontally.

        Returns
        -------
        int
        """
        return self._orientation

    @orientation.setter
    def orientation(self, new_orientation: Qt.Orientation) -> None:
        """
        Whether to lay out the bit indicators vertically or horizontally.

        Parameters
        -------
        new_orientation : Qt.Orientation, int
        """
        self._orientation = new_orientation
        self.set_spacing()
        self.rebuild_layout()

    def set_spacing(self) -> None:
        """
        Configures the correct spacing given the selected orientation.
        """
        label_spacing = 5
        if self._circles:
            indicator_spacing = 5
        else:
            indicator_spacing = 0

        self.layout().setContentsMargins(0, 0, 0, 0)

        if self._orientation == Qt.Horizontal:
            self.layout().setHorizontalSpacing(indicator_spacing)
            self.layout().setVerticalSpacing(label_spacing)
        elif self._orientation == Qt.Vertical:
            self.layout().setHorizontalSpacing(label_spacing)
            self.layout().setVerticalSpacing(indicator_spacing)

    @Property(bool)
    def showLabels(self) -> bool:
        """
        Whether or not to show labels next to each bit indicator.

        Returns
        -------
        bool
        """
        return self._show_labels

    @showLabels.setter
    def showLabels(self, show: bool) -> None:
        """
        Whether or not to show labels next to each bit indicator.

        Parameters
        -------
        show : bool
            If True the widget will show a label next to the bit indicator
        """
        self._show_labels = show
        for label in self._labels:
            label.setVisible(show)

    @Property(bool)
    def bigEndian(self) -> bool:
        """
        Whether the most significant bit is at the start or end of the widget.

        Returns
        -------
        bool
        """
        return self._big_endian

    @bigEndian.setter
    def bigEndian(self, is_big_endian: bool) -> None:
        """
        Whether the most significant bit is at the start or end of the widget.

        Parameters
        -------
        is_big_endian : bool
            If True, the Big Endian will be used, Little Endian otherwise
        """
        self._big_endian = is_big_endian

        origin_map = {(Qt.Vertical, True): Qt.BottomLeftCorner,
                      (Qt.Vertical, False): Qt.TopLeftCorner,
                      (Qt.Horizontal, True): Qt.TopRightCorner,
                      (Qt.Horizontal, False): Qt.TopLeftCorner}

        origin = origin_map[(self.orientation, self.bigEndian)]
        self.layout().setOriginCorner(origin)
        self.rebuild_layout()

    @Property(bool)
    def circles(self) -> bool:
        """
        Draw indicators as circles, rather than rectangles.

        Returns
        -------
        bool
        """
        return self._circles

    @circles.setter
    def circles(self, draw_circles: bool) -> None:
        """
        Draw indicators as circles, rather than rectangles.

        Parameters
        ----------
        draw_circles : bool
            If True, bits will be represented as circles
        """
        self._circles = draw_circles
        self.set_spacing()
        for indicator in self._indicators:
            indicator.circle = self._circles
        self.update_indicators()

    @Property(QTabWidget.TabPosition)
    def labelPosition(self) -> QTabWidget.TabPosition:
        """
        The side of the widget to display labels on.

        Returns
        -------
        int
        """
        return self._label_position

    @labelPosition.setter
    def labelPosition(self, new_pos: QTabWidget.TabPosition) -> None:
        """
        The side of the widget to display labels on.

        Parameters
        ----------
        new_pos : QTabWidget.TabPosition, int
        """
        self._label_position = new_pos
        self.rebuild_layout()

    @Property(int)
    def numBits(self) -> int:
        """
        Number of bits to interpret.

        Returns
        -------
        int
        """
        return self._num_bits

    @numBits.setter
    def numBits(self, new_num_bits: int) -> None:
        """
        Number of bits to interpret.

        Parameters
        ----------
        new_num_bits : int
        """
        if new_num_bits < 1:
            return
        self._num_bits = new_num_bits
        for indicator in self._indicators:
            indicator.deleteLater()
        self._indicators = [PyDMBitIndicator(parent=self, circle=self.circles)
                            for i in range(0, self._num_bits)]
        old_labels = self.labels
        new_labels = ["Bit {}".format(i) for i in range(0, self._num_bits)]
        for i, old_label in enumerate(old_labels):
            if i >= self._num_bits:
                break
            new_labels[i] = old_label
        self.labels = new_labels

    @Property(int)
    def shift(self) -> int:
        """
        Bit shift.

        Returns
        -------
        int
        """
        return self._shift

    @shift.setter
    def shift(self, new_shift: int) -> None:
        """
        Bit shift.

        Parameters
        ----------
        new_shift : int
        """
        self._shift = new_shift
        self.update_indicators()

    @Property('QStringList')
    def labels(self) -> List[str]:
        """
        Labels for each bit.

        Returns
        -------
        list
        """
        return [str(l.text()) for l in self._labels]

    @labels.setter
    def labels(self, new_labels: List[str]) -> None:
        """
        Labels for each bit.

        Parameters
        ----------
        new_labels : list
        """
        for label in self._labels:
            label.hide()
            label.deleteLater()
        self._labels = [QLabel(text, parent=self) for text in new_labels]
        # Have to reset showLabels to hide or show all the new labels we just made.
        self.showLabels = self._show_labels
        self.rebuild_layout()

    def value_changed(self, new_val: int) -> None:
        """
        Callback invoked when the Channel value is changed.

        Parameters
        ----------
        new_val : int
            The new value from the channel.
        """
        super(PyDMByteIndicator, self).value_changed(new_val)
        try:
            int(new_val)
            self.update_indicators()
        except:
            pass

    def paintEvent(self, _) -> None:
        """
        Paint events are sent to widgets that need to update themselves,
        for instance when part of a widget is exposed because a covering
        widget was moved.

        At PyDMDrawing this method handles the alarm painting with parameters
        from the stylesheet, configures the brush, pen and calls ```draw_item```
        so the specifics can be performed for each of the drawing classes.

        Parameters
        ----------
        event : QPaintEvent
        """
        painter = QPainter(self)
        opt = QStyleOption()
        opt.initFrom(self)
        self.style().drawPrimitive(QStyle.PE_Widget, opt, painter, self)
        painter.setRenderHint(QPainter.Antialiasing)

    def alarm_severity_changed(self, new_alarm_severity: int) -> None:
        """
        Callback invoked when the Channel alarm severity is changed.

        Parameters
        ----------
        new_alarm_severity : int
            The new severity where 0 = NO_ALARM, 1 = MINOR, 2 = MAJOR
            and 3 = INVALID
        """

        if new_alarm_severity == self._alarm_state:
            return
        else:
            super(PyDMByteIndicator, self).alarm_severity_changed(new_alarm_severity)

            # Checks if _shift attribute exits because base class can call method
            # before the object constructor is complete
            if hasattr(self, '_shift'):
                self.update_indicators()
