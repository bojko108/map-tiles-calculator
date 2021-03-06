# -*- coding: utf-8 -*-
"""
/***************************************************************************
 MapTilesCalculator
                                 A QGIS plugin
 Estimates the number of map tiles for a bbox and zoom levels
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2020-04-28
        git sha              : $Format:%H$
        copyright            : (C) 2020 by bojko108
        email                : bojko108@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
from qgis.core import QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsProject

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .map_tiles_calculator_dialog import MapTilesCalculatorDialog
import os.path

from .calculator import Calculator


class MapTilesCalculator:
    """QGIS Plugin Implementation."""
    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(self.plugin_dir, 'i18n',
                                   'MapTilesCalculator_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Count Map Tiles')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('MapTilesCalculator', message)

    def add_action(self,
                   icon_path,
                   text,
                   callback,
                   enabled_flag=True,
                   add_to_menu=True,
                   add_to_toolbar=True,
                   status_tip=None,
                   whats_this=None,
                   parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(self.menu, action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/map_tiles_calculator/icon.png'
        self.add_action(icon_path,
                        text=self.tr(u'Count Map Tiles'),
                        callback=self.run,
                        parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(self.tr(u'&Count Map Tiles'), action)
            self.iface.removeToolBarIcon(action)

    def run(self):
        """Run method that performs all the real work"""

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False
            self.dlg = MapTilesCalculatorDialog()

        # minLon, minLat, maxLon, maxLat
        # bbox = (22.4773, 41.8132, 24.7185, 43.0617)
        self.bbox = self.getCurrentMapExtent()
        self.minZoom = 1
        self.maxZoom = 20
        self.calcualtor = Calculator()

        # show the dialog
        self.dlg.show()

        self.dlg.mapExtentText.setText('{0},{1},{2},{3} [EPSG:{4}]'.format(
            self.bbox[0],
            self.bbox[1],
            self.bbox[2],
            self.bbox[3],
            self.bbox[4],
        ))
        self.dlg.resultText.setPlainText('')

        self.dlg.minZoomText.setText(str(self.minZoom))
        self.dlg.maxZoomText.setText(str(self.maxZoom))
        self.dlg.minZoomSlider.setValue(self.minZoom)
        self.dlg.maxZoomSlider.setValue(self.maxZoom)

        self.dlg.minZoomSlider.sliderMoved.connect(self.minZoomSliderMoved)
        self.dlg.maxZoomSlider.sliderMoved.connect(self.maxZoomSliderMoved)
        self.dlg.minZoomSlider.valueChanged.connect(self.minZoomSliderMoved)
        self.dlg.maxZoomSlider.valueChanged.connect(self.maxZoomSliderMoved)
        self.dlg.pushButton.clicked.connect(self.calculateMapTilesCount)

        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass

    def minZoomSliderMoved(self, value):
        self.minZoom = value
        self.dlg.minZoomText.setText(str(self.minZoom))

    def maxZoomSliderMoved(self, value):
        self.maxZoom = value
        self.dlg.maxZoomText.setText(str(self.maxZoom))

    def calculateMapTilesCount(self):
        if self.minZoom > self.maxZoom:
            self.iface.messageBar().pushMessage('error')
            self.dlg.resultText.setPlainText(
                'error: min zoom cannot be greater than max zoom')
            return

        count = self.calcualtor.calculateTileCount(self.bbox, self.minZoom,
                                                   self.maxZoom)
        size = self.calculateApproximateSize(count)

        self.dlg.resultText.setPlainText(
            'estimated map tiles count: {0}\napproximate size: {1}'.format(
                count, size))

    def calculateApproximateSize(self, count):
        size = count * int(self.dlg.tileSizeText.text())
        sizes = ('KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB')
        index = 0

        while size > 1024:
            index += 1
            size = size / 1024
        return '{0} {1}'.format(round(size, 2), sizes[index])

    def getCurrentMapExtent(self):
        # minLon, minLat, maxLon, maxLat
        # bbox = (22.4773, 41.8132, 24.7185, 43.0617)
        bbox = self.iface.mapCanvas().extent()
        targetCRS = 4326
        mapCRS = self.iface.mapCanvas().mapSettings().destinationCrs().srsid()

        sourceCRS = QgsCoordinateReferenceSystem(mapCRS)
        destCRS = QgsCoordinateReferenceSystem(targetCRS)
        transform = QgsCoordinateTransform(sourceCRS, destCRS,
                                           QgsProject.instance())

        bbox = transform.transformBoundingBox(bbox)
        return (round(bbox.xMinimum(), 6), round(bbox.yMinimum(), 6),
                round(bbox.xMaximum(), 6), round(bbox.yMaximum(),
                                                 6), targetCRS)
