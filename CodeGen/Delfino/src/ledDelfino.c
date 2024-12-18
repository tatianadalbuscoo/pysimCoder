#include "led.h"

void LED_Init(int pin)
{
    // Set up GPIO for the LED
    GPIO_SetupPinMux(pin, GPIO_MUX_CPU1, 0);
    GPIO_SetupPinOptions(pin, GPIO_OUTPUT, GPIO_PUSHPULL);
}

/*
* e.g.: if pin = 34
* pin - 32 = 2
* 1 << 2 = 00000100
*/
void LED_On(int pin) {

    // Turn on the LED on the specified pin
    if (pin >= 0 && pin < 32) {
        GpioDataRegs.GPACLEAR.all = (1 << pin); 
    }
    else if (pin >= 32 && pin < 64) {
        GpioDataRegs.GPBCLEAR.all = (1 << (pin - 32)); 
    }
    else if (pin >= 64 && pin < 96) {
        GpioDataRegs.GPCCLEAR.all = (1 << (pin - 64)); 
    }
    else if (pin >= 96 && pin < 128) {
        GpioDataRegs.GPDCLEAR.all = (1 << (pin - 96)); 
    }
    else if (pin >= 128 && pin < 160) {
        GpioDataRegs.GPECLEAR.all = (1 << (pin - 128)); 
    }
    else if (pin >= 160 && pin < 169) {
        GpioDataRegs.GPFCLEAR.all = (1 << (pin - 160));
    }
}

/*
* eg: if pin = 34
* pin - 32 = 2
* 1 << 2 = 00000100
*/
void LED_Off(int pin) {

    // Turn off the LED on the specified pin
    if (pin >= 0 && pin < 32) {
        GpioDataRegs.GPASET.all = (1 << pin);
    }
    else if (pin >= 32 && pin < 64) {
        GpioDataRegs.GPBSET.all = (1 << (pin - 32));
    }
    else if (pin >= 64 && pin < 96) {
        GpioDataRegs.GPCSET.all = (1 << (pin - 64));
    }
    else if (pin >= 96 && pin < 128) {
        GpioDataRegs.GPDSET.all = (1 << (pin - 96));
    }
    else if (pin >= 128 && pin < 160) {
        GpioDataRegs.GPESET.all = (1 << (pin - 128));
    }
    else if (pin >= 160 && pin < 169) {
        GpioDataRegs.GPFSET.all = (1 << (pin - 160));
    }
}






