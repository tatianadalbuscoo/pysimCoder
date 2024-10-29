#include "button.h"

void Button_Init(int pin)
{
    // Set up GPIO for the button
    GPIO_SetupPinMux(pin, GPIO_MUX_CPU1, 0);
    GPIO_SetupPinOptions(pin, GPIO_INPUT, GPIO_PULLUP);
}

Uint16 Button_IsPressed(int pin)
{
    // Controlla se il bottone è premuto sul pin specificato
    return (GpioDataRegs.GPADAT.all & (1 << pin)) != 0;
}

