import serial
import struct
import pyqtgraph as pg
from pyqtgraph.Qt import QtWidgets, QtCore
import time

porta_seriale = "COM4"
baud_rate = 2000000
SYNC_FLOAT = 123456.789  # Valore di sincronizzazione
BUFFER_SIZE = 70  # Numero di float previsti per ogni ciclo

# Liste per i dati
x_data = []  # Lista per i tempi
y_data = []  # Lista per i valori

# Configura la finestra PyQtGraph
app = QtWidgets.QApplication([])
win = pg.GraphicsLayoutWidget(show=True, title="Segnale in tempo reale")
win.resize(800, 600)
win.setWindowTitle("Segnale in tempo reale")
plot = win.addPlot(title="Segnale")
curve = plot.plot(pen='y')  # Linea gialla
plot.setLabel('left', 'Valore del segnale')  # Etichetta asse Y
plot.setLabel('bottom', 'Tempo', units='s')  # Etichetta asse X con unita

try:
    # Apre la porta seriale
    ser = serial.Serial(porta_seriale, baud_rate, timeout=1)
    print(f"Connessione stabilita su {porta_seriale} a {baud_rate} baud.")

    start_time = time.time()  # Inizio della registrazione dei tempi

    def update():
        global x_data, y_data

        # Aspetta il valore di sincronizzazione prima di ogni ciclo
        print("In attesa del float di sincronizzazione...")
        sync_found = False
        while not sync_found:
            raw_data = ser.read(4)
            if len(raw_data) == 4:
                valore = struct.unpack('<f', raw_data)[0]
                # Stampa i byte ricevuti e il valore convertito
                byte1, byte2, byte3, byte4 = raw_data
                print(f"Byte ricevuti: {byte1:02X}, {byte2:02X}, {byte3:02X}, {byte4:02X}")
                print(f"Ricevuto valore: {valore}")
                if abs(valore - SYNC_FLOAT) < 1e-3:  # Tolleranza per confronto float
                    print("Ricevuto valore di sincronizzazione! Inizio ciclo...")
                    sync_found = True
            else:
                print("Timeout: Nessun dato ricevuto. Riprovando...")

        # Riceve i successivi BUFFER_SIZE - 1 float
        for _ in range(BUFFER_SIZE - 1):
            raw_data = ser.read(4)
            if len(raw_data) == 4:
                valore = struct.unpack('<f', raw_data)[0]
                # Stampa i byte ricevuti e il valore convertito
                byte1, byte2, byte3, byte4 = raw_data
                print(f"Byte ricevuti: {byte1:02X}, {byte2:02X}, {byte3:02X}, {byte4:02X}")
                print(f"Ricevuto float: {valore}")

                # Registra il tempo trascorso
                elapsed_time = time.time() - start_time
                x_data.append(elapsed_time)
                y_data.append(valore)

                # Mostra solo gli ultimi 500 punti
                if len(x_data) > 500:
                    x_data = x_data[-500:]
                    y_data = y_data[-500:]
            else:
                print("Timeout: Nessun dato ricevuto. Interruzione del ciclo.")
                break

        # Aggiorna il grafico
        curve.setData(x=x_data, y=y_data)

    timer = QtCore.QTimer()
    timer.timeout.connect(update)
    timer.start(100)  # Aggiorna ogni 100ms

    QtWidgets.QApplication.instance().exec()

except serial.SerialException as e:
    print(f"Errore: {e}")
except KeyboardInterrupt:
    print("\nInterrotto dall'utente.")
finally:
    ser.close()
    print("Connessione seriale chiusa.")
