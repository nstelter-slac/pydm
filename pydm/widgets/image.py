from qtpy.QtWidgets import QActionGroup
from qtpy.QtCore import Signal, Slot, Property, QTimer, QThread
from pyqtgraph import ImageView, PlotItem
from pyqtgraph import ColorMap
from pyqtgraph.graphicsItems.ViewBox.ViewBoxMenu import ViewBoxMenu
import numpy as np
import logging
from .channel import PyDMChannel
from .colormaps import cmaps, cmap_names, PyDMColorMap
from .base import PyDMWidget, PostParentClassInitSetup
from pydm.utilities import ACTIVE_QT_WRAPPER, QtWrapperTypes

logger = logging.getLogger(__name__)


class ReadingOrder(object):
    """Class to build ReadingOrder ENUM property."""

    Fortranlike = 0
    Clike = 1


if ACTIVE_QT_WRAPPER == QtWrapperTypes.PYSIDE6:
    from PySide6.QtCore import QEnum
    from enum import Enum

    @QEnum
    # overrides prev enum def
    class ReadingOrder(Enum):  # noqa F811
        Fortranlike = 0
        Clike = 1


class DimensionOrder(object):
    """
    Class to build DimensionOrder ENUM property.

    This relates to how the pva image data is being sent. Included in this data are the dimensions of the
    image (width and height) as part of the array 'dimension_t[] dimension'.
    (https://github.com/epics-base/normativeTypesCPP/wiki/Normative+Types+Specification#ntndarray)
    But if the array should be ordered [height, width] or [width, height] does not seem to be specified.
    This option lets the user set which ordering PyDM should interpret this 'dimension' array as having.

    HeightFirst = [height, width]
    WidthFirst = [width, height]
    (PyDM assumes HeightFirst as default)

    If you are wondering what ordering a certain pva address is using, you can 'pvget' the address
    to see the ordering of values in its 'dimension' array.
    """

    HeightFirst = 0
    WidthFirst = 1


if ACTIVE_QT_WRAPPER == QtWrapperTypes.PYSIDE6:
    from PySide6.QtCore import QEnum
    from enum import Enum

    @QEnum
    # overrides prev enum def
    class DimensionOrder(Enum):  # noqa F811
        HeightFirst = 0
        WidthFirst = 1


class ImageUpdateThread(QThread):
    updateSignal = Signal(list)

    def __init__(self, image_view):
        QThread.__init__(self)
        self.image_view = image_view

    def run(self):
        img = self.image_view.image_waveform

        if self.image_view._dimension_order == DimensionOrder.WidthFirst:
            shape = img.shape
            # numpy reshape asks for (height, width) as it's params,
            # and if we know our 'img.shape' is ordered [width, height],
            # we must pass reshape(height, width) which is (shape[1], shape[0])
            img = img.reshape(shape[1], shape[0])

        needs_redraw = self.image_view.needs_redraw
        image_dimensions = len(img.shape)
        width = self.image_view.imageWidth
        reading_order = self.image_view.readingOrder
        normalize_data = self.image_view._normalize_data
        cm_min = self.image_view.cm_min
        cm_max = self.image_view.cm_max

        if not needs_redraw:
            logging.debug("ImageUpdateThread - needs redraw is False. Aborting.")
            return
        if image_dimensions == 1:
            if width < 1:
                # We don't have a width for this image yet, so we can't draw it
                logging.debug("ImageUpdateThread - no width available. Aborting.")
                return
            try:
                if reading_order == ReadingOrder.Clike:
                    img = img.reshape((-1, width), order="C")
                else:
                    img = img.reshape((width, -1), order="F")
            except ValueError:
                logger.error("Invalid width for image during reshape: %d", width)

        if len(img) <= 0:
            return
        logging.debug("ImageUpdateThread - Will Process Image")
        img = self.image_view.process_image(img)
        if normalize_data:
            mini = img.min()
            maxi = img.max()
        else:
            mini = cm_min
            maxi = cm_max
        logging.debug("ImageUpdateThread - Emit Update Signal")
        self.updateSignal.emit([mini, maxi, img])
        logging.debug("ImageUpdateThread - Set Needs Redraw -> False")
        self.image_view.needs_redraw = False


class PyDMImageView(ImageView, PyDMWidget):
    """
    A PyQtGraph ImageView with support for Channels and more from PyDM.

    If there is no :attr:`channelWidth` it is possible to define the width of
    the image with the :attr:`width` property.

    The :attr:`normalizeData` property defines if the colors of the images are
    relative to the :attr:`colorMapMin` and :attr:`colorMapMax` property or to
    the minimum and maximum values of the image.

    Use the :attr:`newImageSignal` to hook up to a signal that is emitted when a new
    image is rendered in the widget.

    Parameters
    ----------
    parent : QWidget
        The parent widget for the Label
    image_channel : str, optional
        The channel to be used by the widget for the image data.
    width_channel : str, optional
        The channel to be used by the widget to receive the image width
        information
    """

    ReadingOrder = ReadingOrder
    DimensionOrder = DimensionOrder

    if ACTIVE_QT_WRAPPER == QtWrapperTypes.PYQT5:
        from PyQt5.QtCore import Q_ENUM

        Q_ENUM(ReadingOrder)
        Q_ENUM(DimensionOrder)
        Q_ENUM(PyDMColorMap)

    # Make enum definitions known to this class
    Fortranlike = ReadingOrder.Fortranlike
    Clike = ReadingOrder.Clike

    HeightFirst = DimensionOrder.HeightFirst
    WidthFirst = DimensionOrder.WidthFirst

    Magma = PyDMColorMap.Magma
    Inferno = PyDMColorMap.Inferno
    Plasma = PyDMColorMap.Plasma
    Viridis = PyDMColorMap.Viridis
    Jet = PyDMColorMap.Jet
    Monochrome = PyDMColorMap.Monochrome
    Hot = PyDMColorMap.Hot

    color_maps = cmaps

    def __init__(self, parent=None, image_channel=None, width_channel=None):
        """Initialize widget."""
        # Set the default colormap.
        self._colormap = PyDMColorMap.Inferno
        self._cm_colors = None
        self._imagechannel = None
        self._widthchannel = None
        self.image_waveform = np.zeros(0)
        self._image_width = 0
        self._normalize_data = False
        self._auto_downsample = True
        self._show_axes = False

        # Set default reading order of numpy array data to Fortranlike.
        self._reading_order = ReadingOrder.Fortranlike
        self._dimension_order = DimensionOrder.HeightFirst

        self._redraw_rate = 30

        # Set color map limits.
        self.cm_min = 0.0
        self.cm_max = 255.0

        plot_item = PlotItem()
        ImageView.__init__(self, parent, view=plot_item)
        PyDMWidget.__init__(self)
        self._channels = [None, None]
        self.thread = None
        self.axes = dict({"t": None, "x": 0, "y": 1, "c": None})
        self.showAxes = self._show_axes
        self.imageItem.setOpts(axisOrder="row-major")

        # Hide some items of the widget.
        self.ui.histogram.hide()
        self.getImageItem().sigImageChanged.disconnect(self.ui.histogram.imageChanged)
        self.ui.roiBtn.hide()
        self.ui.menuBtn.hide()

        # Make a right-click menu for changing the color map.
        self.cm_group = QActionGroup(self)
        self.cmap_for_action = {}
        for cm in self.color_maps:
            action = self.cm_group.addAction(cmap_names[cm])
            action.setCheckable(True)
            self.cmap_for_action[action] = cm

        self.colorMap = self._colormap

        # Setup the redraw timer.
        self.needs_redraw = False
        self.redraw_timer = QTimer(self)
        self.redraw_timer.timeout.connect(self.redrawImage)
        self.maxRedrawRate = self._redraw_rate
        self.newImageSignal = self.getImageItem().sigImageChanged
        # Set live channels if requested on initialization
        if image_channel:
            self.imageChannel = image_channel or ""
        if width_channel:
            self.widthChannel = width_channel or ""
        # Execute setup calls that must be done here in the widget class's __init__,
        # and after it's parent __init__ calls have completed.
        # (so we can avoid pyside6 throwing an error, see func def for more info)
        PostParentClassInitSetup(self)

    # On pyside6, we need to expilcity call pydm's base class's eventFilter() call or events
    # will not propagate to the parent classes properly.
    def eventFilter(self, obj, event):
        return PyDMWidget.eventFilter(self, obj, event)

    @Property(str, designable=False)
    def channel(self):
        return

    @channel.setter
    def channel(self, ch):
        if not ch:
            return
        logger.info("Use the imageChannel property with the ImageView widget.")
        return

    def widget_ctx_menu(self):
        """
        Fetch the Widget specific context menu.

        It will be populated with additional tools by `assemble_tools_menu`.

        Returns
        -------
        QMenu or None
            If the return of this method is None a new QMenu will be created by
            `assemble_tools_menu`.
        """
        self.menu = ViewBoxMenu(self.getView().getViewBox())
        cm_menu = self.menu.addMenu("Color Map")
        for act in self.cmap_for_action.keys():
            cm_menu.addAction(act)
        cm_menu.triggered.connect(self._changeColorMap)
        return self.menu

    def _changeColorMap(self, action):
        """
        Method invoked by the colormap Action Menu.

        Changes the current colormap used to render the image.

        Parameters
        ----------
        action : QAction
        """
        self.colorMap = self.cmap_for_action[action]

    @Property(float)
    def colorMapMin(self):
        """
        Minimum value for the colormap.

        Returns
        -------
        float
        """
        return self.cm_min

    @colorMapMin.setter
    @Slot(float)
    def colorMapMin(self, new_min):
        """
        Set the minimum value for the colormap.

        Parameters
        ----------
        new_min : float
        """
        if self.cm_min != new_min:
            self.cm_min = new_min
            if self.cm_min > self.cm_max:
                self.cm_max = self.cm_min

    @Property(float)
    def colorMapMax(self):
        """
        Maximum value for the colormap.

        Returns
        -------
        float
        """
        return self.cm_max

    @colorMapMax.setter
    @Slot(float)
    def colorMapMax(self, new_max):
        """
        Set the maximum value for the colormap.

        Parameters
        ----------
        new_max : float
        """
        if self.cm_max != new_max:
            self.cm_max = new_max
            if self.cm_max < self.cm_min:
                self.cm_min = self.cm_max

    def setColorMapLimits(self, mn, mx):
        """
        Set the limit values for the colormap.

        Parameters
        ----------
        mn : int
            The lower limit
        mx : int
            The upper limit
        """
        if mn >= mx:
            return
        self.cm_max = mx
        self.cm_min = mn

    @Property(PyDMColorMap)
    def colorMap(self):
        """
        Return the color map used by the ImageView.

        Returns
        -------
        PyDMColorMap
        """
        return self._colormap

    @colorMap.setter
    def colorMap(self, new_cmap):
        """
        Set the color map used by the ImageView.

        Parameters
        -------
        new_cmap : PyDMColorMap
        """
        self._colormap = new_cmap
        self._cm_colors = self.color_maps[new_cmap]
        self.setColorMap()
        for action in self.cm_group.actions():
            if self.cmap_for_action[action] == self._colormap:
                action.setChecked(True)
            else:
                action.setChecked(False)

    def setColorMap(self, cmap=None):
        """
        Update the image colormap.

        Parameters
        ----------
        cmap : ColorMap
        """
        if not cmap:
            if not self._cm_colors.any():
                return
            # Take default values
            pos = np.linspace(0.0, 1.0, num=len(self._cm_colors))
            cmap = ColorMap(pos, self._cm_colors)
        self.getView().getViewBox().setBackgroundColor(cmap.map(0))
        lut = cmap.getLookupTable(0.0, 1.0, alpha=False)
        self.getImageItem().setLookupTable(lut)

    @Slot(bool)
    def image_connection_state_changed(self, conn):
        """
        Callback invoked when the Image Channel connection state is changed.

        Parameters
        ----------
        conn : bool
            The new connection state.
        """
        if conn:
            self.redraw_timer.start()
        else:
            self.redraw_timer.stop()

    @Slot(np.ndarray)
    def image_value_changed(self, new_image):
        """
        Callback invoked when the Image Channel value is changed.

        We try to do as little as possible in this method, because it
        gets called every time the image channel updates, which might
        be extremely often.  Basically just store the data, and set
        a flag requesting that the image be redrawn.

        Parameters
        ----------
        new_image : np.ndarray
            The new image data.  This can be a flat 1D array, or a 2D array.
        """
        if new_image is None or new_image.size == 0:
            return
        logging.debug("ImageView Received New Image - Needs Redraw -> True")
        self.image_waveform = new_image
        self.needs_redraw = True

    @Slot(int)
    def image_width_changed(self, new_width):
        """
        Callback invoked when the Image Width Channel value is changed.

        Parameters
        ----------
        new_width : int
            The new image width
        """
        if new_width is None:
            return
        self._image_width = int(new_width)

    def process_image(self, image):
        """
        Boilerplate method to be used by applications in order to
        add calculations and also modify the image before it is
        displayed at the widget.

        .. warning::
           This code runs in a separated QThread so it **MUST** not try to write
           to QWidgets.

        Parameters
        ----------
        image : np.ndarray
            The Image Data as a 2D numpy array

        Returns
        -------
        np.ndarray
            The Image Data as a 2D numpy array after processing.
        """
        return image

    def redrawImage(self):
        """
        Set the image data into the ImageItem, if needed.

        If necessary, reshape the image to 2D first.
        """
        if self.thread is not None and not self.thread.isFinished():
            logger.warning("Image processing has taken longer than the refresh rate.")
            return
        self.thread = ImageUpdateThread(self)
        self.thread.updateSignal.connect(self.__updateDisplay)
        logging.debug("ImageView RedrawImage Thread Launched")
        self.thread.start()

    def toggleRedraw(self) -> bool:
        """
        Start or stop the thread responsible for drawing the image. Can be called by the user to
        pause redrawing the image, and resume later if needed.

        Returns
        -------
        bool
            True if the image is being redrawn on a timer, false otherwise
        """
        self.redraw_timer.stop() if self.redraw_timer.isActive() else self.redraw_timer.start()
        return self.redraw_timer.isActive()

    @Slot(list)
    def __updateDisplay(self, data):
        logging.debug("ImageView Update Display with new image")
        mini, maxi = data[0], data[1]
        img = data[2]
        self.getImageItem().setLevels([mini, maxi])
        self.getImageItem().setImage(img, autoLevels=False, autoDownsample=self.autoDownsample)

    @Property(bool)
    def autoDownsample(self):
        """
        Return if we should or not apply the
        autoDownsample option to PyQtGraph.

        Return
        ------
        bool
        """
        return self._auto_downsample

    @autoDownsample.setter
    def autoDownsample(self, new_value):
        """
        Whether we should or not apply the
        autoDownsample option to PyQtGraph.

        Parameters
        ----------
        new_value: bool
        """
        if new_value != self._auto_downsample:
            self._auto_downsample = new_value

    @Property(int)
    def imageWidth(self):
        """
        Return the width of the image.

        Return
        ------
        int
        """
        return self._image_width

    @imageWidth.setter
    def imageWidth(self, new_width):
        """
        Set the width of the image.

        Can be overridden by :attr:`widthChannel`.

        Parameters
        ----------
        new_width: int
        """
        if self._image_width != int(new_width) and (self._widthchannel is None or self._widthchannel == ""):
            self._image_width = int(new_width)

    @Property(bool)
    def normalizeData(self):
        """
        Return True if the colors are relative to data maximum and minimum.

        Returns
        -------
        bool
        """
        return self._normalize_data

    @normalizeData.setter
    @Slot(bool)
    def normalizeData(self, new_norm):
        """
        Define if the colors are relative to minimum and maximum of the data.

        Parameters
        ----------
        new_norm: bool
        """
        if self._normalize_data != new_norm:
            self._normalize_data = new_norm

    @Property(ReadingOrder)
    def readingOrder(self):
        """
        Return the reading order of the :attr:`imageChannel` array.

        Returns
        -------
        ReadingOrder
        """
        return self._reading_order

    @readingOrder.setter
    def readingOrder(self, new_order):
        """
        Set reading order of the :attr:`imageChannel` array.

        Parameters
        ----------
        new_order: ReadingOrder
        """
        if self._reading_order != new_order:
            self._reading_order = new_order

    @Property(DimensionOrder)
    def dimensionOrder(self):
        """
        Return the dimension order of the :attr:`imageChannel` array.
        (for more info see DimensionOrder class definition)

        Returns
        -------
        DimensionOrder
        """
        return self._dimension_order

    @dimensionOrder.setter
    def dimensionOrder(self, new_order):
        """
        Set dimension order of the :attr:`imageChannel` array.

        Parameters
        ----------
        new_order: DimensionOrder
        """
        if self._dimension_order != new_order:
            self._dimension_order = new_order

    def keyPressEvent(self, ev):
        """Handle keypress events."""
        return

    @Property(str)
    def imageChannel(self):
        """
        The channel address in use for the image data .

        Returns
        -------
        str
            Channel address
        """
        if self._imagechannel:
            return str(self._imagechannel.address)
        else:
            return ""

    @imageChannel.setter
    def imageChannel(self, value):
        """
        The channel address in use for the image data .

        Parameters
        ----------
        value : str
            Channel address
        """
        if self._imagechannel != value:
            # Disconnect old channel
            if self._imagechannel:
                self._imagechannel.disconnect()
            # Create and connect new channel
            self._imagechannel = PyDMChannel(
                address=value,
                connection_slot=self.image_connection_state_changed,
                value_slot=self.image_value_changed,
                severity_slot=self.alarmSeverityChanged,
            )
            self._channels[0] = self._imagechannel
            self._imagechannel.connect()

    @Property(str)
    def widthChannel(self):
        """
        The channel address in use for the image width .

        Returns
        -------
        str
            Channel address
        """
        if self._widthchannel:
            return str(self._widthchannel.address)
        else:
            return ""

    @widthChannel.setter
    def widthChannel(self, value):
        """
        The channel address in use for the image width .

        Parameters
        ----------
        value : str
            Channel address
        """
        if self._widthchannel != value:
            # Disconnect old channel
            if self._widthchannel:
                self._widthchannel.disconnect()
            # Create and connect new channel
            self._widthchannel = PyDMChannel(
                address=value,
                connection_slot=self.connectionStateChanged,
                value_slot=self.image_width_changed,
                severity_slot=self.alarmSeverityChanged,
            )
            self._channels[1] = self._widthchannel
            self._widthchannel.connect()

    def channels(self):
        """
        Return the channels being used for this Widget.

        Returns
        -------
        channels : list
            List of PyDMChannel objects
        """
        return self._channels

    def channels_for_tools(self):
        """Return channels for tools."""
        return [self._imagechannel]

    @Property(int)
    def maxRedrawRate(self):
        """
        The maximum rate (in Hz) at which the plot will be redrawn.

        The plot will not be redrawn if there is not new data to draw.

        Returns
        -------
        int
        """
        return self._redraw_rate

    @maxRedrawRate.setter
    def maxRedrawRate(self, redraw_rate):
        """
        The maximum rate (in Hz) at which the plot will be redrawn.

        The plot will not be redrawn if there is not new data to draw.

        Parameters
        -------
        redraw_rate : int
        """
        self._redraw_rate = redraw_rate
        self.redraw_timer.setInterval(int((1.0 / self._redraw_rate) * 1000))

    @Property(bool)
    def showAxes(self):
        """
        Whether or not axes should be shown on the widget.
        """
        return self._show_axes

    @showAxes.setter
    def showAxes(self, show):
        self._show_axes = show
        self.getView().showAxis("left", show=show)
        self.getView().showAxis("bottom", show=show)

    @Property(float)
    def scaleXAxis(self):
        """
        Sets the scale for the X Axis.

        For example, if your image has 100 pixels per millimeter, you can set
        xAxisScale to 1/100 = 0.01 to make the X Axis report in millimeter units.
        """
        # protect against access to not yet initialized view
        if hasattr(self, "view"):
            return self.getView().getAxis("bottom").scale
        return None

    @scaleXAxis.setter
    def scaleXAxis(self, new_scale):
        self.getView().getAxis("bottom").setScale(new_scale)

    @Property(float)
    def scaleYAxis(self):
        """
        Sets the scale for the Y Axis.

        For example, if your image has 100 pixels per millimeter, you can set
        yAxisScale to 1/100 = 0.01 to make the Y Axis report in millimeter units.
        """
        # protect against access to not yet initialized view
        if hasattr(self, "view"):
            return self.getView().getAxis("left").scale
        return None

    @scaleYAxis.setter
    def scaleYAxis(self, new_scale):
        self.getView().getAxis("left").setScale(new_scale)
