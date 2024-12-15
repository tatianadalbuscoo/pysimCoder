
#include "sci.h"

#define FLOAT_BYTES 4     // Numero di byte per ogni float
#define FIFO_SIZE 4       // Numero massimo di float nella FIFO

volatile float tx_buffer[5] = { 1.1, 2.2, 3.3, 4.4, 5.5 }; // Buffer con un solo valore float
volatile int tx_index = 0;           // Indice del buffer di float
volatile Uint16 isr_counter = 0;     // Contatore per verificare quante volte viene invocato l'ISR
volatile Uint16 fifo_byte_counter = 0; // Contatore dei byte trasmessi per ciascun float

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

    SciaRegs.SCIHBAUD.all = 0x0A;    // Baud rate
    SciaRegs.SCILBAUD.all = 0x2B;

    SciaRegs.SCICCR.bit.LOOPBKENA = 0; // Disabilita loopback
    SciaRegs.SCIFFTX.bit.TXFFIL = 0;  // Interrupt quando la FIFO è vuota
    SciaRegs.SCIFFTX.bit.TXFFIENA = 1; // Abilita l'interrupt FIFO TX
    SciaRegs.SCIFFTX.bit.TXFIFORESET = 1; // Resetta e abilita la FIFO TX
    SciaRegs.SCIFFTX.bit.SCIFFENA = 1; // Abilita le funzionalità avanzate della FIFO
    SciaRegs.SCIFFTX.bit.SCIRST = 1; // Il modulo SCI è attivo


    //SciaRegs.SCIFFTX.all = 0xC022;     // Abilita FIFO TX
    // Configura la FIFO TX per chiamare l'interrupt quando è vuota
      // SciaRegs.SCIFFTX.bit.TXFFIL = 1;   // Soglia per l'interrupt: FIFO vuota
       //SciaRegs.SCIFFTX.bit.TXFFIENA = 1; // Abilita interrupt TX FIFO
       //SciaRegs.SCIFFTX.bit.TXFIFORESET = 1; // Reset della FIFO TX

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
    isr_counter++;  // Incrementa il contatore ISR

    // Trasmetti il float corrente
    int dati_da_inviare = sizeof(tx_buffer) / sizeof(tx_buffer[0]);
    if (tx_index < sizeof(tx_buffer) / sizeof(tx_buffer[0])) { // Controlla che ci siano dati da inviare
        int i;
        for (i = 0; i < 4; i++) {
            PutToFifo(tx_buffer[tx_index]);
            tx_index++;
        }

    }
    else {
        int u;
        u = 8;
        // Se tutti i dati sono stati inviati, resetta l'indice per una nuova trasmissione
        //tx_index = 0;
    }

    SciaRegs.SCIFFTX.bit.TXFFINTCLR = 1;  // Pulisci il flag TX
    PieCtrlRegs.PIEACK.all |= PIEACK_GROUP9;
}

