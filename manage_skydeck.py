# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ManageSkydeck
                                 A QGIS plugin
 This is a plugin to download files from Skydeck, process it in QGIS and upload the results back to Skydeck portal.
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2024-03-10
        git sha              : $Format:%H$
        copyright            : (C) 2024 by Asteria
        email                : neethu.narayanan@asteria.co.in
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

from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication, QUrl
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QListWidgetItem
from qgis.core import QgsRasterLayer, QgsProject, QgsVectorLayer, QgsRasterFileWriter, QgsRasterPipe, QgsCoordinateReferenceSystem, QgsVectorFileWriter
from qgis.utils import iface


from .resources import *

from .manage_skydeck_dialog import ManageSkydeckDialog
from .import_export import ImportExportWindow
import os.path
import requests
import tempfile
import sys
import jwt
import os
import platform
import subprocess
from urllib.parse import urlparse, parse_qs

try:
    from azure.storage.blob import BlobServiceClient
except ImportError:
    if platform.system() == 'Linux':
        subprocess.run(['pip', 'install', 'azure-storage-blob'])
    elif platform.system() == 'Darwin':
        current_path = sys.executable
        last_slash_index = current_path.rfind('/')
        install_path = current_path[:last_slash_index]
        #subprocess.run(["cd", current_path], shell=True)
        subprocess.run([install_path+'/bin/pip3', 'install', 'azure-storage-blob'])
    else:
        current_path = os.getcwd()
        subprocess.run(["cd", current_path], shell=True)
        subprocess.run(['pip', 'install', 'azure-storage-blob'], shell=True)
finally:
    from azure.storage.blob import BlobServiceClient




class ManageSkydeck:
    """QGIS Plugin Implementation."""

    endpoint = "https://skydeck.asteria.co.in"
    blob_endpoint = "https://skydeckcorefilestrgprd.blob.core.windows.net"

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        self.dlg = ManageSkydeckDialog()

        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'ManageSkydeck_{}.qm'.format(locale))
        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&SkyGIS')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None
        #self.open_web_page()

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
        return QCoreApplication.translate('ManageSkydeck', message)


    def add_action(
        self,
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
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/manage_skydeck/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u''),
            callback=self.run,
            parent=self.iface.mainWindow())
        
        self.dlg.loginButton.clicked.connect(self.open_web_page)
        # will be set False in run()

        # self.open_web_page()
        #self.first_start = True
    

    def on_url_changed(self, url):
        if self.initial_redirection_done:
            print(f"Bearer  will be processed here")
            self.web_view.loadFinished.connect(self.on_load_finished)

        else:
            self.initial_redirection_done = True
            print("Ignoring the first URL change event.")

    def on_load_finished(self, ok):
        # This slot is called when the web page has finished loading.
        if ok:
            print("Page loaded successfully. Processing the page.")
            frame = self.web_view.page().mainFrame()
            url = frame.url().toString()
            print(url)
            parsed_url = urlparse(url)
            query_params = parse_qs(parsed_url.query)
            token = query_params.get('token', [None])[0]
            print(f"Token: {token}")
            self.handle_token(token)
        else:
            print("Failed to load page")


    def handle_token(self, token):
        if token:
            print("Token is valid")
            self.dlg.close()
            self.import_export_window = ImportExportWindow(token)
            #Verify RBAC
            print(f"Bearer {token}")
            if not isinstance(token, bytes):
                encoded_token = token.encode()
            try:
                decoded_token = jwt.decode(encoded_token, options={"verify_signature": False})
            except jwt.DecodeError:
                print("Failed to decode token")
            # Extract email and sub
            email = decoded_token.get('email')
            sub = decoded_token.get('sub')
            rbac_data = {"email": email, "sub": sub}
            print(f"Email: {email}, Sub: {sub}")
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.post(url="https://skydeck-staging.asteria.co.in/api/gis/v1/qgis/rbac", headers=headers, json=rbac_data)
            print(f"Response message from rbac: {response}")
            print(f"Response : {response.json()}")
            if response.json() is not True:
                print("RBAC Failed")
                iface.messageBar().pushMessage(f"UNAUTHORISED USER", level=2, duration=5)
            else:
                print("RBAC Success")
                self.import_export_window.show()

        else:
            print("No token found")
            iface.messageBar().pushMessage(f"Error in validating the user. Please try after sometime", level=2, duration=5)
            self.dlg.close()


    def open_web_page(self):
        try:
            print("Clicked on login button")
            self.initial_redirection_done = False
            self.web_view = self.dlg.skydeckwebView
            self.web_view.load(QUrl(f"https://skydeck-staging.asteria.co.in/auth/login"))
            self.web_view.urlChanged.connect(self.on_url_changed)
        except Exception as e:
            print(f"Error : {e}")


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&SkyGIS'),
                action)
            self.iface.removeToolBarIcon(action)


    def run(self):
        """Run method that performs all the real work"""

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False
            

        # show the dialog
        self.dlg.show()

        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass
