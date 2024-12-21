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

#include "led.h"

// Initializes a specified GPIO pin for LED output with push-pull configuration
void LED_Init(int pin)
{
    // Set up GPIO for the LED
    GPIO_SetupPinMux(pin, GPIO_MUX_CPU1, 0);
    GPIO_SetupPinOptions(pin, GPIO_OUTPUT, GPIO_PUSHPULL);
}

/*
* Turns on the LED connected to the specified GPIO pin by clearing the corresponding bit.
* Example: If pin = 34, calculates (pin - 32) = 2, then (1 << 2) = 00000100 to clear the bit.
*/
void LED_On(int pin) 
{

    // Turn on the LED on the specified pin
    if (pin >= 0 && pin < 32) 
    {
        GpioDataRegs.GPACLEAR.all = (1 << pin); 
    }
    else if (pin >= 32 && pin < 64) 
    {
        GpioDataRegs.GPBCLEAR.all = (1 << (pin - 32)); 
    }
    else if (pin >= 64 && pin < 96) 
    {
        GpioDataRegs.GPCCLEAR.all = (1 << (pin - 64)); 
    }
    else if (pin >= 96 && pin < 128) 
    {
        GpioDataRegs.GPDCLEAR.all = (1 << (pin - 96)); 
    }
    else if (pin >= 128 && pin < 160) 
    {
        GpioDataRegs.GPECLEAR.all = (1 << (pin - 128)); 
    }
    else if (pin >= 160 && pin < 169) 
    {
        GpioDataRegs.GPFCLEAR.all = (1 << (pin - 160));
    }
}

/*
* Turns off the LED connected to the specified GPIO pin by setting the corresponding bit.
* Example: If pin = 34, calculates (pin - 32) = 2, then (1 << 2) = 00000100 to set the bit.
*/
void LED_Off(int pin) 
{

    // Turn off the LED on the specified pin
    if (pin >= 0 && pin < 32) 
    {
        GpioDataRegs.GPASET.all = (1 << pin);
    }
    else if (pin >= 32 && pin < 64) 
    {
        GpioDataRegs.GPBSET.all = (1 << (pin - 32));
    }
    else if (pin >= 64 && pin < 96) 
    {
        GpioDataRegs.GPCSET.all = (1 << (pin - 64));
    }
    else if (pin >= 96 && pin < 128) 
    {
        GpioDataRegs.GPDSET.all = (1 << (pin - 96));
    }
    else if (pin >= 128 && pin < 160) 
    {
        GpioDataRegs.GPESET.all = (1 << (pin - 128));
    }
    else if (pin >= 160 && pin < 169) 
    {
        GpioDataRegs.GPFSET.all = (1 << (pin - 160));
    }
}

