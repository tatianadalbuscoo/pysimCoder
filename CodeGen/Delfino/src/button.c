#include "button.h"

void Button_Init(int pin)
{
    // Set up GPIO for the button
    GPIO_SetupPinMux(pin, GPIO_MUX_CPU1, 0);
    GPIO_SetupPinOptions(pin, GPIO_INPUT, GPIO_PULLUP);
}

Uint16 Button_IsPressed(int pin) {
    if (pin >= 0 && pin <= 31) {
        // GPIO 0-31 -> GPADAT
        return (GpioDataRegs.GPADAT.all & (1 << pin)) == 0;
    }
    else if (pin >= 32 && pin <= 63) {
        // GPIO 32-63 -> GPBDAT
        return (GpioDataRegs.GPBDAT.all & (1 << (pin - 32))) == 0;
    }
    else if (pin >= 64 && pin <= 95) {
        // GPIO 64-95 -> GPCDAT
        return (GpioDataRegs.GPCDAT.all & (1 << (pin - 64))) == 0;
    }
    else if (pin >= 96 && pin <= 127) {
        // GPIO 96-127 -> GPDDAT
        return (GpioDataRegs.GPDDAT.all & (1 << (pin - 96))) == 0;
    }
    else if (pin >= 128 && pin <= 159) {
        // GPIO 128-159 -> GPEDAT
        return (GpioDataRegs.GPEDAT.all & (1 << (pin - 128))) == 0;
    }
    else if (pin >= 160 && pin <= 168) {
        // GPIO 160-168 -> GPFDAT
        return (GpioDataRegs.GPFDAT.all & (1 << (pin - 160))) == 0;
    }
    else {
        // Invalid pin, return 0 or an error code as needed
        return 0;
    }
}

