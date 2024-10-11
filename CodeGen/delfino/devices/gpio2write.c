#include "F28x_Project.h"

// Funzione di inizializzazione del GPIO
void init_GPIO(uint16_t pin) {
    EALLOW;
    GPIO_SetupPinMux(pin, GPIO_MUX_CPU1, 0);
    GPIO_SetupPinOptions(pin, GPIO_OUTPUT, GPIO_PUSHPULL);
    EDIS;
}

// Funzione per controllare il GPIO
void GPIO_Write(uint16_t pin, uint16_t state) {
    if (state == 1) {
        GpioDataRegs.GPASET.bit.GPIO31 = 1; // Accende il LED
    }
    else {
        GpioDataRegs.GPACLEAR.bit.GPIO31 = 1; // Spegne il LED
    }
}
