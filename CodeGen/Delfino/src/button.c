#include "button.h"

void Button_Init(int pin)
{
    // Set up GPIO for the button
    GPIO_SetupPinMux(pin, GPIO_MUX_CPU1, 0);
    GPIO_SetupPinOptions(pin, GPIO_INPUT, GPIO_PULLUP);
}

/*
* e.g.: if pin = 34
* pin - 32 = 2
* 1 << 2 = 00000100
*/
Uint16 Button_IsPressed(int pin) {

    // GPIO 0-31 -> GPADAT
    if (pin >= 0 && pin <= 31) {
        return (GpioDataRegs.GPADAT.all & (1 << pin)) == 0;
    }
    // GPIO 32-63 -> GPBDAT
    else if (pin >= 32 && pin <= 63) {
        return (GpioDataRegs.GPBDAT.all & (1 << (pin - 32))) == 0;
    }
    // GPIO 64-95 -> GPCDAT
    else if (pin >= 64 && pin <= 95) {
        return (GpioDataRegs.GPCDAT.all & (1 << (pin - 64))) == 0;
    }
    // GPIO 96-127 -> GPDDAT
    else if (pin >= 96 && pin <= 127) {
        return (GpioDataRegs.GPDDAT.all & (1 << (pin - 96))) == 0;
    }
    // GPIO 128-159 -> GPEDAT
    else if (pin >= 128 && pin <= 159) {
        return (GpioDataRegs.GPEDAT.all & (1 << (pin - 128))) == 0;
    }
    // GPIO 160-168 -> GPFDAT
    else if (pin >= 160 && pin <= 168) {
        return (GpioDataRegs.GPFDAT.all & (1 << (pin - 160))) == 0;
    }
    // Invalid pin
    else {
        return 0;
    }
}

