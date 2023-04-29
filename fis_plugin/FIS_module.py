# -*- coding: utf-8 -*-
"""
/***************************************************************************
 WofEClass
                                 A QGIS plugin
                        Fuzzy Inference System
 
 Created by Prakriti Shetty, BTech Chemical Engg, IIT Bombay. 
 
 Generated using the basic template from Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2023-01-01
        end                  : 2023-05-01
        git sha              : $Format:%H$
        email                : prakritishetty02@gmail.com
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

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .FIS_module_dialog import FISPluginDialog
import os.path

#System imports
import os
import os.path
from pathlib import Path
import csv
import math
import qgis
import processing
from processing.algs.gdal.GdalUtils import GdalUtils
from osgeo import gdal, ogr, osr, gdalconst
from PyQt5.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QAbstractItemView, QDialog, QListWidget,  QListWidgetItem, QAction, QFileDialog, QApplication, QWidget, QPushButton, QMessageBox, QMainWindow, QApplication, QLabel
from qgis.core import QgsVectorLayer, Qgis, QgsProject, QgsMapLayer, QgsRasterLayer
from qgis.analysis import QgsRasterCalculator, QgsRasterCalculatorEntry 
import pandas as pd
import numpy as np
import sys
import scipy.stats
from scipy import ndimage


class FISPlugin:
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
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'WofEClass_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Fuzzy Inference System')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None






        label = QLabel()
        pixmap = QPixmap('icon.png')
        label.setPixmap(pixmap)
        

        
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
        return QCoreApplication.translate('FISPlugin', message)


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
            self.iface.addPluginToRasterMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = 'C://Users//prakr_cepprws//AppData//Roaming//QGIS//QGIS3//profiles//default//python//plugins//fis_plugin//icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Fuzzy Logic'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True

        
    def inp_evdnc_rst(self):
        global names_evr
        names_evr =(QFileDialog.getOpenFileNames(caption="Add evidence rasters", filter="Evidence Rasters (*.tif)")[0])
        for name in names_evr:
            self.dlg.lw_evdnc_rsts.addItem(name)
        inFile =str(names_evr)  
        print(names_evr)
    

    def removeSelectedEvR(self):
       for item in self.dlg.lw_evdnc_rsts.selectedItems():
            self.dlg.lw_evdnc_rsts.takeItem(self.dlg.lw_evdnc_rsts.row(item))
    
    
    
    # def loadRasters(self):
    #     self.dlg.cb_raster.clear()
    #     #self.dlg.cb_xtnt_rstr.clear()
    #     #self.dlg.cb_xtnt_rstr_rsp.clear()
    #     layers=[layer for layer in QgsProject.instance().mapLayers().values()]
    #     raster_layers=[]
    #     for layer in layers:
    #         if layer.type()==QgsMapLayer.RasterLayer:
    #             raster_layers.append(layer.name())
    #     self.dlg.cb_raster.addItems(raster_layers)   
    #     #self.dlg.cb_xtnt_rstr.addItems(raster_layers)
    #     #self.dlg.cb_xtnt_rstr_rsp.addItems(raster_layers)
        
    # def openRaster(self):
    #     """Open raster from file dialog"""
    #     inFile=str(QFileDialog.getOpenFileName(caption="Add raster to map project", filter="Evidence raster (*.tif)")[0])
    #     name = str.split(os.path.basename(inFile), ".")
    #     base=os.path.basename(inFile)
    #     name_ = os.path.splitext(base)[0]
        
    #     if inFile is not None:
    #         self.iface.addRasterLayer(inFile, str.split(os.path.basename(inFile), ".")[0])
    #         self.loadRasters()
    #             # Add the selected filename to combobox
    #         self.dlg.cb_raster.addItem(name_)
            
    #         # Obtain index of newly-added item
    #         index = self.dlg.cb_raster.findText(name_)
    #         # Set the combobox to select the new item
    #         self.dlg.cb_raster.setCurrentIndex(index)
                
 
  
    
    def add_fuzzy_rule(self):
        print("")

    def prepro(self):
       
        #Step 1: Get the number of factors and variables for each factor
        no_facs = self.dlg.no_facs.text()
        no_vars_fac1 = self.dlg.no_vars_fac1.text()
        no_vars_fac2 = self.dlg.no_vars_fac2.text()
        no_vars_outputfac = self.dlg.no_vars_outputfac.text()
        
     
        # Mask Layer
        msk_name= self.dlg.cb_msk.currentText()
        msk_layer = QgsProject().instance().mapLayersByName(msk_name)[0]
        # msk_src = msk_layer.source()
        
        # Compute entries from filenames of layers added in the listwidget
        paths = names_evr       
        lst =  [QgsRasterLayer(str(path)) for path in paths]
        
        for lyr in lst:
            inp = lyr
            path = inp.source()
            rstr_baseName = str.split(os.path.basename(path), ".")
            ot_rsmpl = scratch_dir + '/' + rstr_baseName[0] +'_rsmpl' + '.tif'
            ot_c = working_dir + '/' + rstr_baseName[0] +'_clip' + '.tif'
            
            data = gdal.Open(path, gdalconst.GA_ReadOnly)
            gdal.Warp(ot_rsmpl, data, format = 'GTiff', xRes = unt_m, yRes = unt_m) 
            
            processing.run('gdal:cliprasterbymasklayer',
               {'ALPHA_BAND' : False, 
               'CROP_TO_CUTLINE' : True, 
               'DATA_TYPE' : 6, 
               'INPUT' : ot_rsmpl, 
               'KEEP_RESOLUTION' : False, 
               'MASK' : msk_layer, 
               'MULTITHREADING' : False, 
               'NODATA' :  -999999999, 
               'OPTIONS' : '', 
               'OUTPUT' : ot_c, 
               'SET_RESOLUTION' : False, 
               'SOURCE_CRS' : None, 
               'TARGET_CRS' : None, 
               'X_RESOLUTION' : None, 
               'Y_RESOLUTION' : None} )

            qgis.utils.iface.addRasterLayer(ot_c)
    
        #Step 2: Rasterize training sites
        
        ##Rasterization of training sites
        trng_name= self.dlg.cb_shp.currentText()
        trng_layer = QgsProject().instance().mapLayersByName(trng_name)[0]
        path_trng = trng_layer.source()
        layer = trng_layer
        #next 13 lines refer I-B 
        #St_Area_Rst = ot_c
        St_Area_Rst = ot_rsmpl
        dim = gdal.Open(St_Area_Rst,gdalconst.GA_ReadOnly)
        xoff,a,b,yoff,d,e = dim.GetGeoTransform()
        band1= dim.GetRasterBand(1)
        rows = dim.RasterYSize
        cols = dim.RasterXSize
        Total_pixel = (rows*cols)
        extent = layer.extent()
        xmin = xoff
        xmax = xoff + (a*cols)
        ymin = yoff + (e*rows)
        ymax = yoff
         
        '''
        #Sample code to save the file to the same directory as the inpput
        output_loc_name = str(os.path.dirname(path))
        output_new = output_loc_name + '/temp_trng_rstr.tif'
        output = output_new
        '''
        
        
        global dep_rst_clip
        dep_rst = scratch_dir + '/trng_rst.tif'
        dep_rst_clip = scratch_dir + '/' + 'dep_rst_clip.tif'
        
        field_name = "Dep_ID"
        field_index = layer.fields().indexFromName(field_name)

        if field_index != -1:
                   
            processing.run("gdal:rasterize",
                               {"INPUT":layer,
                               "FIELD":"Dep_ID",
                               "UNITS": 0,
                               "DIMENSIONS":0,
                               "WIDTH":cols,
                               "HEIGHT":rows,
                               "EXTENT":"%f,%f,%f,%f"% (xmin, xmax, ymin, ymax),
                               "TFW":1,
                               "RTYPE":0,
                               "NO_DATA":0,
                               "COMPRESS":0,
                               "JPEGCOMPRESSION":1,
                               "ZLEVEL":1,
                               "PREDICTOR":1,
                               "TILED":False,
                               "BIGTIFF":2,
                               "EXTRA": '',
                               "OUTPUT":dep_rst})
            #target_ds = None
           
            ##Clipping training sites raster to extent mask
            msk_c_name= self.dlg.cb_msk.currentText()
            msk_c_layer = QgsProject().instance().mapLayersByName(msk_c_name)[0]
            msk_c_src = msk_c_layer.source()
            mask_c = msk_c_layer

            processing.run('gdal:cliprasterbymasklayer',
               {'ALPHA_BAND' : False, 
               'CROP_TO_CUTLINE' : True, 
               'DATA_TYPE' : 0, 
               'INPUT' : dep_rst, 
               'KEEP_RESOLUTION' : False, 
               'MASK' : msk_layer, 
               'MULTITHREADING' : False, 
               'NODATA' : -999999999,
               'OPTIONS' : '', 
               'OUTPUT' : dep_rst_clip, 
               'SET_RESOLUTION' : False, 
               'SOURCE_CRS' : None, 
               'TARGET_CRS' : None, 
               'X_RESOLUTION' : None, 
               'Y_RESOLUTION' : None} )
            
            #résampling the deposit raster to ensure cell size
            #ot_dep_rsmpl is used for all three tools in the plugin
            global ot_dep_rsmpl 
            ot_dep_rsmpl = working_dir + '/' + 'Training_sites' + '.tif'
            gdal.Warp(ot_dep_rsmpl, dep_rst_clip, format = 'GTiff', xRes = unt_m, yRes = unt_m)
            qgis.utils.iface.addRasterLayer(ot_dep_rsmpl)
            self.preProCmptMsg()
            self.tab_close()
        
        else: 
            self.depMsg()
     
    def MFSelect(self):
    
        global slctd_MF_F1_var1
        global slctd_MF_F1_var2
        global slctd_MF_F1_var3
        global slctd_MF_F2_var1
        global slctd_MF_F2_var2
        global slctd_MF_F2_var3
        global slctd_MF_outputfac_var1
        global slctd_MF_outputfac_var2
        global slctd_MF_outputfac_var3
        global MF_F1_var1
        global MF_F1_var2
        global MF_F1_var3
        global MF_F2_var1
        global MF_F2_var2
        global MF_F2_var3
        global MF_outputfac_var1
        global MF_outputfac_var2
        global MF_outputfac_var3
        slctd_MF_F1_var1 = self.dlg.MF_F1_var1.currentText()
        slctd_MF_F1_var2 = self.dlg.MF_F1_var2.currentText()
        slctd_MF_F1_var3 = self.dlg.MF_F1_var3.currentText()
        slctd_MF_F2_var1 = self.dlg.MF_F2_var1.currentText()
        slctd_MF_F2_var2 = self.dlg.MF_F2_var2.currentText()
        slctd_MF_F2_var3 = self.dlg.MF_F2_var3.currentText()
        slctd_MF_outputfac_var1 = self.dlg.MF_outputfac_var1.currentText()
        slctd_MF_outputfac_var2 = self.dlg.MF_outputfac_var2.currentText()
        slctd_MF_outputfac_var3 = self.dlg.MF_outputfac_var3.currentText()
        MF_F1_var1 = self.dlg.le_F1_var1.text()
        MF_F1_var2 = self.dlg.le_F1_var2.text()
        MF_F1_var3 = self.dlg.le_F1_var3.text()
        MF_F2_var1 = self.dlg.le_F2_var1.text()
        MF_F2_var2 = self.dlg.le_F2_var2.text()
        MF_F2_var3 = self.dlg.le_F2_var3.text()
        MF_outputfac_var1 = self.dlg.le_outputfac_var1.text()
        MF_outputfac_var2 = self.dlg.le_outputfac_var2.text()
        MF_outputfac_var3 = self.dlg.le_outputfac_var3.text() 

        fac1_vars = [MF_F1_var1, MF_F1_var2, MF_F1_var3]
        fac2_vars = [MF_F2_var1, MF_F2_var2, MF_F2_var3]
        fac3_vars = [MF_outputfac_var1, MF_outputfac_var2, MF_outputfac_var3]
        operations = ['AND', 'OR', 'Algebraic Sum','Algebraic Product']
        self.dlg.choose_MF_fac1.clear()
        self.dlg.choose_MF_fac1.addItems(fac1_vars)
        self.dlg.choose_MF_fac2.clear()
        self.dlg.choose_MF_fac2.addItems(fac2_vars)
        self.dlg.choose_MF_outputfac.clear()
        self.dlg.choose_MF_outputfac.addItems(fac3_vars)
        self.dlg.choose_operator.clear()
        self.dlg.choose_operator.addItems(operations)

        # self.dlg.le_scrt.setText(scratch_dir)

        

        return MF_F1_var1, MF_F1_var2, MF_F1_var3, MF_F2_var1, MF_F2_var2, MF_F2_var3, MF_outputfac_var1, MF_outputfac_var2, MF_outputfac_var3;              
              
    
    
        
    def tab_close(self):
        #This fucntion closes the plugin;
        self.dlg.close()
 
    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginRasterMenu(
                self.tr(u'&Weights of Evidence (WofE) Model'),
                action)
            self.iface.removeToolBarIcon(action)

    def save_fuzzy_rule(self):
        global fac1_var
        global operator
        global fac2_var
        global outputfac_var
        fac1_var = self.dlg.choose_MF_fac1.currentText()
        operator = self.dlg.choose_operator.currentText()
        fac2_var = self.dlg.choose_MF_fac2.currentText()
        outputfac_var = self.dlg.choose_MF_outputfac.currentText()



    def save_feature_vec(self):

        if(fac1_var == MF_F1_var1):
            mf = slctd_MF_F1_var1
        elif(fac1_var == MF_F1_var2):
            mf = slctd_MF_F1_var2
        else:
            mf = slctd_MF_F1_var3

        if(fac2_var == MF_F2_var1):
            mf1 = slctd_MF_F2_var1
        elif(fac2_var == MF_F2_var2):
            mf1 = slctd_MF_F2_var2
        else:
            mf1 = slctd_MF_F2_var3

        if(outputfac_var == MF_outputfac_var1):
            mf2 = slctd_MF_outputfac_var1
        elif(outputfac_var == MF_outputfac_var2):
            mf2 = slctd_MF_outputfac_var2
        else:
            mf2 = slctd_MF_outputfac_var3
        
        self.computefuzzy( mf, mf1, mf2)


    def computefuzzy(self, mf, mf1, mf2):


        if(mf == "Piecewise Linear"):
            y=(0.1*int(self.dlg.le_fac1.text()))
        elif(mf == "Gaussian"):
            y=scipy.stats.norm(0, 1).pdf(int(self.dlg.le_fac1.text()))
        elif(mf == "Sigmoid"):
            y=1/(1 + np.exp(-int(self.dlg.le_fac1.text())))
        elif(mf == "Quadratic"):
            y="4"
        elif(mf == "Cubic"):
            y="5"
        
        if(mf1 == "Piecewise Linear"):
            y1=(0.1*int(self.dlg.le_fac2.text()))
        elif(mf1 == "Gaussian"):
            y1=scipy.stats.norm(0, 1).pdf(int(self.dlg.le_fac2.text()))
        elif(mf1 == "Sigmoid"):
            y1=1/(1 + np.exp(-int(self.dlg.le_fac2.text())))
        elif(mf1 == "Quadratic"):
            y1="40"
        elif(mf1 == "Cubic"):
            y1="50"

        self.dlg.le_calc_fac1.setText(str(y))
        self.dlg.le_calc_fac2.setText(str(y1))

        if(operator == "AND"):
            final = min(y,y1)    
        elif(operator == "OR"):
            final = max(y,y1)
        elif(operator == "Algebraic Product"):
            final = y*y1
        elif(operator == "Algebraic Sum"):
            final = 1-((1-y)*(1-y1))

        self.dlg.le_calc_final.setText(str(final))

        if(mf2 == "Piecewise Linear"):
            x = 10*final
        elif(mf2 == "Gaussian"):
            x=0
        elif(mf2 == "Sigmoid"):
            x=0
        elif(mf2 == "Quadratic"):
            x=0
        elif(mf2 == "Cubic"):
            x=0

        centroid = 2*final/4

        self.dlg.le_defuzz_probab.setText(str(centroid))

    def loadRasters(self):
        self.dlg.cb_raster.clear()
        #self.dlg.cb_xtnt_rstr.clear()
        #self.dlg.cb_xtnt_rstr_rsp.clear()
        layers=[layer for layer in QgsProject.instance().mapLayers().values()]
        raster_layers=[]
        for layer in layers:
            if layer.type()==QgsMapLayer.RasterLayer:
                raster_layers.append(layer.name())
        self.dlg.cb_raster.addItems(raster_layers)   
        #self.dlg.cb_xtnt_rstr.addItems(raster_layers)
        #self.dlg.cb_xtnt_rstr_rsp.addItems(raster_layers)    

    def inp_evdnc_rst(self):
        global names_evr
        names_evr =(QFileDialog.getOpenFileNames(caption="Add evidence rasters", filter="Evidence Rasters (*.tif)")[0])
        for name in names_evr:
            self.dlg.lw_evdnc_rsts.addItem(name)
        inFile =str(names_evr)  
        print(names_evr)

    def removeSelectedEvR(self):
       for item in self.dlg.lw_evdnc_rsts.selectedItems():
            self.dlg.lw_evdnc_rsts.takeItem(self.dlg.lw_evdnc_rsts.row(item))
        
        

    def run(self):
        """Run method that performs all the real work"""

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False
            self.dlg = FISPluginDialog()
            
            # For 'Identify Factors' Tab
            
            self.dlg.no_facs.setText('')
            self.dlg.no_vars_fac1.setText('')
            self.dlg.no_vars_fac2.setText('')
            self.dlg.no_vars_outputfac.setText('')
            self.dlg.pb_pre_proc.clicked.connect(self.prepro)
            self.dlg.pb_pre_proc_cancel.clicked.connect(self.tab_close)
            

            # For 'Decide Membership Functions' Tab

            MF_type = ['Piecewise Linear', 'Gaussian', 'Sigmoid','Quadratic','Cubic']
            self.dlg.MF_F1_var1.clear()
            self.dlg.MF_F1_var1.addItems(MF_type)
            self.dlg.MF_F1_var2.clear()
            self.dlg.MF_F1_var2.addItems(MF_type)
            self.dlg.MF_F1_var3.clear()
            self.dlg.MF_F1_var3.addItems(MF_type)
            self.dlg.MF_F2_var1.clear()
            self.dlg.MF_F2_var1.addItems(MF_type)
            self.dlg.MF_F2_var2.clear()
            self.dlg.MF_F2_var2.addItems(MF_type)
            self.dlg.MF_F2_var3.clear()
            self.dlg.MF_F2_var3.addItems(MF_type)
            self.dlg.MF_outputfac_var1.clear()
            self.dlg.MF_outputfac_var1.addItems(MF_type)
            self.dlg.MF_outputfac_var2.clear()
            self.dlg.MF_outputfac_var2.addItems(MF_type)
            self.dlg.MF_outputfac_var3.clear()
            self.dlg.MF_outputfac_var3.addItems(MF_type)

        
            self.dlg.pb_decideMF.clicked.connect(self.MFSelect)
            self.dlg.pb_cancel_decideMF.clicked.connect(self.tab_close)
            self.dlg.le_F1_var1.setText('')
            self.dlg.le_F1_var2.setText('')
            self.dlg.le_F1_var3.setText('')
            self.dlg.le_F2_var1.setText('')
            self.dlg.le_F2_var2.setText('')
            self.dlg.le_F2_var3.setText('')
            self.dlg.le_outputfac_var1.setText('')
            self.dlg.le_outputfac_var2.setText('')
            self.dlg.le_outputfac_var3.setText('')
            
           # For 'Fuzzy Rules' Tab
            
            self.dlg.pb_fuzzy_rule_save.clicked.connect(self.save_fuzzy_rule)
            self.dlg.pb_fuzzy_rule_cancel.clicked.connect(self.tab_close)


            # For 'Feature Vector' Tab
            
            self.dlg.le_fac1.setText('')
            self.dlg.le_fac2.setText('')
            self.dlg.pb_feature_vec_save.clicked.connect(self.save_feature_vec)
            self.dlg.pb_feature_vec_cancel.clicked.connect(self.tab_close)


            # for the new tab
            self.dlg.pb_add_rasters.clicked.connect(self.inp_evdnc_rst)
            self.dlg.pb_remove_rasters.clicked.connect(self.removeSelectedEvR)

            


            
    
        


        
       


        
      

        # show the dialog
        self.dlg.show()
        
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass
