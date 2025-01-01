/*
COPYRIGHT (C) 2022  Roberto Bucher (roberto.bucher@supsi.ch)
MODIFIED BY Tatiana Dal Busco

This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 2 of the License, or (at your option) any later version.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this library; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA.
*/

#include "sci.h"

#define FLOAT_BYTES 4     // Number of bytes for each float
#define FIFO_SIZE 4       // Maximum number of floats in FIFO
#define DATA_BUFFER 70    // Maximum number of floats in buffer
#define SYNC_FLOAT 123456.789f  // Float value for synchronization

// Function Prototypes
void PutToFifo(float floatToSend);


// Buffer
volatile float tx_buffer[DATA_BUFFER] = {};

// Index of the float buffer used for sending
volatile int tx_index = 0;

// Where the next data should be inserted in the buffer
volatile int index_data_buffer = 0;

// Number of floats in the buffer to be sent to the TX FIFO.
volatile int number_float_buffer = 0;

/*
* Adds a float value to the TX buffer, restarting from position 1 if full
* (preserves the first float for synchronization), and enables SCIA TX interrupt.
*/
void add_signal_in_buffer(float value)
{
    //  If the buffer is full, start writing again from position 1 (does not overwrite the first float for synchronization)
    if (index_data_buffer >= DATA_BUFFER) 
    {
        // Start writing again after the synchronization float.
        index_data_buffer = 1;
    }

    // Add the signal to the buffer at the next available position.
    tx_buffer[index_data_buffer] = value;

    number_float_buffer++;
    index_data_buffer++;

    // Enable the SCIA TX interrupt
    PieCtrlRegs.PIEIER9.bit.INTx2 = 1;
}


// Initializes the buffer with a synchronization float and resets indices and counters.
void init_buffer(void)
{
    tx_buffer[0] = SYNC_FLOAT;

    // Sending starts from the synchronization value
    tx_index = 0;

    // Writing to the buffer begins after the sync value
    index_data_buffer = 1;
    
    // No real data in buffer yet
    number_float_buffer = 0;
}


// Configura GPIO42 e GPIO43 per SCIA
void configure_gpio42_43_for_scia(void)
{
    EALLOW;
    GpioCtrlRegs.GPBMUX1.bit.GPIO42 = 3;  // Configure GPIO42 for SCITXD
    GpioCtrlRegs.GPBMUX1.bit.GPIO43 = 3;  // Configure GPIO43 for SCIRXD
    GpioCtrlRegs.GPBGMUX1.bit.GPIO42 = 3; // Configure GPIO42 for SCITXD (high priority)
    GpioCtrlRegs.GPBGMUX1.bit.GPIO43 = 3; // Configure GPIO43 for SCIRXD (high priority)
    EDIS;
}


// Configuring the SCIA FIFO
void scia_fifo_init(void)
{
    SciaRegs.SCICCR.all = 0x0007;           // 1 stop bit, no parity, 8 char bits
    SciaRegs.SCICTL1.all = 0x0003;
    SciaRegs.SCICTL2.bit.TXINTENA = 1;      // Enable TX interrupt

    // Baud rate
    SciaRegs.SCIHBAUD.all = 0x00;
    SciaRegs.SCILBAUD.all = 0x0B;

    SciaRegs.SCICCR.bit.LOOPBKENA = 0;      // Disable loopback
    SciaRegs.SCIFFTX.bit.TXFFIL = 0;        // Interrupt when FIFO is empty
    SciaRegs.SCIFFTX.bit.TXFFIENA = 1;      // Enable FIFO TX interrupt
    SciaRegs.SCIFFTX.bit.TXFIFORESET = 1;   // Reset and enable FIFO TX
    SciaRegs.SCIFFTX.bit.SCIFFENA = 1;      // Enable advanced FIFO features
    SciaRegs.SCIFFTX.bit.SCIRST = 1;        // The SCI module is active

    SciaRegs.SCIFFCT.all = 0x0;

    SciaRegs.SCICTL1.all = 0x0023;
    SciaRegs.SCIFFRX.bit.RXFIFORESET = 1;

    EALLOW;
    ClkCfgRegs.LOSPCP.bit.LSPCLKDIV = 0;
    EDIS;
}

// Configure the interrupt for SCIA
void interrupt_fifo_setup(void)
{
    EALLOW;

    // Enable TX interrupt in PIE group
    PieCtrlRegs.PIEIER9.bit.INTx2 = 1;
    EDIS;
}


// Adds a float to the SCI TX FIFO by splitting it into bytes (little-endian)
void PutToFifo(float floatToSend)
{
    union {
        float f;

        // On this processor, unsigned char has 16 bits.
        unsigned char c[2];
    } Tdata;

    Tdata.f = floatToSend;

    // Access 16-bit blocks
    uint16_t block1 = Tdata.c[0];
    uint16_t block2 = Tdata.c[1];

    // Send 16-bit blocks by splitting them into bytes (for little-endian format).
    SciaRegs.SCITXBUF.all = block1 & 0xFF;        // Least significant byte of the first block
    SciaRegs.SCITXBUF.all = (block1 >> 8) & 0xFF; // Most significant byte of the first block
    SciaRegs.SCITXBUF.all = block2 & 0xFF;        // Least significant byte of the second block
    SciaRegs.SCITXBUF.all = (block2 >> 8) & 0xFF; // Most significant byte of the second block
}

// Interrupt called when the TX FIFO is empty
interrupt void sciaTxFifoIsr(void)
{
    DINT;

    int i;
    for (i = 0; i < 4; i++) 
    {

        // If there is no more data to send
        if (number_float_buffer <= 0 && tx_index > 0) 
        {
            // Disable SCIA TX interrupt
            PieCtrlRegs.PIEIER9.bit.INTx2 = 0;
            break;
        }
        if (tx_index >= DATA_BUFFER) 
        {
            tx_index = 0;
        }

        // Add float from buffer to fifo
        PutToFifo(tx_buffer[tx_index]);

        // Update indexes only if we are not sending the sync value
        if (tx_index != 0) 
        {
            number_float_buffer--;
        }
        tx_index++;
    }

    // Clear the TX flag
    SciaRegs.SCIFFTX.bit.TXFFINTCLR = 1;
    PieCtrlRegs.PIEACK.all |= PIEACK_GROUP9;

    EINT;
}


