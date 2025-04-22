
# SkyDeck Plugin

## Description:

Seamlessly Integrate and Manage SkyDeck Geospatial Data within QGIS
The SkyDeck QGIS Plugin integrates your SkyDeck account into QGIS so you can easily manage and process your geospatial data. With this plugin, you can easily import raster and vector data from SkyDeck with a single click, as well as update vector data directly back to SkyDeck. Enhance your workflow by leveraging SkyDeck's powerful cloud-based processing and storage, all within the familiar QGIS environment.

SkyDeck is a unified cloud-based SaaS platform developed by [Asteria Aerospace](https://asteria.co.in/), designed for seamless drone data management, advanced data processing, data visualization and geospatial analysis. It provides secure, centralized management for scaling drone programs across multiple applications, including agriculture, infrastructure, surveying, oil and gas, and more.

An active SkyDeck account is required to use this plugin. Discover [SkyDeck](https://asteria.co.in/skydeck) or [Start a Free Trial](https://skydeck.asteria.co.in/ui/onboarding) today.


## Installation

"Stable" releases are available through the official QGIS plugins repository.

Prerequisites:
QGIS 3.40 or greater installed


Installation steps:

Open Plugin Manager and search for SkyGIS plugin and install it.
And restart QGIS so that changes in environment take effect.    

## Troubleshooting: Missing `PyQt5.QtWebEngineWidgets`

#### On Windows:
1. Open **Start Menu** and search for `OSGeo4W Shell`.
2. Run the following command:
   pip install PyQtWebEngine
3. Restart QGIS and try again.

#### On Linux:
1. Open your system terminal.
2. Run the following command:
   pip install PyQtWebEngine
3. Restart QGIS and try again.

  
## For testing on stage environment:

1. Download the zip file from https://github.com/asteriaaerospace/SkyDeck-QGIS-Plugin/tree/staging 
2. Open Plugin Manager in QGIS and use install from zip option

