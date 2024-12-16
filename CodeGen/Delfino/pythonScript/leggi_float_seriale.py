import serial
import struct

# Configura la porta seriale corretta
porta_seriale = "COM4"  # Cambia con la tua porta
baud_rate = 2000000  # Baud rate a 2 Mbps
SYNC_FLOAT = 123456.789  # Valore di sincronizzazione
BUFFER_SIZE = 70  # Numero di float previsti per ogni ciclo

try:
    # Apre la porta seriale
    ser = serial.Serial(porta_seriale, baud_rate, timeout=1)
    print(f"Connessione stabilita su {porta_seriale} a {baud_rate} baud.")

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
                    break  # Esce dal ciclo di attesa
            else:
                print("Timeout: Nessun dato ricevuto.")

        # **Una volta trovato il valore di sincronizzazione, leggi il ciclo di 70 float**
        float_count = 1  # Abbiamo trovato il primo float (valore di sincronizzazione)
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

                float_count += 1
            else:
                print("Timeout: Nessun dato ricevuto.")
                break  # Esci se un timeout durante il ciclo

        # Verifica che il ciclo sia stato completato
        if float_count == BUFFER_SIZE:
            print("Ciclo completo di 70 float ricevuto.")
        else:
            print("Errore: Ciclo incompleto di float.")

except serial.SerialException as e:
    print(f"Errore: {e}")
except KeyboardInterrupt:
    print("\nInterrotto dall'utente.")
finally:
    ser.close()
    print("Connessione seriale chiusa.")
