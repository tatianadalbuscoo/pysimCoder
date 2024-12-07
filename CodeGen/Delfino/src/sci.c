
#include "sci.h"


void loop()
{

    scia_send_message("ciao");
    //DELAY_US(100000); // Delay to avoid flooding the serial line
}

// SCIA initialization
void scia_init()
{
    configure_gpio42_43_for_scia();  // Configure GPIO42 and GPIO43 for SCIA
    scia_fifo_init();    // Initialize SCIA FIFO
    SciaRegs.SCICCR.all = 0x0007;   // 1 stop bit, no parity, 8-bit chars
    SciaRegs.SCICTL1.all = 0x0003;  // Enable TX, RX
    SciaRegs.SCICTL2.all = 0x0003;  // Enable interrupt for TX, RX
    SciaRegs.SCIHBAUD.all = 0x0A; // Set HBAUD
    SciaRegs.SCILBAUD.all = 0x2B; // Set LBAUD (for 9600 baud rate)
    SciaRegs.SCICTL1.all = 0x0023;  // Release SCIA from reset

    EALLOW;
    ClkCfgRegs.LOSPCP.bit.LSPCLKDIV = 0;
    EDIS;
}

// SCIA FIFO initialization
void scia_fifo_init()
{
    SciaRegs.SCIFFTX.all = 0xE040;  // Enable TX FIFO, clear TX FIFO
    SciaRegs.SCIFFRX.all = 0x2044;  // Enable RX FIFO, clear RX FIFO
    SciaRegs.SCIFFCT.all = 0x0;     // Clear FIFO counters
    SciaRegs.SCICTL1.all = 0x0023;  // Relinquish SCI from Reset
    SciaRegs.SCIFFTX.bit.TXFIFORESET = 1;
    SciaRegs.SCIFFRX.bit.RXFIFORESET = 1;
}

// Transmit a character
void scia_xmit(int a)
{
    while (SciaRegs.SCIFFTX.bit.TXFFST != 0) {} // Wait for space in TX FIFO
    SciaRegs.SCITXBUF.all = a;                   // Transmit character
}

// Transmit a message
void scia_send_message(const char* msg)
{
    int i = 0;
    while (msg[i] != '\0')
    {
        scia_xmit(msg[i]); // Transmit each character
        i++;
    }
}

// Configure GPIO42 and GPIO43
void configure_gpio42_43_for_scia(void)
{

    EALLOW;
    GpioCtrlRegs.GPBMUX1.bit.GPIO42 = 3;
    GpioCtrlRegs.GPBMUX1.bit.GPIO43 = 3;
    GpioCtrlRegs.GPBGMUX1.bit.GPIO42 = 3;
    GpioCtrlRegs.GPBGMUX1.bit.GPIO43 = 3;
    EDIS;

}
