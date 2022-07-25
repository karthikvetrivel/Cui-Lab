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


# PIXEL POSIITON --> FREQUENCY


# STEP 1: Enter Initial Frequency, Identify Position
# - this is what helps determine what a_x is
 

# STEP 2: Hard-code a table of four pixel pair positions, use previous model to calculate frequencies (new a_x and previous slope)

# STEP 2: Shine lasers at the four frequencies
    # - Find the real pixel position pairs at each point 

# STEP 3: 
    # - Calculate new linear equation 


# We try to make this software as time efficient as possible. 


# Camera Integration;
# OpenCV w/ the Spinnaker SDK