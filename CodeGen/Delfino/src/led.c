#include "led.h"

void LED_Init(void)
{
    // Set up GPIO for the LED
    GPIO_SetupPinMux(LED_GPIO_BLUE, GPIO_MUX_CPU1, 0);
    GPIO_SetupPinOptions(LED_GPIO_BLUE, GPIO_OUTPUT, GPIO_PUSHPULL);
}

void LED_On(void)
{
    GpioDataRegs.GPASET.bit.GPIO31 = 1;   // Turn on LED
}

void LED_Off(void)
{
    GpioDataRegs.GPACLEAR.bit.GPIO31 = 1; // Turn off LED
}


