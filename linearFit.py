import json
import numpy as np
import matplotlib.pyplot as plt 

frequencyData = json.load(open("frequencyData.json"))
positionData = json.load(open("calibrationData.json"))

x_input = []
x_output = []

y_input = []
y_output = []

for i in positionData.values(): 
    x_input.append(i[0])
    y_input.append(i[1])

for i in frequencyData.values():
    x_output.append(float(i[0]))
    y_output.append(float(i[1]))

m_x, b_x = np.polyfit(x_input, x_output, 1)
m_y, b_y = np.polyfit(y_input, y_output, 1)
