import serial
import struct
import pyqtgraph as pg
from pyqtgraph.Qt import QtWidgets, QtCore
import time
from serial.tools import list_ports

baud_rate = 2000000
SYNC_FLOAT = 123456.789  # Synchronization value
BUFFER_SIZE = 70  # Number of floats expected per cycle

def select_serial_port():

    """
    Prompt the user to select a serial port or automatically choose the first available.
    """

    ports = list_ports.comports()
    if not ports:
        raise serial.SerialException("No serial ports found.")
    
    print("Available ports:")
    for i, port in enumerate(ports):
        print(f" {i + 1}: {port.device}")

    try:
        choice = int(input(f"Select a port [1-{len(ports)}] (default: 1, The first available port): ").strip())
        if 1 <= choice <= len(ports):
            return ports[choice - 1].device
    except ValueError:
        pass

    # Default to the first port if no valid choice is made
    print(f"No valid input provided. Defaulting to port {ports[0].device}.")
    return ports[0].device

# Data lists
x_data = []  # List for time
y_data = []  # List for values

# Configure the PyQtGraph window
app = QtWidgets.QApplication([])
win = pg.GraphicsLayoutWidget(show=True, title="Real-Time Signal")
win.resize(800, 600)
win.setWindowTitle("Real-Time Signal")
plot = win.addPlot(title="Signal")
curve = plot.plot(pen='y')  # Yellow line
plot.setLabel('left', 'Signal Value')  # Y-axis label
plot.setLabel('bottom', 'Time', units='s')  # X-axis label with units

try:

    # Prompt the user or auto-detect the serial port
    serial_port = select_serial_port()
    print(f"Connecting to {serial_port}...")

    # Open the serial port
    ser = serial.Serial(serial_port, baud_rate, timeout=1)
    print(f"Connection established on {serial_port} at {baud_rate} baud.")

    start_time = time.time()  # Start recording time

    def update():
        global x_data, y_data

        # Wait for the synchronization value before each cycle
        print("Waiting for the synchronization float...")
        sync_found = False
        while not sync_found:
            raw_data = ser.read(4)
            if len(raw_data) == 4:
                value = struct.unpack('<f', raw_data)[0]
                # Print the received bytes and the converted value
                byte1, byte2, byte3, byte4 = raw_data
                print(f"Bytes received: {byte1:02X}, {byte2:02X}, {byte3:02X}, {byte4:02X}")
                print(f"Received value: {value}")
                if abs(value - SYNC_FLOAT) < 1e-3:  # Float comparison tolerance
                    print("Synchronization value received! Starting cycle...")
                    sync_found = True
            else:
                print("Timeout: No data received. Retrying...")

        # Receive the next BUFFER_SIZE - 1 floats
        for _ in range(BUFFER_SIZE - 1):
            raw_data = ser.read(4)
            if len(raw_data) == 4:
                value = struct.unpack('<f', raw_data)[0]

                # Print the received bytes and the converted value
                byte1, byte2, byte3, byte4 = raw_data
                print(f"Bytes received: {byte1:02X}, {byte2:02X}, {byte3:02X}, {byte4:02X}")
                print(f"Received float: {value}")

                # Record elapsed time
                elapsed_time = time.time() - start_time
                x_data.append(elapsed_time)
                y_data.append(value)

                # Keep only the last 500 points
                if len(x_data) > 500:
                    x_data = x_data[-500:]
                    y_data = y_data[-500:]
            else:
                print("Timeout: No data received. Cycle interrupted.")
                break

        # Update the plot
        curve.setData(x=x_data, y=y_data)

    timer = QtCore.QTimer()
    timer.timeout.connect(update)
    timer.start(1)  # Update every 1ms

    QtWidgets.QApplication.instance().exec()

except serial.SerialException as e:
    print(f"Error: {e}")
except KeyboardInterrupt:
    print("\nInterrupted by user.")
finally:
    ser.close()
    print("Serial connection closed.")
