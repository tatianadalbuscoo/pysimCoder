import serial
import struct

porta_seriale = "COM4"
baud_rate = 2000000  # Baud rate a 2 Mbps

try:
    # Apre la porta seriale
    ser = serial.Serial(porta_seriale, baud_rate, timeout=1)
    print(f"Connessione stabilita su {porta_seriale} a {baud_rate} baud.")

    while True:
        # Legge 4 byte (un float)
        raw_data = ser.read(4)
        if len(raw_data) == 4:
            # Debug: Mostra i byte ricevuti
            byte1, byte2, byte3, byte4 = raw_data
            print(f"Byte ricevuti: {byte1:02X}, {byte2:02X}, {byte3:02X}, {byte4:02X}")
            
            # Converte i byte in un valore float
            valore = struct.unpack('<f', raw_data)[0]
            print(f"Ricevuto float: {valore}")
        else:
            print("Timeout: Nessun dato ricevuto.")
except serial.SerialException as e:
    print(f"Errore: {e}")
except KeyboardInterrupt:
    print("\nInterrotto dall'utente.")
finally:
    ser.close()
    print("Connessione seriale chiusa.")
