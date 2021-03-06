''' Graphical user interface for displaying images

@todo file list - selectable, sortable, metadata

@todo - detect raw images

.. Created on Jul 19, 2013
.. codeauthor:: Robert Langlois <rl2528@columbia.edu>
'''
from pyui.MontageViewer import Ui_MainWindow
from HelpUI import Dialog as HelpDialog
from util.qt4_loader import QtGui
from util.qt4_loader import QtCore
from util.qt4_loader import qtSlot
from AutoPickUI import Widget as AutoPickWidget
from util import qimage_utility
import property
from ..metadata import spider_utility
from ..metadata import format
from ..image import ndimage_utility
from ..image import ndimage_file
from ..image import ndimage_interpolate
from ..image import ndimage_filter
from ..image.ctf import estimate1d as estimate_ctf1d
from ..util import drawing
from ..util import plotting
from util import messagebox
import glob
import os
import numpy #, itertools
import logging

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)

class MainWindow(QtGui.QMainWindow):
    ''' Main window display for the plotting tool
    '''
    
    def __init__(self, parent=None):
        "Initialize a image display window"
        
        QtGui.QMainWindow.__init__(self, parent)
        
        # Setup logging
        root = logging.getLogger()
        while len(root.handlers) > 0: root.removeHandler(root.handlers[0])
        h = logging.StreamHandler()
        h.setFormatter(logging.Formatter('%(message)s'))
        root.addHandler(h)
        
        # Build window
        _logger.info("\rBuilding main window ...")
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        # Setup variables
        self.lastpath = str(QtCore.QDir.currentPath())
        self.loaded_images = []
        self.files = []
        self.file_index = []
        self.color_level = None
        self.base_level = None
        self.inifile = '' #'ara_view.ini'
        self.settings_group = 'ImageViewer'
        self.imagesize=0
        
        # Image View
        self.imageListModel = QtGui.QStandardItemModel(self)
        self.ui.imageListView.setModel(self.imageListModel)
        
        #self.templateListModel = QtGui.QStandardItemModel(self)
        #self.ui.templateListView.setModel(self.templateListModel)
        
        # Empty init
        self.ui.actionForward.setEnabled(False)
        self.ui.actionBackward.setEnabled(False)
        self.setup()
        
        self.ui.autopickWidget = AutoPickWidget(self)
        self.ui.tabWidget.addTab(self.ui.autopickWidget, "AutoPick")
        self.ui.tabWidget.currentChanged.connect(self.tabValid)
        
        # Custom Actions
        
        self.ui.dockWidgetAction = self.ui.dockWidget.toggleViewAction()
        self.ui.whatsThisAction = QtGui.QWhatsThis.createAction(self)
        icon8 = QtGui.QIcon()
        icon8.addPixmap(QtGui.QPixmap(":/mini/mini/application_side_list.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.ui.dockWidgetAction.setIcon(icon8)
        self.ui.dockWidgetAction.setToolTip("Show or hide the controls widget")
        self.ui.dockWidgetAction.setWhatsThis(QtGui.QApplication.translate("MainWindow", '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">\n<html><head><meta name="qrichtext" content="1" /><style type="text/css">\np, li { white-space: pre-wrap; }\n</style></head><body style=" font-family:\'Lucida Grande\'; font-size:13pt; font-weight:400; font-style:normal;">\n<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><img src=":/mini/mini/application_side_list.png" /> Display/Hide the controls widget</p>\n<p style="-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"></p>\n<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">This widget can be hidden to increase the number of images that can be shown.</p></body></html>', None, QtGui.QApplication.UnicodeUTF8))
        self.ui.toolBar.addAction(self.ui.dockWidgetAction)
        self.ui.toolBar.addAction(self.ui.whatsThisAction)
        
        # Create advanced settings
        
        property.setView(self.ui.advancedSettingsTreeView)
        self.advanced_settings, self.advanced_names = self.ui.advancedSettingsTreeView.model().addOptionList(self.advancedSettings())
        self.ui.advancedSettingsTreeView.setStyleSheet('QTreeView::item[readOnly="true"]{ color: #000000; }')
        
        for i in xrange(self.ui.advancedSettingsTreeView.model().rowCount()-1, 0, -1):
            if self.ui.advancedSettingsTreeView.model().index(i, 0).internalPointer().isReadOnly(): # Hide widget items (read only)
                self.ui.advancedSettingsTreeView.setRowHidden(i, QtCore.QModelIndex(), True)
        
        # Help system
        self.helpDialog = HelpDialog(self)
        _logger.info("\rLoading settings ...")
        self.loadSettings()
        
    def advancedSettings(self):
        '''
        '''
        
        return self.sharedAdvancedSettings()+[
               dict(average=False, help="Average images in stack rather than display individual"),
               ]
    
    def sharedAdvancedSettings(self):
        ''' Get a list of advanced settings
        '''
        
        return [ 
               # Global options
               dict(mark_image=False, help="Cross out selected images"),
               dict(downsample_type=('ft', 'bilinear', 'fs', 'sblack'), help="Choose the down sampling algorithm ranked from fastest to most accurate"),
               dict(second_image="", help="Path to a tooltip image that can be cross-indexed with the current one (SPIDER filename)", gui=dict(filetype='open')),
               dict(second_nstd=5.0, help="Outlier removal for second image loading"),
               dict(second_downsample=1.0, help="Factor to downsample second image"),
               dict(gaussian_low_pass=0.0, help="Resolution for Gaussian low pass filter"),
               dict(gaussian_high_pass=0.0, help="Resolution for Gaussian high pass filter"),
               dict(show_label=False, help="Show the labels below each image"),
               dict(current_powerspec=True, help="Is the current image displayed a power spectra?"),               
               dict(alternate_image="", help="Path to a alternate image that can be cross-indexed with the current one (SPIDER filename)", gui=dict(filetype='open')),

               # Window Options
               dict(coords="",    help="Path to coordinate file", gui=dict(filetype='open')),
               dict(good_file="", help="Highlight selected coordinates in red - unselected in blue", gui=dict(filetype='open')),
               dict(window=200, help="Size of window to box particle"),               
               dict(power_spectra=0, help="Estimate a powerspectra on the fly and save as a tool tip", gui=dict()),
               dict(invert=False, help="Perform contrast inversion"),
               dict(bin_window=6.0, help="Number of times to decimate coordinates (and window)"),
               dict(line_width=1, help="Set the line width for the boxes on the micrograph"),

               # Power spectra options
               dict(center_mask=0, help="Radius of mask for image center"),
               dict(radialAverage=False, help="Display 1D radial average (1D power spect if image is a 2D powerspec)"),
               dict(resolution_rings="", help="Display resolution rings, specific comma seperate list of resolutions: 12,6"),
               
               
               # Hidden options
               dict(zoom=self.ui.imageZoomDoubleSpinBox.value(), help="Zoom factor where 1.0 is original size", gui=dict(readonly=True, value=self.ui.imageZoomDoubleSpinBox)),
               dict(contrast=self.ui.contrastSlider.value(), help="Level of contrast in the image", gui=dict(readonly=True, value=self.ui.contrastSlider)),
               dict(imageCount=self.ui.imageCountSpinBox.value(), help="Number of images to display at once", gui=dict(readonly=True, value=self.ui.imageCountSpinBox)),
               dict(imagePage=self.ui.pageSpinBox.value(), help="Current page of images", gui=dict(readonly=True, value=self.ui.pageSpinBox)),
               dict(decimate=self.ui.decimateSpinBox.value(), help="Number of times to reduce the size of the image in memory", gui=dict(readonly=True, value=self.ui.decimateSpinBox)),
               dict(clamp=self.ui.clampDoubleSpinBox.value(), help="Bad pixel removal: higher the number less bad pixels removed", gui=dict(readonly=True, value=self.ui.clampDoubleSpinBox)),
               
               ]
            
    def currentFileList(self):
        '''
        '''
        
        #self.file_index[item.data(QtCore.Qt.UserRole), 2]
        template = self.get_template()
        files = []
        for i in xrange(self.imageListModel.rowCount()):
            idx = self.imageListModel.item(i).data(QtCore.Qt.UserRole)
            filename = self.files[self.file_index[idx, 0]]
            if template is not None: filename=spider_utility.spider_filename(template, filename)
            files.append(filename)
        return files
    
    def micrographDecimationFactor(self):
        '''
        '''
        
        return self.advanced_settings.bin_window
    
    def setWindowSize(self, window):
        '''
        '''
        
        self.advanced_settings.window=window
        
    def setAlternateImage(self, filename, emptyonly=False):
        '''
        '''
        
        if not emptyonly or self.advanced_settings.alternate_image == "":
            self.advanced_settings.alternate_image=os.path.relpath(filename)
        
    def setCoordinateFile(self, filename, emptyonly=False):
        '''
        '''
        
        if not emptyonly or self.advanced_settings.coords == "":
            self.advanced_settings.coords=os.path.relpath(filename)
        
    def closeEvent(self, evt):
        '''Window close event triggered - save project and global settings 
        
        :Parameters:
            
        evt : QCloseEvent
              Event for to close the main window
        '''
        
        self.saveSettings()
        QtGui.QMainWindow.closeEvent(self, evt)
        
    def setup(self):
        ''' Display specific setup
        '''
        
        self.ui.toolBar.removeAction(self.ui.actionSave)
        self.ui.imageListView.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
    
    # Slots for GUI
    
    def tabValid(self, index):
        '''
        '''
        
        if index != 2: return
        if not self.ui.autopickWidget.isValid():
            self.ui.tabWidget.setCurrentIndex(0)
          
    @qtSlot()
    def on_reloadPageButton_clicked(self):
        '''
        '''
        
        self.on_loadImagesPushButton_clicked()
    
    @qtSlot()
    def on_actionSwap_Image_triggered(self):
        '''
        '''
        
        self.advanced_settings.current_powerspec=not self.advanced_settings.current_powerspec
        self.on_loadImagesPushButton_clicked()
    
    @qtSlot()
    def on_actionShow_Coordinates_triggered(self):
        '''
        '''
        
        self.on_loadImagesPushButton_clicked()
           
#    @qtSlot(int)
#    def on_pageSpinBox_valueChanged(self, val):
#        ''' Called when the user changes the group number in the spin box
#        '''
#        
#        self.on_loadImagesPushButton_clicked()
    
    @qtSlot()
    def on_actionForward_triggered(self):
        ''' Called when the user clicks the next view button
        '''
        
        self.ui.pageSpinBox.setValue(self.ui.pageSpinBox.value()+1)
        self.on_loadImagesPushButton_clicked()
    
    @qtSlot()
    def on_actionBackward_triggered(self):
        ''' Called when the user clicks the previous view button
        '''
        
        self.ui.pageSpinBox.setValue(self.ui.pageSpinBox.value()-1)
        self.on_loadImagesPushButton_clicked()
    
    @qtSlot()
    def on_actionLoad_More_triggered(self):
        ''' Called when someone clicks the Open Button
        '''
        
        if len(self.files) == 0: return
        files = glob.glob(spider_utility.spider_searchpath(self.files[0]))
        _logger.info("Found %d files on %s"%(len(files), spider_utility.spider_searchpath(self.files[0])))
        if len(files) > 0:
            self.openImageFiles(files) #[str(f) for f in files if not format.is_readable(str(f))])
    
    @qtSlot()
    def on_actionOpen_triggered(self):
        ''' Called when someone clicks the Open Button
        '''
        
        files = QtGui.QFileDialog.getOpenFileNames(self.ui.centralwidget, self.tr("Open a set of images or documents"), self.lastpath)
        if isinstance(files, tuple): files = files[0]
        if len(files) > 0:
            self.lastpath = os.path.dirname(str(files[0]))
            #self.openImageFiles([str(f) for f in files if not format.is_readable(str(f))])
            self.openImageFiles(files)
    
    @qtSlot(int)
    def on_contrastSlider_valueChanged(self, value):
        ''' Called when the user uses the contrast slider
        '''
        
        if self.color_level is None: return
        
        if self.base_level is not None and len(self.base_level) > 0 and not isinstance(self.base_level[0], list):
            if value != 200:
                self.color_level = qimage_utility.adjust_level(qimage_utility.change_contrast, self.base_level, value)
            else:
                self.color_level = self.base_level
            
            for i in xrange(len(self.loaded_images)):
                self.loaded_images[i].setColorTable(self.color_level)
                pix = QtGui.QPixmap.fromImage(self.loaded_images[i])
                icon = QtGui.QIcon(pix)
                icon.addPixmap(pix,QtGui.QIcon.Normal)
                icon.addPixmap(pix,QtGui.QIcon.Selected)
                self.imageListModel.item(i).setIcon(icon)
        else:
            
            for i in xrange(len(self.loaded_images)):
                if value != 200:
                    self.color_level = qimage_utility.adjust_level(qimage_utility.change_contrast, self.base_level[i], value)
                else:
                    self.color_level = self.base_level[i]
                self.loaded_images[i].setColorTable(self.color_level)
                pix = QtGui.QPixmap.fromImage(self.loaded_images[i])
                icon = QtGui.QIcon(pix)
                icon.addPixmap(pix,QtGui.QIcon.Normal)
                icon.addPixmap(pix,QtGui.QIcon.Selected)
                self.imageListModel.item(i).setIcon(icon)
            
    
    @qtSlot(int)
    def on_zoomSlider_valueChanged(self, zoom):
        '''
        '''
        
        zoom = zoom/float(self.ui.zoomSlider.maximum())
        self.ui.imageZoomDoubleSpinBox.blockSignals(True)
        self.ui.imageZoomDoubleSpinBox.setValue(zoom)
        self.ui.imageZoomDoubleSpinBox.blockSignals(False)
        self.on_imageZoomDoubleSpinBox_valueChanged(zoom)
    
    @qtSlot(float)
    def on_imageZoomDoubleSpinBox_valueChanged(self, zoom=None):
        ''' Called when the user wants to plot only a subset of the data
        
        :Parameters:
        
        index : int
                New index in the subset combobox
        '''
        
        if zoom is None: zoom = self.ui.imageZoomDoubleSpinBox.value()
        self.ui.zoomSlider.blockSignals(True)
        self.ui.zoomSlider.setValue(int(self.ui.zoomSlider.maximum()*zoom))
        self.ui.zoomSlider.blockSignals(False)
        
        if self.imagesize > 0:
            n = max(5, int(self.imagesize*zoom))
            self.ui.imageListView.setIconSize(QtCore.QSize(n, n))
    
    def get_template(self):
        '''
        '''
        
        template = None
        load_alternate = self.ui.actionSwap_Image.isChecked()
        if self.advanced_settings.alternate_image != "" and load_alternate:
            template = self.advanced_settings.alternate_image
            if not os.path.exists(template) and hasattr(self.advanced_settings, 'path_prefix'):
                template = os.path.join(self.advanced_settings.path_prefix, template)
        return template
    
    @qtSlot()
    def on_loadImagesPushButton_clicked(self):
        ''' Load the current batch of images into the list
        '''
        
        if len(self.files) == 0: return
        self.imageListModel.clear()
        index, start=self.imageSubset(self.ui.pageSpinBox.value()-1, self.ui.imageCountSpinBox.value())
        if len(index) == 0:
            self.ui.pageSpinBox.blockSignals(True)
            self.ui.pageSpinBox.setValue(0)
            self.ui.pageSpinBox.blockSignals(False)
            self.ui.imageCountSpinBox.blockSignals(True)
            self.ui.imageCountSpinBox.setValue(1)
            self.ui.imageCountSpinBox.blockSignals(False)
            index, start=self.imageSubset(0, 1)
        bin_factor = self.ui.decimateSpinBox.value()
        nstd = self.ui.clampDoubleSpinBox.value()
        img = None
        self.loaded_images = []
        self.base_level=None
        zoom = self.ui.imageZoomDoubleSpinBox.value()
        masks={}
        
        template = self.get_template()
        
        progressDialog = QtGui.QProgressDialog('Opening...', "Cancel", 0,len(index),self)
        progressDialog.setWindowModality(QtCore.Qt.WindowModal)
        progressDialog.show()
        
        self.ui.imageListView.setModel(None)
        
        if not drawing.is_available():
            _logger.info("No PIL loaded")
            self.advanced_settings.mark_image=False
        if not plotting.is_available():
            _logger.info("No matplotlib loaded")
            self.advanced_settings.mark_image=False
        
        current_powerspec = self.advanced_settings.current_powerspec
        if current_powerspec:
            if self.advanced_settings.invert:
                _logger.info("Cannot invert a power spectra")
        else:
            if self.advanced_settings.center_mask > 0:
                _logger.info("Cannot mask micrograph")
        
        added_items=[]
        for i, (imgname, img, pixel_size) in enumerate(iter_images(self.files, index, template)):
            selimg = None
            progressDialog.setValue(i+1)
            if hasattr(img, 'ndim'):
                if current_powerspec and self.advanced_settings.center_mask > 0 and img.shape not in masks:
                    masks[img.shape]=ndimage_utility.model_disk(self.advanced_settings.center_mask, img.shape)*-1+1
                if self.advanced_settings.invert and not current_powerspec:
                    if img.max() != img.min(): ndimage_utility.invert(img, img)
                img = ndimage_utility.replace_outlier(img, nstd, nstd, replace='mean')
                if self.advanced_settings.gaussian_high_pass > 0.0:
                    img=ndimage_filter.filter_gaussian_highpass(img, pixel_size/self.advanced_settings.gaussian_high_pass)
                if self.advanced_settings.gaussian_low_pass > 0.0:
                    img=ndimage_filter.filter_gaussian_lowpass(img, pixel_size/self.advanced_settings.gaussian_low_pass)
                if current_powerspec and self.advanced_settings.center_mask > 0:
                    #img[numpy.logical_not(masks[img.shape])] = numpy.mean(img[masks[img.shape]])
                    img *= masks[img.shape]
                if bin_factor > 1.0: img = ndimage_interpolate.interpolate(img, bin_factor, self.advanced_settings.downsample_type)
                pixel_size *= bin_factor
                img = self.display_powerspectra_1D(img, imgname, pixel_size)
                img = self.display_resolution(img, imgname, pixel_size)
                img = self.box_particles(img, imgname)
                if self.advanced_settings.mark_image:
                    imgm = self.imageMarker(img)
                    selimg = qimage_utility.numpy_to_qimage(imgm)
                qimg = qimage_utility.numpy_to_qimage(img)
                if img.ndim == 2:
                    if self.base_level is not None:
                        qimg.setColorTable(self.color_level)
                    else: 
                        self.base_level = qimg.colorTable()
                        self.color_level = qimage_utility.adjust_level(qimage_utility.change_contrast, self.base_level, self.ui.contrastSlider.value())
                        qimg.setColorTable(self.color_level)
                else:
                    if self.base_level is None: self.base_level = []
                    self.base_level.append(qimg.colorTable())
                    self.color_level = qimage_utility.adjust_level(qimage_utility.change_contrast, self.base_level[-1], self.ui.contrastSlider.value())
                    qimg.setColorTable(self.color_level)
                    
            else:
                qimg = img.convertToFormat(QtGui.QImage.Format_Indexed8)
                if self.base_level is None: self.base_level = []
                self.base_level.append(qimg.colorTable())
                self.color_level = qimage_utility.adjust_level(qimage_utility.change_contrast, self.base_level[-1], self.ui.contrastSlider.value())
                qimg.setColorTable(self.color_level)
            self.loaded_images.append(qimg)
            pix = QtGui.QPixmap.fromImage(qimg)
            icon = QtGui.QIcon()
            icon.addPixmap(pix,QtGui.QIcon.Normal)
            if selimg is not None:
                pix = QtGui.QPixmap.fromImage(selimg)
            icon.addPixmap(pix,QtGui.QIcon.Selected)
            if self.advanced_settings.show_label:
                item = QtGui.QStandardItem(icon, "%s/%d"%(os.path.basename(imgname[0]), imgname[1]+1))
            else:
                item = QtGui.QStandardItem(icon, "")
            if hasattr(start, '__iter__'):
                item.setData(start[i], QtCore.Qt.UserRole)
            else:
                item.setData(i+start, QtCore.Qt.UserRole)
            
            self.addToolTipImage(imgname, item, pixel_size)
            self.imageListModel.appendRow(item)
            added_items.append(item)
            
        self.ui.imageListView.setModel(self.imageListModel)
        progressDialog.hide()
        for item in added_items:self.notify_added_item(item)
        
        self.imagesize = img.shape[0] if hasattr(img, 'shape') else img.width()
        n = max(5, int(self.imagesize*zoom))
        self.ui.imageListView.setIconSize(QtCore.QSize(n, n))
        
        batch_count = numpy.ceil(float(self.imageTotal())/self.ui.imageCountSpinBox.value())
        self.ui.pageSpinBox.setSuffix(" of %d"%batch_count)
        self.ui.pageSpinBox.setMaximum(batch_count)
        self.ui.actionForward.setEnabled(self.ui.pageSpinBox.value() < batch_count)
        self.ui.actionBackward.setEnabled(self.ui.pageSpinBox.value() > 0)
    
    def imageMarker(self, img):
        '''
        '''
        
        return drawing.mark(img)
    # Abstract methods
    
    def imageSubset(self, index, count):
        '''
        '''
        
        if hasattr(self.advanced_settings, 'average') and self.advanced_settings.average:
            return self.files[index*count:(index+1)*count], index*count
        return self.file_index[index*count:(index+1)*count], index*count
    
    def imageTotal(self):
        '''
        '''
        
        if hasattr(self.advanced_settings, 'average') and self.advanced_settings.average:
            return len(self.files)
        
        return len(self.file_index)
    
    def notify_added_item(self, item):
        '''
        '''
        
        pass
    
    def notify_added_files(self, newfiles):
        '''
        '''
        
        pass
    
    # Other methods
    
    def addToolTipImage(self, imgname, item, apix):
        '''
        '''
        
        if imgname[1] == 0 and self.advanced_settings.second_image != "":
            second_image = spider_utility.spider_filename(self.advanced_settings.second_image, imgname[0])
            if not os.path.exists(second_image) and hasattr(self.advanced_settings, 'path_prefix'):
                second_image = os.path.join(self.advanced_settings.path_prefix, second_image)
            if os.path.exists(second_image):
                img = read_image(second_image)
                if hasattr(img, 'ndim'):
                    nstd = self.advanced_settings.second_nstd
                    bin_factor = self.advanced_settings.second_downsample
                    if nstd > 0: img = ndimage_utility.replace_outlier(img, nstd, nstd, replace='mean')
                    if bin_factor > 1.0: img = ndimage_interpolate.interpolate(img, bin_factor, self.advanced_settings.downsample_type)
                    qimg = qimage_utility.numpy_to_qimage(img)
                else:
                    qimg = img.convertToFormat(QtGui.QImage.Format_Indexed8)
                item.setToolTip(qimage_utility.qimage_to_html(qimg))
        elif self.advanced_settings.power_spectra > 3:
            if self.advanced_settings.current_powerspec:
                _logger.info("Cannot estimate a periodgram of a power spectra")
                return
            mic = ndimage_file.read_image(imgname[0], imgname[1])
            print "Start estimation"
            img = ndimage_utility.perdiogram(mic, self.advanced_settings.power_spectra, 1, 0.5, 0)
            nstd = self.advanced_settings.second_nstd
            if nstd > 0: img = ndimage_utility.replace_outlier(img, nstd, nstd, replace='mean')
            print "Finished estimation"
            qimg = qimage_utility.numpy_to_qimage(img)
            item.setToolTip(qimage_utility.qimage_to_html(qimg))
        else:
            item.setToolTip('%d@%s - %f'%(imgname[1], imgname[0], apix))
    
    def display_powerspectra_1D(self, img, fileid, pixel_size):
        '''
        '''
        
        if not plotting.is_available():
            _logger.warn("No matplotlib loaded")
            return img
        
        current_powerspec = self.advanced_settings.current_powerspec
        if not current_powerspec and self.advanced_settings.radialAverage:
            _logger.info("Cannot calculate 1D from micrograph, requires powerspectra")
        if not self.advanced_settings.radialAverage or not current_powerspec: return img
        

        
        raw = ndimage_utility.mean_azimuthal(img)[:img.shape[0]/2]
        #raw[1:] = raw[:len(raw)-1]
        raw[:2]=0
        roo = estimate_ctf1d.subtract_background(raw, int(len(raw)*0.2))
        freq = numpy.arange(len(roo), dtype=numpy.float)

        return plotting.plot_line_on_image(img, freq+len(roo), roo, dpi=128)
    
    def display_resolution(self, img, fileid, pixel_size):
        '''
        '''
        
        if not plotting.is_available():
            _logger.warn("No matplotlib loaded")
            return img
        
        current_powerspec = self.advanced_settings.current_powerspec
        if not current_powerspec and self.advanced_settings.resolution_rings:
            _logger.info("Cannot display resolution rings, requires powerspectra")
        if not self.advanced_settings.resolution_rings.strip() or not current_powerspec: return img
        if pixel_size == 0:
            _logger.error("Cannot display rings: no pixel size in header of image")
            return img
        
        st = int(numpy.ceil(((img.shape[0]+1)/2.0)))
        res_vals=[]
        for res in self.advanced_settings.resolution_rings.split(','):
            try: res=float(res)
            except: _logger.error("Resolution must be comma seperated list of floats, not %s"%str(res))
            else:res_vals.append(estimate_ctf1d.resolution(res, st, pixel_size))
        if len(res_vals)==0: return img
        return plotting.plot_circles_on_image(img, res_vals, force_gray=True, linewidth=1, dpi=128)
    
    def display_powerspectra_1D_old(self, img, fileid, pixel_size):
        '''
        '''
        from ..image import peakdetect_1d
        
        if not plotting.is_available():
            _logger.warn("No matplotlib loaded")
            return img
        
        current_powerspec = self.advanced_settings.current_powerspec
        if not current_powerspec and self.advanced_settings.radialAverage:
            _logger.info("Cannot calculate 1D from micrograph, requires powerspectra")
        if not self.advanced_settings.radialAverage or not current_powerspec: return img
        
        st = int(numpy.ceil(((img.shape[0]+1)/2.0)))
        
        if pixel_size == 0: pixel_size=1.58
        rmin = 15.0
        rmax = 12.0
        if rmin < rmax: rmin, rmax = rmax, rmin
        min_freq = pixel_size/rmin
        max_freq = pixel_size/rmax
        rmin = min_freq*img.shape[0]
        rmax = max_freq*img.shape[0]
        rang = (rmax-rmin)/2.0
        freq2 = float(img.shape[0])/(rang/1)
        freq1 = float(img.shape[0])/(rang/15)
        #img=ndimage_filter.filter_annular_bp(img, freq1, freq2, 2)
        
        raw = ndimage_utility.mean_azimuthal(img)[:img.shape[0]/2]
        #raw[1:] = raw[:len(raw)-1]
        raw[:2]=0
        roo=raw
        roo = estimate_ctf1d.subtract_background(raw, int(len(raw)*0.2))
        #roo -= roo.mean()
        freq = numpy.arange(len(roo), dtype=numpy.float)
        peaks = peakdetect_1d.peakdetect(roo, lookahead=5)[0]
        #peaks = peakdetect_1d.peakdetect_fft(roo, freq)[0]
        
        '''
        energy=.7
        roo=numpy.abs(roo)
        rad = numpy.searchsorted(numpy.cumsum(roo)/roo.sum(), energy)
        n = img.shape[0] - int(numpy.ceil(((img.shape[0]+1)/2.0)))
        e = pixel_size/( (0.5*rad)/float(n) )
        print e
        '''
        nimg= plotting.plot_circles_on_image(img, [peaks[i][0] for i in xrange(min(3, len(peaks)))], force_gray=True, linewidth=1, dpi=128)
        return nimg
        return plotting.plot_line_on_image(nimg, freq+len(roo), roo)
    
    def box_particles(self, img, fileid):
        ''' Draw particle boxes on each micrograph
        '''
        
        if not drawing.is_available():
            _logger.warn("No PIL loaded")
            return img
        show_coords = self.ui.actionShow_Coordinates.isChecked()
        current_powerspec = self.advanced_settings.current_powerspec
        if self.advanced_settings.coords == "" or not show_coords or current_powerspec: return img
        if isinstance(fileid, tuple): fileid=fileid[0]
        coords = self.advanced_settings.coords
        if not os.path.exists(coords) and hasattr(self.advanced_settings, 'path_prefix'):
            coords = os.path.join(self.advanced_settings.path_prefix, coords)
        good_file = self.advanced_settings.good_file
        if good_file != "" and not os.path.exists(good_file) and hasattr(self.advanced_settings, 'path_prefix'):
            good_file = os.path.join(self.advanced_settings.path_prefix, good_file)
        
        try:
            coords=format.read(coords, spiderid=fileid, numeric=True)
        except: 
            _logger.exception("Cannot find coordinate file: %s for id %s"%(coords, str(fileid)))
            return img
        select=None
        try:
            select=format.read(good_file, spiderid=fileid, ndarray=True)[0].astype(numpy.int) if good_file != "" else None
        except: 
            _logger.exception("Cannot find selection file: %s for id %s"%(good_file, str(fileid)))
        bin_factor=self.advanced_settings.bin_window
        line_width = self.advanced_settings.line_width
        if select is not None:
            img = drawing.draw_particle_boxes(img, coords, self.advanced_settings.window/bin_factor, bin_factor, outline="blue", width=line_width)
            return drawing.draw_particle_boxes_to_array(img, [coords[i-1] for i in select[:, 0]], self.advanced_settings.window/bin_factor, bin_factor, width=line_width)
        else:
            return drawing.draw_particle_boxes_to_array(img, coords, self.advanced_settings.window/bin_factor, bin_factor, width=line_width)
    
    def openImageFiles(self, files, notify=True):
        ''' Open a collection of image files, sort by content type
        
        :Parameters:
        
        files : list
                List of input files
        '''
        
        fileset=set(self.files)
        files = [os.path.abspath(f) for f in files]
        newfiles = sorted([f for f in files if f not in fileset])
        imgfiles = [f for f in newfiles if not ndimage_file.is_readable(f)]
        if len(imgfiles) > 0:
            messagebox.error_message(self, "File open failed - found non-image files. See details.", "\n".join(imgfiles))
            return
        if notify: self.notify_added_files(newfiles)
        self.updateFileIndex(newfiles)
        self.files.extend(newfiles)
        self.setWindowTitle("File count: %d - Image count: %d"%(len(self.files), len(self.file_index)))
        self.on_loadImagesPushButton_clicked()
        
    def updateFileIndex(self, newfiles):
        '''
        '''
        
        #self.templateListModel
        
        if hasattr(self.file_index, 'ndim'):
            self.file_index = self.file_index.tolist()
        index = len(self.files)
        for filename in newfiles:
            count = ndimage_file.count_images(filename)
            self.file_index.extend([[index, i, 0] for i in xrange(count)])
            index += 1
        self.file_index = numpy.asarray(self.file_index)
        
    def getSettings(self):
        ''' Get the settings object
        '''
        
        '''
        return QtCore.QSettings(QtCore.QSettings.IniFormat, QtCore.QSettings.UserScope, "Arachnid", "ImageView")
        '''
        
        if self.inifile == "": return None
        settings = QtCore.QSettings(self.inifile, QtCore.QSettings.IniFormat)
        return settings
    
    def saveReadOnly(self):
        '''
        '''
        
        current_state = self.advancedSettings()
        for state in current_state:
            if 'gui' in state and 'readonly' in state['gui'] and state['gui']['readonly'] and 'value' in state['gui']:
                keys = [key for key in state.keys() if key not in ('gui', 'help')]
                if len(keys) != 1: raise ValueError, "Cannot find unique key: %s"%str(keys)
                widget = state['gui']['value']
                name = keys[0]
                setattr(self.advanced_settings, name, widget.value())
    
    def loadReadOnly(self):
        '''
        '''
        
        current_state = self.advancedSettings()
        for state in current_state:
            if 'gui' in state and 'readonly' in state['gui'] and state['gui']['readonly'] and 'value' in state['gui']:
                keys = [key for key in state.keys() if key not in ('gui', 'help')]
                if len(keys) != 1: raise ValueError, "Cannot find unique key: %s"%str(keys)
                widget = state['gui']['value']
                name = keys[0]
                widget.setValue(getattr(self.advanced_settings, name))
        
    def saveSettings(self):
        ''' Save the settings of widgets
        '''
        
        self.saveReadOnly()
        settings = self.getSettings()
        if settings is None: return
        settings.beginGroup(self.settings_group)
        settings.setValue('main_window/geometry', self.saveGeometry())
        settings.setValue('main_window/windowState', self.saveState())
        settings.beginGroup('Advanced')
        self.ui.advancedSettingsTreeView.model().saveState(settings)
        settings.endGroup()
        settings.endGroup()
        
    def loadSettings(self):
        ''' Load the settings of widgets
        '''
        
        settings = self.getSettings()
        if settings is None: return
        settings.beginGroup(self.settings_group)
        self.restoreGeometry(settings.value('main_window/geometry'))
        self.restoreState(settings.value('main_window/windowState'))
        settings.beginGroup('Advanced')
        self.ui.advancedSettingsTreeView.model().restoreState(settings) #@todo - does not work!
        settings.endGroup()
        self.loadReadOnly()
        settings.endGroup()

def read_image(filename, index=None):
    '''
    '''
    
    qimg = QtGui.QImage()
    if qimg.load(filename): return qimg
    return ndimage_utility.normalize_min_max(ndimage_file.read_image(filename, index))

def iter_images(files, index, template=None, average=False):
    ''' Wrapper for iterate images that support color PNG files
    
    :Parameters:
    
    filename : str
               Input filename
    
    :Returns:
    
    img : array
          Image array
    '''
    
    qimg = QtGui.QImage()
    if template is not None: filename=spider_utility.spider_filename(template, files[0])
    else: filename = files[0]
    header={}
    if qimg.load(filename):
        if isinstance(index[0], str): files = index
        else:files = [files[i[0]] for i in index]
        for filename in files:
            qimg = QtGui.QImage()
            if template is not None: filename=spider_utility.spider_filename(template, filename)
            if not qimg.load(filename): 
                qimg=QtGui.QPixmap(":/mini/mini/cross.png").toImage()
                _logger.warn("Unable to read image - %s"%filename)
                #raise IOError, "Unable to read image - %s"%filename
            yield (filename,0), qimg, 1.0
    else:
        # todo reorganize with
        '''
        for img in itertools.imap(ndimage_utility.normalize_min_max, ndimage_file.iter_images(filename, index)):
        '''
        if isinstance(index[0], str):
            for f in index:
                avg = None
                if template is not None: 
                    f1=spider_utility.spider_filename(template, f)
                    if os.path.exists(f1): f=f1
                    else: _logger.warn("Unabled to find alternate image: %s"%f1)
                for img in ndimage_file.iter_images(f, header=header):
                    if avg is None: avg = img
                    else: avg+=img
                try:
                    img = ndimage_utility.normalize_min_max(avg)
                except: img=avg
                yield (f, 0), img, header.get('apix', 1.0)
        else:
            for idx in index:
                f, i = idx[:2]
                filename = files[f]
                if template is not None: filename=spider_utility.spider_filename(template, filename)
                try:
                    img = ndimage_file.read_image(filename, i, header=header) 
                except:
                    _logger.exception("Error while reading!")
                    img = ndimage_file.read_image(filename, header=header)
                    #print f, i, len(files), files[f], template, filename
                    #raise
                try:img=ndimage_utility.normalize_min_max(img)
                except: pass
                yield (filename, i), img, header.get('apix', 1.0)
        '''
        for filename in files:
            for i, img in enumerate(itertools.imap(ndimage_utility.normalize_min_max, ndimage_file.iter_images(filename))):
                yield (filename, i), img
        '''
            

    