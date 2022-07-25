import sys
import json

# All necessary PyQt5 imports
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QDialog, QApplication, QMainWindow, QMessageBox, QLabel, QTableWidgetItem, QPushButton
from PyQt5.Qt import Qt

# Necessary Plotting imports
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

# Image and Centroid Finding Imports
from PIL import Image
from photutils.centroids import centroid_com

# Acquire Image
import cameraAcquisition
import dds9m





currentCalibrationSpot = 0
calibrationPositionData = {}
NUM_SPOTS = 4

class MainWindow(QDialog):
    frequencyJson = {}
    def __init__(self):
        super(MainWindow, self).__init__()
        loadUi("mainCalibrationGui.ui", self)

        # Bind all the button clicks in the main window
        self.addButton.clicked.connect(self.add_entry)
        self.resetButton.clicked.connect(self.reset_table)
        self.calibrateButton.clicked.connect(self.go_to_calibration)

        # Initialize properties of the table
        self.tableWidget.setColumnCount(2)
        # self.tableWidget.setRowCount(0)
        self.tableWidget.setHorizontalHeaderLabels(("X Frequency", "Y Frequency"))

        with open("settings.json", "r") as jsonFile:
                data = json.load(jsonFile)

        for i, val in enumerate(data['calibrationFrequencies']):
            x_item = QTableWidgetItem(str(val[0]))
            y_item = QTableWidgetItem(str(val[1]))
            x_item.setTextAlignment(Qt.AlignCenter)
            y_item.setTextAlignment(Qt.AlignCenter)

            self.tableWidget.insertRow(i)
            self.tableWidget.setItem(i, 0, x_item)
            self.tableWidget.setItem(i, 1, y_item)
        

        # Initialize properties of the spinwheel
        self.numPairSelect.setMinimum(2)
        self.numPairSelect.setMaximum(8)

        widget.show()


    def go_to_calibration(self):
        # TODO: CHECK IF THE USER HAS INPUTTED ENOUGH TABLES
        global NUM_SPOTS
        NUM_SPOTS = self.numPairSelect.value()
        print("Calibration Function Reached")
        widget.setCurrentIndex(widget.currentIndex() + 1)
        widget.show()

    def reset_table(self):
        # TODO: RESET THE JSON FILE
        self.tableWidget.setRowCount(0)
        with open("settings.json", "r") as jsonFile:
            data = json.load(jsonFile)

        data["calibrationFrequencies"] = []

        with open("settings.json", "w") as jsonFile:
            json.dump(data, jsonFile)

        
    def add_entry(self):
        currentRowCount = self.tableWidget.rowCount()
        if (currentRowCount < self.numPairSelect.value()): 
            x_freq = self.x_freq_input.text()
            y_freq = self.y_freq_input.text()

            if not x_freq.isnumeric() or not y_freq.isnumeric():
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText("Error")
                msg.setInformativeText('Please only input numeric values to the frequency list.')
                msg.setWindowTitle("Error")
                msg.exec_()
                return

            try:
                x_item = QTableWidgetItem(x_freq)
                y_item = QTableWidgetItem(y_freq)
                x_item.setTextAlignment(Qt.AlignCenter)
                y_item.setTextAlignment(Qt.AlignCenter)

                self.tableWidget.insertRow(currentRowCount)
                self.tableWidget.setItem(currentRowCount, 0, x_item)
                self.tableWidget.setItem(currentRowCount, 1, y_item)

                self.frequencyJson[currentRowCount] = (x_freq, y_freq)
                print(self.frequencyJson)

                with open('frequencyData.json', 'w') as f:
                    json.dump(self.frequencyJson, f)

                self.x_freq_input.setText('')
                self.y_freq_input.setText('')
            
            except ValueError:
                pass
        else: 
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Error")
            msg.setInformativeText('Too many items have been added to the frequency list.')
            msg.setWindowTitle("Error")
            msg.exec_()

class CalibrationScreen(QtWidgets.QMainWindow):
    def __init__(self):
        super(CalibrationScreen, self).__init__()
        self.chart = Canvas(self)
        self.chart.setFixedWidth(800)
        self.chart.setFixedHeight(400)
        self.initUI()

    def initUI(self): 
        self.label = QLabel("Is this position satisfactory?", self)
        self.label.move(30, 420)
        self.label.adjustSize()
        self.label.show()

        self.yesBtn = QPushButton("Yes", self)
        self.yesBtn.move(25, 450)
        self.yesBtn.adjustSize()
        self.yesBtn.show()

        self.noBtn = QPushButton("No", self)
        self.noBtn.move(90, 450)
        self.noBtn.adjustSize()
        self.noBtn.show()

        self.noBtn.clicked.connect(self.redo_position)
        self.yesBtn.clicked.connect(self.go_next_image)

    def redo_position(self):
        self.chart.hide() 
        chart = Canvas2(self)
        chart.setFixedWidth(800)
        chart.setFixedHeight(500)
        chart.show()

        self.nextBtn = QPushButton("Next", self)
        self.nextBtn.move(700, 550)
        self.nextBtn.adjustSize()
        self.nextBtn.show()

        self.nextBtn.clicked.connect(self.go_next_image)

    def go_next_image(self):
        global widget
        global currentCalibrationSpot
        currentCalibrationSpot += 1

        global calibrationPositionData
        with open('calibrationData.json', 'w') as f:
            json.dump(calibrationPositionData, f)

        if currentCalibrationSpot < NUM_SPOTS: 
            calibrationScreen = CalibrationScreen()
            widget.addWidget(calibrationScreen)
            widget.setCurrentIndex(widget.currentIndex() + 1)
        
        else: 
            print("Calibration is done!")

            with open("settings.json", "r") as jsonFile:
                data = json.load(jsonFile)

            data["calibrationComplete"] = True

            with open("settings.json", "w") as jsonFile:
                json.dump(data, jsonFile)

            currentCalibrationSpot = 0
            widget.setCurrentIndex(0)

            import GUI.calibratedGui as calibratedGui
            self.newWindow = calibratedGui.widget
            self.newWindow.show()
            widget.close()

  
class Canvas(FigureCanvas):
    def __init__(self, parent):
        fig, self.ax = plt.subplots(figsize=(5, 4), dpi=100)
        super().__init__(fig)
        self.setParent(parent)

        """ 
        Matplotlib Script
        """
        
        cameraAcquisition.main()
        im = np.array(Image.open('laserspots.jpg').convert('L'))
        point_x, point_y = centroid_com(im)
        plt.plot(point_x, point_y, marker="+", ms=8, mew=1, color="red")

        # UPDATE GLOBAL VARIABLES
        global calibrationPositionData
        global currentCalibrationSpot
    
        calibrationPositionData[currentCalibrationSpot] = (point_x, point_y)
        
class Canvas2(FigureCanvas):
    def __init__(self, parent):
        fig, self.ax = plt.subplots(figsize=(5, 4), dpi=100)
        super().__init__(fig)
        self.setParent(parent)

        """ 
        Matplotlib Script
        """
        im = np.array(Image.open('laserspots.jpg').convert('L'))

        def mouse_event(event):
            chart = Canvas2(self)
            chart.setFixedWidth(800)
            chart.setFixedHeight(500)
            chart.show()
            plt.plot(event.xdata, event.ydata, marker="+", ms=8, mew=1, color="red")
            fig.canvas.draw()
            
            # UPDATE GLOBAL VARIABLES
            global calibrationPositionData
            global currentCalibrationSpot
        
            calibrationPositionData[currentCalibrationSpot] = (event.xdata, event.ydata)

        cid = fig.canvas.mpl_connect('button_press_event', mouse_event)
        plt.imshow(im)


app = QApplication(sys.argv)
widget = QtWidgets.QStackedWidget()
mainWindow = MainWindow()
calibrationScreen = CalibrationScreen()
widget.addWidget(mainWindow)
widget.addWidget(calibrationScreen)
widget.setFixedHeight(600)
widget.setFixedWidth(800)
widget.show()

try:
   sys.exit(app.exec_())
except:
    print("Exiting")
