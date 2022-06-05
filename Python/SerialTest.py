import serial
import matplotlib.pyplot as plt
import numpy
import re

ser = serial.Serial()
ser.baudrate = 19200
ser.port = 'COM4'
ser.timeout = 1
ser.parity = serial.PARITY_NONE
ser.stopbits = 1

ser.open()



plt.ion()
class DynamicUpdate():

    def __init__(self):
        self.x_data = [0]
        self.y_data = [0]

    def on_launch(self):
        #Set up plot
        self.figure, self.ax = plt.subplots()
        self.lines, = self.ax.plot([],[],)
        #Autoscale on unknown axis and known lims on the other
        self.ax.set_autoscaley_on(True)
        # self.ax.set_xlim(self.min_x, self.max_x)
        #Other stuff
        self.ax.grid()
        ...

    def on_running(self, ydata):
        #Update data (with the new _and_ the old points)
        self.x_data
        self.y_data.append(ydata)
        self.x_data.append(self.x_data[-1]+1)
        self.lines.set_xdata(self.x_data)
        self.lines.set_ydata(self.y_data)
        #Need both of these in order to rescale
        self.ax.relim()
        self.ax.autoscale_view()
        #We need to draw *and* flush
        self.figure.canvas.draw()
        self.figure.canvas.flush_events()

    #Example
    def __call__(self):
        import numpy as np
        import time
        self.on_launch()
        xdata = []
        ydata = []
        for x in np.arange(0,10,0.5):
            xdata.append(x)
            ydata.append(np.exp(-x**2)+10*np.exp(-(x-7)**2))

            time.sleep(1)
        return xdata, ydata




def update_line(hl, new_data):
    hl.set_ydata(numpy.append(hl.get_ydata(), new_data))
    plt.draw()


d = DynamicUpdate()
d.on_launch()

while(1):
    # print("Reading")
    # print(list(map(hex,list()))
    # ser.write(b'\x01\x04\x00\x00\x00\x02\x71\xCB')
    # ser.readline()

    incomming = ser.readline()

    if b'Outcoming' in incomming:
        # print(incomming)
        data = incomming.decode('UTF-8').split(";")[:-1]
        # print(data)

        newData = [ float(re.search(r'\d+',entry).group()) for entry in data]
        print(newData)
        d.on_running(newData[2])
        # update_line(hl,data[0])
    # ser.write(b'Hi')


ser.close()



