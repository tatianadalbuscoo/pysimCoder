#include "led.h"

void LED_Init(int pin)
{
    // Set up GPIO for the LED
    GPIO_SetupPinMux(pin, GPIO_MUX_CPU1, 0);
    GPIO_SetupPinOptions(pin, GPIO_OUTPUT, GPIO_PUSHPULL);
}

void LED_On(int pin)
{
    // Accendi il LED sul pin specificato
    if (pin < 32)
        GpioDataRegs.GPASET.all |= (1 << pin); // Per pin da 0 a 31
    else
        GpioDataRegs.GPBSET.all |= (1 << (pin - 32)); // Per pin da 32 a 63
}

void LED_Off(int pin)
{
    // Spegni il LED sul pin specificato
    if (pin < 32)
        GpioDataRegs.GPACLEAR.all |= (1 << pin); // Per pin da 0 a 31
    else
        GpioDataRegs.GPBCLEAR.all |= (1 << (pin - 32)); // Per pin da 32 a 63
}



