import serial
import struct
import matplotlib.pyplot as plt
import time


porta_seriale = "COM4"
baud_rate = 2000000
SYNC_FLOAT = 123456.789  # Valore di sincronizzazione
BUFFER_SIZE = 70  # Numero di float previsti per ogni ciclo

# Liste per il grafico
x_data = []  # Lista per i tempi
y_data = []  # Lista per i valori

try:
    # Apre la porta seriale
    ser = serial.Serial(porta_seriale, baud_rate, timeout=1)
    print(f"Connessione stabilita su {porta_seriale} a {baud_rate} baud.")

    start_time = time.time()  # Inizio della registrazione dei tempi

    while True:
        # **Aspetta il valore di sincronizzazione**
        print("In attesa del float di sincronizzazione...")
        while True:
            # Legge 4 byte (un float)
            raw_data = ser.read(4)
            if len(raw_data) == 4:
                # Converte i byte in un valore float
                valore = struct.unpack('<f', raw_data)[0]

                # Controlla se il valore e il valore di sincronizzazione
                if abs(valore - SYNC_FLOAT) < 1e-3:  # Tolleranza per confronto float
                    print("Ricevuto valore di sincronizzazione! Inizio ciclo...")
                    break
            else:
                print("Timeout: Nessun dato ricevuto.")

        # **Una volta trovato il valore di sincronizzazione, leggi il ciclo di 70 float**
        float_count = 1
        sync_found = True

        while float_count < BUFFER_SIZE:
            raw_data = ser.read(4)
            if len(raw_data) == 4:
                # Debug: Mostra i byte ricevuti
                byte1, byte2, byte3, byte4 = raw_data
                print(f"Byte ricevuti: {byte1:02X}, {byte2:02X}, {byte3:02X}, {byte4:02X}")

                # Converte i byte in un valore float
                valore = struct.unpack('<f', raw_data)[0]
                print(f"Ricevuto float: {valore}")

                # Aggiungi il dato al grafico
                elapsed_time = time.time() - start_time
                x_data.append(elapsed_time)  # Tempo trascorso
                y_data.append(valore)       # Valore ricevuto

                float_count += 1
            else:
                print("Timeout: Nessun dato ricevuto.")
                break  # Esci se un timeout durante il ciclo

        # Verifica che il ciclo sia stato completato
        if float_count == BUFFER_SIZE:
            print("Ciclo completo di 70 float ricevuto.")
        else:
            print("Errore: Ciclo incompleto di float.")

        # Aggiorna il grafico
        plt.clf()  # Pulisce il grafico precedente
        plt.plot(x_data, y_data, label="Segnale ricevuto")
        plt.xlabel("Tempo (s)")
        plt.ylabel("Valore del segnale")
        plt.title("Segnale in tempo reale")
        plt.legend()
        plt.pause(0.01)  # Aggiorna il grafico
except serial.SerialException as e:
    print(f"Errore: {e}")
except KeyboardInterrupt:
    print("\nInterrotto dall'utente.")
finally:
    ser.close()
    print("Connessione seriale chiusa.")
    plt.show()  # Mostra il grafico finale quando il programma termina