import os
import requests
import sys
import platform
import subprocess
import tempfile
import importlib

from PyQt5 import QtCore

from qgis.PyQt.QtWidgets import QListWidgetItem


from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from qgis.core import QgsRasterLayer, QgsProject, QgsVectorLayer, QgsRasterFileWriter, QgsRasterPipe, QgsCoordinateReferenceSystem, QgsVectorFileWriter
from qgis.PyQt.QtWidgets import QListWidgetItem
from qgis.utils import iface
from qgis.PyQt.QtCore import QUrl
from PyQt5.QtWebKitWidgets import QWebPage

try:
    from azure.storage.blob import BlobServiceClient
except ImportError:
    if platform.system() == 'Linux':
        subprocess.run(['pip', 'install', 'azure-storage-blob'])
    elif platform.system() == 'Darwin':
        current_path = sys.executable
        last_slash_index = current_path.rfind('/')
        install_path = current_path[:last_slash_index]
        subprocess.run([install_path+'/bin/pip3', 'install', 'azure-storage-blob'])
    else:
        current_path = os.getcwd()
        subprocess.run(["cd", current_path], shell=True)
        subprocess.run(['pip', 'install', 'azure-storage-blob'], shell=True)
finally:
    from azure.storage.blob import BlobServiceClient



FORM_IMPORT_EXPORT_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ImportExportFiles.ui'))

class ImportExportWindow(QtWidgets.QDialog, FORM_IMPORT_EXPORT_CLASS):

    endpoint = "https://skydeck-staging.asteria.co.in"
    blob_endpoint = "https://sdcorefilestrgstg.blob.core.windows.net"

    def __init__(self,token, webView, parent=None):
        super(ImportExportWindow, self).__init__(parent)
        self.setupUi(self)
        self.token = token
        self.webView = webView
        print(f" TOKEN RECIEVED ----: {self.token}")


        # # Connect the buttons to the respective functions
        self.importConnectButton.clicked.connect(self.fetchSkydeckData)
        self.importpushButton.clicked.connect(self.addQGISLayer)
        self.exportConnectButton.clicked.connect(self.fetchQGISData)
        self.exportPushButton.clicked.connect(self.uploadToSkydeck)
        self.logoutButton.clicked.connect(self.skydeckLogout)

    def skydeckLogout(self):
        try:
            print("Logout from Skydeck")

            self.clear()
            self.importURL.clear()
            self.exportURL.clear()
            del self.token

            # Disconnect the signals
            self.webView.urlChanged.disconnect()
            self.webView.loadFinished.disconnect()

            self.webView.load(QUrl(f"https://skydeck-staging.asteria.co.in/auth/logout"))
            iface.messageBar().pushMessage(f"Logged out successfully", level=3, duration=5)

            print("Closed the plugin")
            self.close()
            print("Closed")
        except Exception as e:
            print(f"Error in logout: {e}")
            iface.messageBar().pushMessage(f"Error in logout", level=2, duration=5)
            self.clear()
            self.close()
        


    def clear(self):
        #self.importURL.clear()
        #self.importToken.clear()
        self.importRasterList.clear()
        self.importVectorList.clear()
        self.importFileListGroupBox.setVisible(False)
        #self.exportURL.clear()
        #self.exportToken.clear()
        self.exportRasterList.clear()
        self.exportVectorList.clear()
        self.exportFileListGroupBox.setVisible(False)
        print("Cleared the form fields")

    def get_sas(self):
        #token = str(self.importToken.text()) if self.importToken.text() else str(self.exportToken.text())
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(url=f"{ImportExportWindow.endpoint}/api/gis/v1/qgis/get-sas", headers=headers)
        print(f"Response message from sas: {response.json()}")
        sas = response.json()["sas"]
        print(f"SAS token: {sas}")
        return sas


    def getRasterDict(self):
        file_url = str(self.importURL.text())
        url_parts = file_url.split('/')
        organisation_id = url_parts[5]
        site_id = url_parts[7]
        survey_id = url_parts[9]
        #token = str(self.importToken.text())
        headers = {"Authorization": f"Bearer {self.token}"}
        raster_url = f"{ImportExportWindow.endpoint}/api/core/v1/organisations/{organisation_id}/sites/{site_id}/surveys/{survey_id}/rasters"
        response = requests.get(url=raster_url, headers=headers)
        return response


    def getVectorDict(self):
        file_url = str(self.importURL.text())
        url_parts = file_url.split('/')
        organisation_id = url_parts[5]
        site_id = url_parts[7]
        survey_id = url_parts[9]
        #token = str(self.importToken.text())
        headers = {"Authorization": f"Bearer {self.token}"}
        raster_url = f"{ImportExportWindow.endpoint}/api/core/v1/organisations/{organisation_id}/sites/{site_id}/surveys/{survey_id}/vectors"
        response = requests.get(url=raster_url, headers=headers)
        return response
    
    def fetchQGISData(self):
        try:
            raster_layers = []
            vector_layers = []
            self.exportRasterList.clear()
            self.exportVectorList.clear()
            # Accessing the current project
            project = QgsProject.instance()
            # Getting all layers in the project
            #layers1 = project.mapLayers()
            layers = {name: layer for name, layer in project.mapLayers().items() if not layer.source().startswith("/vsicurl/")}
            print(f"Layers new : {layers}")
            for layer_id, layer in layers.items():
                print(f"Layer: {layers.items()}")
                if isinstance(layer, QgsRasterLayer):
                    raster_layers.append(layer.name())
                    print(f"Raster layers: {layer.name()}")
                elif isinstance(layer, QgsVectorLayer):
                    vector_layers.append(layer.name())
                    print(f"Vector layers: {layer.name()}")
            for values in raster_layers:
                item = QListWidgetItem(values)
                item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
                item.setCheckState(QtCore.Qt.Unchecked)
                self.exportRasterList.addItem(item)
                print('Raster layers: ', values)
            for vector_values in vector_layers:
                vector_item = QListWidgetItem(vector_values)
                vector_item.setFlags(vector_item.flags() | QtCore.Qt.ItemIsUserCheckable)
                vector_item.setCheckState(QtCore.Qt.Unchecked)
                self.exportVectorList.addItem(vector_item)
                print('Vector layers: ', vector_values)
            
            # Show the group box after populating the ListView
            self.exportFileListGroupBox.setVisible(True)
            print("Fetched data from Qgis")
        except Exception as e:
            print(f"Error in fetching data from QGIS: {e}")
            iface.messageBar().pushMessage(f"Error in fetching data from QGIS", level=2, duration=5)
            self.clear()
            #self.close()
        

    def fetchSkydeckData(self):
        try:    
            global rasters_dict
            global vectors_dict
            print("Clicked on connect")
            self.importRasterList.clear()
            self.importVectorList.clear()
            raster_response = self.getRasterDict()
            rasters_dict = raster_response.json()
            raster_names = []
            print(f"Response message from skydeck raster: {raster_response}")
            for raster in rasters_dict["data"]["rasters"]:
                raster_names.append(raster["name"])
            for values in raster_names:
                item = QListWidgetItem(values)
                item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
                item.setCheckState(QtCore.Qt.Unchecked)
                self.importRasterList.addItem(item)


            vectors_response = self.getVectorDict()
            vectors_dict = vectors_response.json()
            vector_names = []
            print(f"Response message from skydeck vector: {vectors_response}")
            for vector in vectors_dict["data"]["vectors"]:
                vector_names.append(vector["name"])
            for vector_values in vector_names:
                vector_item = QListWidgetItem(vector_values)
                vector_item.setFlags(vector_item.flags() | QtCore.Qt.ItemIsUserCheckable)
                vector_item.setCheckState(QtCore.Qt.Unchecked)
                self.importVectorList.addItem(vector_item)


            # Show the group box after populating the ListView
            self.importFileListGroupBox.setVisible(True)
            print("Fetched data from Skydeck")
        except Exception as e:
            print(f"Error in fetching data from Skydeck: {e}")
            iface.messageBar().pushMessage(f"Error in fetching data from Skydeck", level=2, duration=5)
            self.clear()
            #self.close()


    def addQGISLayer(self):
        try:
            print("Clicked on Import layer")
            sas = self.get_sas()
            for i in range(self.importRasterList.count()):
                item = self.importRasterList.item(i)
                if item.checkState() == QtCore.Qt.Checked:
                    print(f"Item checked: {item.text()}")
                    #file_url = self.getdownloadURL(item.text(), rasters_dict)
                    for raster in rasters_dict["data"]["rasters"]:
                        if raster["name"] == item.text():
                            file_url = raster["cogeotiff"]["downloadUrl"]
                            print("File URL: ", file_url)
                    layer_name = str(item.text())
                    if not file_url.startswith("/vsicurl/"):
                        file_url = "/vsicurl/" + file_url +"?"+ sas
                        print("Final File URL: ", file_url)
                    raster_layer = QgsRasterLayer(file_url, layer_name, "gdal")
                    if not raster_layer.isValid():
                        print(f"Error: Unable to load raster layer from {file_url}")
                    else:
                        # Add the raster layer to the map
                        QgsProject.instance().addMapLayer(raster_layer)
                        print(f"Raster layer added successfully: {layer_name}")
            
            print("Adding vector layer")
            for i in range(self.importVectorList.count()):
                vector_item = self.importVectorList.item(i)
                if vector_item.checkState() == QtCore.Qt.Checked:
                    print(f"vecter Item checked: {vector_item.text()}")
                    #file_url = self.getdownloadURL(item.text(), rasters_dict)
                    for vector in vectors_dict["data"]["vectors"]:
                        if vector["name"] == vector_item.text():
                            vector_file_url = vector["geojson"]["downloadUrl"]
                            print("Vctor File URL: ", vector_file_url)
                    vector_layer_name = str(vector_item.text())
                    vector_file_url = "/vsicurl/" + vector_file_url +"?"+ sas
                    print("Final vector  File URL: ", vector_file_url)
                    vector_layer = QgsVectorLayer(vector_file_url, vector_layer_name, "ogr")
                    if not vector_layer.isValid():
                        print(f"Error: Unable to load vector layer from {vector_file_url}")
                    else:
                        # Add the raster layer to the map
                        QgsProject.instance().addMapLayer(vector_layer)
                        print(f"Vector layer added successfully: {vector_layer_name}")

            iface.messageBar().pushMessage(f"Layer added successfully", level=3, duration=5)
            self.clear()
            self.close()
            print("Closed")
        except Exception as e:
            print(f"Error in adding layer: {e}")
            iface.messageBar().pushMessage(f"Error in adding layer", level=2, duration=5)
            self.clear()
            #self.close()


    def uploadToSkydeck(self):
        try:
            print("Uploading data to skydeck")
            rasters_dict = {"rasters": []}
            vectors_dict = {"vectors": []}
            integration_URL = str(self.exportURL.text())
            url_parts = integration_URL.split('/')
            organisation_id = url_parts[5]
            site_id = url_parts[7]
            survey_id = url_parts[9]
            #token = str(self.exportToken.text())
            headers = {"Authorization": f"Bearer {self.token}"}

            for i in range(self.exportRasterList.count()):
                item = self.exportRasterList.item(i)
                if item.checkState() == QtCore.Qt.Checked:
                    print(f"Item checked: {item.text()}")
                    raster_file_path = tempfile.NamedTemporaryFile(suffix=".tiff")
                    EPSG = 'EPSG:25832'
                    project = QgsProject.instance()
                    rlayer = project.mapLayersByName(item.text())[0]
                    pipe = QgsRasterPipe()
                    pipe.set(rlayer.dataProvider().clone())
                    file_writer = QgsRasterFileWriter(raster_file_path.name)
                    file_writer.writeRaster(pipe, rlayer.width(),rlayer.height(), rlayer.extent(), QgsCoordinateReferenceSystem(EPSG))
                    rasters_dict["rasters"].append({"filename": item.text(), "filepath": raster_file_path.name})

            print(f"Rasters dict done")

            for i in range(self.exportVectorList.count()):
                vector_item = self.exportVectorList.item(i)
                if vector_item.checkState() == QtCore.Qt.Checked:
                    print(f"Vector Item checked: {vector_item.text()}")
                    vector_file_path = tempfile.NamedTemporaryFile(suffix=".geojson")
                    project = QgsProject.instance()
                    vlayer = project.mapLayersByName(vector_item.text())[0]
                    QgsVectorFileWriter.writeAsVectorFormat(vlayer, vector_file_path.name, "utf-8", vlayer.crs(), "GeoJSON")
                    vectors_dict["vectors"].append({"filename": vector_item.text(), "filepath": vector_file_path.name})
            print(f"Vectors dict done")

            for raster in rasters_dict["rasters"]:
                raster_path = raster['filepath']
                raster_file_name = raster['filename']
                raster_options = {"Surface Model": "dsm", "Terrain Model": "dtm", "Orthophoto": "orthophoto", "NDVI":"ndvi", "Slope Map":"slope"}
                selected_text = self.rasterType.currentText()
                raster_type = raster_options[selected_text] if selected_text in raster_options else "other"
                raster_request_path = f"/api/core/v1/organisations/{organisation_id}/sites/{site_id}/surveys/{survey_id}/rasters"
                raster_sizeInBytes = os.path.getsize(raster_path)
                raster_url = ImportExportWindow.endpoint+raster_request_path
                raster_data = {"name": raster_file_name, "type": raster_type}
                try:
                    raster_con = requests.post(raster_url, headers=headers, json=raster_data)
                    raster_response = raster_con.json()
                    raster_id = raster_response["data"]["raster"]["uuid"]
                    raster_upload_path = ImportExportWindow.endpoint+raster_request_path+"/"+raster_id
                    #upload to blob
                    raster_sas = self.get_sas()
                    blob_url = ImportExportWindow.blob_endpoint
                    with open(raster_path, "rb") as file_obj:
                        service_client = BlobServiceClient(account_url=blob_url, credential=raster_sas)
                        blob_client = service_client.get_blob_client(container="raster", blob=raster_upload_path)
                        blob_client.upload_blob(file_obj, overwrite=True) 
                        print(f'-----Uploaded raster file to : {raster_upload_path}-----')
                    raster_payload = {
                        "type": raster_type,
                        "geotiff": {
                            "name": raster_file_name,
                            "downloadUrl": blob_client.url,
                            "sizeInBytes": raster_sizeInBytes,
                            "uploadStatus": "uploaded",
                        },
                    }
                    raster_upload_response = requests.patch(raster_upload_path, headers=headers, json=raster_payload)
                    if raster_upload_response.status_code == 200:
                        iface.messageBar().pushMessage(f"Raster Upload Success!", level=3, duration=5)
                    else:
                         iface.messageBar().pushMessage(f"Raster Upload Failed!", level=2, duration=5)
                    print(f"Raster response : {raster_upload_response.json()}")
                except Exception as e:
                    print(f"Error in uploading the raster : {e}")
                    iface.messageBar().pushMessage(f"Error in uploading the raster ", level=2, duration=5)

            for vector in vectors_dict["vectors"]:
                vector_file_name = vector['filename']
                vector_path = vector['filepath']
                url_parts = integration_URL.split('/')
                organisation_id = url_parts[5]
                site_id = url_parts[7]
                survey_id = url_parts[9]
                request_path = f"/api/core/v1/organisations/{organisation_id}/sites/{site_id}/surveys/{survey_id}/vectors"

                vector_sizeInBytes = os.path.getsize(vector_path)
                vector_url = ImportExportWindow.endpoint+request_path
                data = {"name": vector_file_name, "type": "geojson"}
                try:
                    con = requests.post(vector_url, headers=headers, json=data)
                    vector_response = con.json()
                    vector_id = vector_response["data"]["vector"]["uuid"]
                    vector_upload_path = ImportExportWindow.endpoint+request_path+"/"+vector_id
                    #upload to blob
                    vector_sas = self.get_sas()
                    blob_url = ImportExportWindow.blob_endpoint
                    with open(vector_path, "rb") as file_obj:
                        vector_service_client = BlobServiceClient(account_url=blob_url, credential=vector_sas)
                        vector_blob_client = vector_service_client.get_blob_client(container="vector", blob=vector_upload_path)
                        vector_blob_client.upload_blob(file_obj, overwrite=True) 
                        print(f'-----Uploaded vector file to : {vector_upload_path}-----')

                    vector_payload = {
                        "type": "geojson",
                        "geojson": {
                            "name": vector_file_name,
                            "downloadUrl": vector_blob_client.url,
                            "sizeInBytes": vector_sizeInBytes,
                            "uploadStatus": "uploaded",
                        },
                    }
                    v_upload_response = requests.patch(vector_upload_path, headers=headers, json=vector_payload)
                    if v_upload_response.status_code == 200:
                        iface.messageBar().pushMessage(f"Vector Upload Success!", level=3, duration=5)
                    else:
                         iface.messageBar().pushMessage(f"Vector Upload Failed!", level=2, duration=5)
                    print(f"vector response : {v_upload_response.json()}")
                except Exception as e:
                    print(f"Error in uploading the vector : {e}")
                    iface.messageBar().pushMessage(f"Error in uploading the vector ", level=2, duration=5)

            self.clear()
            #self.close()
            print("Closed")
        except Exception as e:  
            print(f"Error in uploading data to Skydeck: {e}")
            iface.messageBar().pushMessage(f"Error in uploading data to Skydeck", level=2, duration=5)
            self.clear()
            self.close()