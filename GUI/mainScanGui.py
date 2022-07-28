from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QDialog, QMessageBox, QPushButton
from PyQt5.uic import loadUi
import sys
import json
import PySpin
from matplotlib import image
import dds9m
import serial

# Necessary Plotting imports
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

# Image and Centroid Finding Imports
from PIL import Image


NUM_SPOTS = 0
SPOTS_TO_SCAN = []

class MainWindow(QDialog): 
    def __init__(self):
        super(MainWindow, self).__init__()
        loadUi("mainScanGui.ui", self)
         # Bind all the button clicks in the main window
        self.scanButton.clicked.connect(self.goToScan)
        self.calibrateBtn.clicked.connect(self.go_to_calibrate)
        self.statusLabel.setText("Status: Calibration Required")
        self.statusLabel.setStyleSheet("color: red;")

    def goToScan(self): 
        print("Scan Function Reached")
        global NUM_SPOTS
        NUM_SPOTS = self.numSpotSelect.value()
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def go_to_calibrate(self):
        import GUI.mainCalibrationGui
        widget.close()
    

class ScanWindow(QDialog):
    global SPOTS_TO_SCAN
    def __init__(self):
        super(ScanWindow, self).__init__()
        self.chart = Canvas(self)
        self.chart.setFixedWidth(800)
        self.chart.setFixedHeight(500)
        loadUi("scanningNeurons.ui", self)
        self.resetBtn.clicked.connect(self.reset_spots)
        self.calibrateBtn.clicked.connect(self.go_to_calibrate)
        self.wizardBtn.clicked.connect(self.go_to_wizard)
        self.scanBtn.clicked.connect(self.activate_scan)
      
    def reset_spots(self):
        self.chart.hide() 
        SPOTS_TO_SCAN = []
        chart = Canvas(self)
        chart.setFixedWidth(800)
        chart.setFixedHeight(500)
        chart.show()  

    def go_to_calibrate(self):
        import mainCalibrationGui
        self.newWindow = mainCalibrationGui.widget
        self.newWindow.show()
        widget.close()
    
    def go_to_wizard(self):
        widget.setCurrentIndex(widget.currentIndex() - 1)

    def activate_scan(self):
        global ser
        baud_rate = 19200
        timeout_sec = 5
        portname ='/dev/cu.usbserial-FT3J30KX'
        ser = serial.Serial(portname, baud_rate, timeout=timeout_sec)
        dds9m.main(ser)
        return
        

class Canvas(FigureCanvas):
    num_clicks = 0
    spots = []
    global NUM_SPOTS
    global SPOTS_TO_SCAN
    def __init__(self, parent):
        fig, self.ax = plt.subplots(figsize=(5, 4), dpi=150)
        super().__init__(fig)
        self.setParent(parent)

        """ 
        Matplotlib Script
        """
        system = PySpin.System.GetInstance()
        cam = (system.GetCameras())[0]
        nodemap_tldevice = cam.GetTLDeviceNodeMap()
        # Initialize camera
        cam.Init()
        # Retrieve GenICam nodemap
        nodemap = cam.GetNodeMap()
        # Acquire images
        sNodemap = cam.GetTLStreamNodeMap()
        # Change bufferhandling mode to NewestOnly
        node_bufferhandling_mode = PySpin.CEnumerationPtr(sNodemap.GetNode('StreamBufferHandlingMode'))
        if not PySpin.IsAvailable(node_bufferhandling_mode) or not PySpin.IsWritable(node_bufferhandling_mode):
            print('Unable to set stream buffer handling mode.. Aborting...')
            return False
        # Retrieve entry node from enumeration node
        node_newestonly = node_bufferhandling_mode.GetEntryByName('NewestOnly')
        if not PySpin.IsAvailable(node_newestonly) or not PySpin.IsReadable(node_newestonly):
            print('Unable to set stream buffer handling mode.. Aborting...')
            return False
        # Retrieve integer value from entry node
        node_newestonly_mode = node_newestonly.GetValue()
        # Set integer value from entry node as new value of enumeration node
        node_bufferhandling_mode.SetIntValue(node_newestonly_mode)

        try:
            node_acquisition_mode = PySpin.CEnumerationPtr(nodemap.GetNode('AcquisitionMode'))
            if not PySpin.IsAvailable(node_acquisition_mode) or not PySpin.IsWritable(node_acquisition_mode):
                print('Unable to set acquisition mode to continuous (enum retrieval). Aborting...')
                return False

            # Retrieve entry node from enumeration node
            node_acquisition_mode_continuous = node_acquisition_mode.GetEntryByName('Continuous')
            if not PySpin.IsAvailable(node_acquisition_mode_continuous) or not PySpin.IsReadable(
                    node_acquisition_mode_continuous):
                print('Unable to set acquisition mode to continuous (entry retrieval). Aborting...')
                return False
            acquisition_mode_continuous = node_acquisition_mode_continuous.GetValue()
            node_acquisition_mode.SetIntValue(acquisition_mode_continuous)
            print('Acquisition mode set to continuous...')
            cam.BeginAcquisition()
            print('Acquiring images...')
            device_serial_number = ''
            node_device_serial_number = PySpin.CStringPtr(nodemap_tldevice.GetNode('DeviceSerialNumber'))
            if PySpin.IsAvailable(node_device_serial_number) and PySpin.IsReadable(node_device_serial_number):
                device_serial_number = node_device_serial_number.GetValue()
                print('Device serial number retrieved as %s...' % device_serial_number)

            while(True):
                try:    
                    image_result = cam.GetNextImage(1000)
                    if image_result.IsIncomplete():
                        print('Image incomplete with image status %d ...' % image_result.GetImageStatus())

                    else:                    

                        # Getting the image data as a numpy array
                        image_data = image_result.GetNDArray()
                        im = image_data.convert('L')
                        # Draws an image on the current figure
                        plt.imshow(im, cmap='gray')
                        for pair in SPOTS_TO_SCAN:
                            plt.plot(pair[0], pair[1], marker="+", ms=5, mew=1, color="red")
                        plt.pause(0.001)
                        plt.clf()

                    image_result.Release()
                
                except PySpin.SpinnakerException as ex:
                    print('Error: %s' % ex)

        except PySpin.SpinnakerException as ex:
            print('Error: %s' % ex)

        # im = np.array(Image.open('scanningTest.png').convert('L'))
        def mouse_event(event):
            if self.num_clicks < NUM_SPOTS:
                self.ax.plot(event.xdata, event.ydata, marker="+", ms=5, mew=1, color="red")
                self.num_clicks += 1
                SPOTS_TO_SCAN.append((event.xdata, event.ydata))

            else: 
              msg = QMessageBox()
              msg.setIcon(QMessageBox.Critical)
              msg.setText("Error")
              msg.setInformativeText("You have clicked too many spots.")
              msg.setWindowTitle("Error")
              msg.exec_()    

        
        cid = fig.canvas.mpl_connect('button_press_event', mouse_event)


app = QApplication(sys.argv)
widget = QtWidgets.QStackedWidget()
mainWindow = MainWindow()
scanWindow = ScanWindow()
widget.addWidget(mainWindow)
widget.addWidget(scanWindow)
widget.setFixedHeight(600)
widget.setFixedWidth(800)
widget.show()


try:
    sys.exit(app.exec_())
except:
    print("Exiting")


