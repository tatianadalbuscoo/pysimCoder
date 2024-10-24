#include "button.h"

void Button_Init(void)
{
    // Set up GPIO for the button
    GPIO_SetupPinMux(BUTTON_GPIO_PIN, GPIO_MUX_CPU1, 0);
    GPIO_SetupPinOptions(BUTTON_GPIO_PIN, GPIO_INPUT, GPIO_PULLUP);
}

Uint16 Button_IsPressed(void)
{
    // Check if button is pressed (returns 1 if pressed, 0 if not)
    return GpioDataRegs.GPADAT.bit.GPIO6 != 0;
}
