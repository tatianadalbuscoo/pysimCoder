
#include "sci.h"

#define FLOAT_BYTES 4     // Numero di byte per ogni float
#define FIFO_SIZE 4       // Numero massimo di float nella FIFO
#define DATA_BUFFER 70

volatile float tx_buffer[DATA_BUFFER] = {}; // Buffer con un solo valore float
volatile int tx_index = 0;           // Indice del buffer di float quello per inviare
volatile int index_data_buffer = 0;  // Dove va inserito il prossimo dato quello per il buffer
volatile int number_float_buffer = 0; //Numero di float nel buffer da inviare alla fifo tx

void add_signal_in_buffer(float value)
{
    // Se il buffer è pieno, ricomincia a scrivere dalla posizione 0
    if (index_data_buffer >= sizeof(tx_buffer) / sizeof(tx_buffer[0])) {
        index_data_buffer = 0; // Resetta l'indice per sovrascrivere
    }

    // Aggiungi il segnale al buffer nella posizione successiva disponibile
    tx_buffer[index_data_buffer] = value;

    // Incrementa il contatore del numero di float nel buffer
    number_float_buffer++;

    index_data_buffer++;
}


// Configura GPIO42 e GPIO43 per SCIA
void configure_gpio42_43_for_scia(void)
{
    EALLOW;
    GpioCtrlRegs.GPBMUX1.bit.GPIO42 = 3;  // Configura GPIO42 per SCITXD
    GpioCtrlRegs.GPBMUX1.bit.GPIO43 = 3;  // Configura GPIO43 per SCIRXD
    GpioCtrlRegs.GPBGMUX1.bit.GPIO42 = 3; // Configura GPIO42 per SCITXD (alta priorità)
    GpioCtrlRegs.GPBGMUX1.bit.GPIO43 = 3; // Configura GPIO43 per SCIRXD (alta priorità)
    EDIS;
}

// Configurazione della FIFO SCIA
void scia_fifo_init(void)
{
    SciaRegs.SCICCR.all = 0x0007;      // 1 stop bit, no parity, 8 char bits
    SciaRegs.SCICTL1.all = 0x0003;     // Abilita TX, RX
    SciaRegs.SCICTL2.bit.TXINTENA = 1; // Abilita interrupt TX

    SciaRegs.SCIHBAUD.all = 0x00;    // Baud rate
    SciaRegs.SCILBAUD.all = 0x0B;

    SciaRegs.SCICCR.bit.LOOPBKENA = 0; // Disabilita loopback
    SciaRegs.SCIFFTX.bit.TXFFIL = 0;  // Interrupt quando la FIFO è vuota
    SciaRegs.SCIFFTX.bit.TXFFIENA = 1; // Abilita l'interrupt FIFO TX
    SciaRegs.SCIFFTX.bit.TXFIFORESET = 1; // Resetta e abilita la FIFO TX
    SciaRegs.SCIFFTX.bit.SCIFFENA = 1; // Abilita le funzionalità avanzate della FIFO
    SciaRegs.SCIFFTX.bit.SCIRST = 1; // Il modulo SCI è attivo


    SciaRegs.SCIFFCT.all = 0x0;

    SciaRegs.SCICTL1.all = 0x0023;     // Rilascia SCIA da reset
    SciaRegs.SCIFFRX.bit.RXFIFORESET = 1;

    EALLOW;
    ClkCfgRegs.LOSPCP.bit.LSPCLKDIV = 0;
    EDIS;
}

// Configura gli interrupt per SCIA
void interrupt_fifo_setup(void)
{
    EALLOW;
    PieCtrlRegs.PIEIER9.bit.INTx2 = 1;  // Abilita TX interrupt nel gruppo PIE
    EDIS;
}

void PutToFifo(float floatToSend)
{
    union {
        float f;

        // unseïgned char in questo processore ha 16 bit
        unsigned char c[2];
    } Tdata;

    Tdata.f = floatToSend;

    // Accedi ai blocchi da 16 bit
    uint16_t block1 = Tdata.c[0];
    uint16_t block2 = Tdata.c[1];

    // Invia i blocchi da 16 bit separandoli in byte (per il little endian)

    SciaRegs.SCITXBUF.all = block1 & 0xFF;        // Byte meno significativo del primo blocco
    SciaRegs.SCITXBUF.all = (block1 >> 8) & 0xFF; // Byte più significativo del primo blocco
    SciaRegs.SCITXBUF.all = block2 & 0xFF;        // Byte meno significativo del secondo blocco
    SciaRegs.SCITXBUF.all = (block2 >> 8) & 0xFF; // Byte più significativo del secondo blocco
}

// ISR per la trasmissione
interrupt void sciaTxFifoIsr(void)
{
    int i;
    for (i = 0; i < 4; i++) {

        if (number_float_buffer <= 0) {
            break;
        }
        if (tx_index >= DATA_BUFFER) {
            tx_index = 0;
        }
        PutToFifo(tx_buffer[tx_index]);
        tx_index++;
        number_float_buffer--;
    }

    SciaRegs.SCIFFTX.bit.TXFFINTCLR = 1;  // Pulisci il flag TX
    PieCtrlRegs.PIEACK.all |= PIEACK_GROUP9;
}

