import serial
import struct
from serial.tools import list_ports

baud_rate = 2000000
SYNC_FLOAT = 123456.789  # Synchronization value
BUFFER_SIZE = 70  # Number of floats expected in each cycle

def find_serial_port():

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

try:

    # Prompt the user or auto-detect the serial port
    serial_port = find_serial_port()
    print(f"Connecting to {serial_port}...")

    # Open the serial port
    ser = serial.Serial(serial_port, baud_rate, timeout=1)
    print(f"Connection established on {serial_port} at {baud_rate} baud.")

    while True:

        # Wait for the synchronization float
        print("Waiting for the synchronization float...")
        while True:

            # Read 4 bytes (one float)
            raw_data = ser.read(4)
            if len(raw_data) == 4:

                # Convert the bytes into a float value
                value = struct.unpack('<f', raw_data)[0]

                # Check if the value matches the synchronization value
                if abs(value - SYNC_FLOAT) < 1e-3:  # Tolerance for float comparison
                    print("Synchronization float received! Starting cycle...")
                    break  # Exit the waiting loop
            else:
                print("Timeout: No data received.")

        # Once the synchronization float is found, read the cycle of 70 floats
        float_count = 1

        while float_count < BUFFER_SIZE:
            raw_data = ser.read(4)
            if len(raw_data) == 4:
                byte1, byte2, byte3, byte4 = raw_data
                print(f"Bytes received: {byte1:02X}, {byte2:02X}, {byte3:02X}, {byte4:02X}")

                # Convert the bytes into a float value
                value = struct.unpack('<f', raw_data)[0]
                print(f"Received float: {value}")

                float_count += 1
            else:
                print("Timeout: No data received.")
                break  # Exit if a timeout occurs during the cycle

        # Verify that the cycle was completed
        if float_count == BUFFER_SIZE:
            print("Complete cycle of 70 floats received.")
        else:
            print("Error: Incomplete cycle of floats.")

except serial.SerialException as e:
    print(f"Error: {e}")
except KeyboardInterrupt:
    print("\nInterrupted by user.")
finally:
    ser.close()
    print("Serial connection closed.")
