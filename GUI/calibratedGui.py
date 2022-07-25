from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QDialog, QMessageBox, QPushButton
from PyQt5.uic import loadUi
import sys
import json

# Necessary Plotting imports
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

# Image and Centroid Finding Imports
from PIL import Image
from photutils.datasets import make_4gaussians_image
from photutils.centroids import centroid_com, centroid_quadratic
from photutils.centroids import centroid_1dg, centroid_2dg


SPOTS_TO_SCAN = 0

class MainWindow(QDialog): 
    def __init__(self):
        super(MainWindow, self).__init__()
        loadUi("mainScanGui.ui", self)
         # Bind all the button clicks in the main window
        self.scanButton.clicked.connect(self.goToScan)
        self.calibrateBtn.clicked.connect(self.go_to_calibrate)
        self.statusLabel.setText("Status: Calibration Complete")

    def goToScan(self): 
        print("Scan Function Reached")
        global SPOTS_TO_SCAN
        SPOTS_TO_SCAN = self.numSpotSelect.value()
        widget.setCurrentIndex(widget.currentIndex() + 1)

    
    def go_to_calibrate(self):
        import GUI.mainCalibrationGui
        self.newWindow = GUI.mainCalibrationGui.widget
        self.newWindow.show()
        widget.close()
    
class ScanWindow(QDialog):
    def __init__(self):
        super(ScanWindow, self).__init__()
        self.chart = Canvas(self)
        self.chart.setFixedWidth(800)
        self.chart.setFixedHeight(500)
        loadUi("scanningNeurons.ui", self)
        self.resetBtn.clicked.connect(self.reset_spots)
        self.calibrateBtn.clicked.connect(self.go_to_calibrate)
        self.wizardBtn.clicked.connect(self.go_to_wizard)
      
    def reset_spots(self): 
        self.chart.hide() 
        chart = Canvas(self)
        chart.setFixedWidth(800)
        chart.setFixedHeight(500)
        chart.show()  

    def go_to_calibrate(self):
        import GUI.mainCalibrationGui as mainCalibrationGui
        self.newWindow = mainCalibrationGui.widget
        self.newWindow.show()
        widget.close()
    
    def go_to_wizard(self):
        widget.setCurrentIndex(widget.currentIndex() - 1)



class Canvas(FigureCanvas):
    num_clicks = 0
    spots = []
    global SPOTS_TO_SCAN
    def __init__(self, parent):
        fig, self.ax = plt.subplots(figsize=(5, 4), dpi=150)
        super().__init__(fig)
        self.setParent(parent)

        """ 
        Matplotlib Script
        """
        im = np.array(Image.open('scanningTest.png').convert('L'))
        x1, x2 = centroid_com(im)
        print((x1, x2))  

        def mouse_event(event):
            if self.num_clicks < SPOTS_TO_SCAN:
                plt.plot(event.xdata, event.ydata, marker="+", ms=5, mew=1, color="red")
                fig.canvas.draw()
                self.num_clicks += 1
            
            else: 
              msg = QMessageBox()
              msg.setIcon(QMessageBox.Critical)
              msg.setText("Error")
              msg.setInformativeText("You have clicked too many spots.")
              msg.setWindowTitle("Error")
              msg.exec_()    

        
        cid = fig.canvas.mpl_connect('button_press_event', mouse_event)
        plt.imshow(im)


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


