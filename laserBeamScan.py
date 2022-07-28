import json
import sys
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QDialog, QMessageBox, QPushButton
from pip import main

with open("settings.json", "r") as jsonFile:
    data = json.load(jsonFile)

data["calibrationComplete"] = False

with open("settings.json", "w") as jsonFile:
    json.dump(data, jsonFile)

import GUI.mainCalibrationGui
