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

#include "button.h"

// Initializes a specified GPIO pin for button input with pull-up resistor
void Button_Init(int pin)
{
    // Set up GPIO for the button
    GPIO_SetupPinMux(pin, GPIO_MUX_CPU1, 0);
    GPIO_SetupPinOptions(pin, GPIO_INPUT, GPIO_PULLUP);
}

/*
* Checks if a button connected to the specified GPIO pin is pressed.
* Returns 1 if the button is pressed, 0 otherwise.
* Example: If pin = 34, calculates (pin - 32) = 2, then (1 << 2) = 00000100.
*/
Uint16 Button_IsPressed(int pin) 
{

    // GPIO 0-31 -> GPADAT
    if (pin >= 0 && pin <= 31) 
    {
        return (GpioDataRegs.GPADAT.all & (1 << pin)) == 0;
    }

    // GPIO 32-63 -> GPBDAT
    else if (pin >= 32 && pin <= 63) 
    {
        return (GpioDataRegs.GPBDAT.all & (1 << (pin - 32))) == 0;
    }

    // GPIO 64-95 -> GPCDAT
    else if (pin >= 64 && pin <= 95) 
    {
        return (GpioDataRegs.GPCDAT.all & (1 << (pin - 64))) == 0;
    }

    // GPIO 96-127 -> GPDDAT
    else if (pin >= 96 && pin <= 127) 
    {
        return (GpioDataRegs.GPDDAT.all & (1 << (pin - 96))) == 0;
    }

    // GPIO 128-159 -> GPEDAT
    else if (pin >= 128 && pin <= 159) 
    {
        return (GpioDataRegs.GPEDAT.all & (1 << (pin - 128))) == 0;
    }

    // GPIO 160-168 -> GPFDAT
    else if (pin >= 160 && pin <= 168) 
    {
        return (GpioDataRegs.GPFDAT.all & (1 << (pin - 160))) == 0;
    }

    // Invalid pin
    else 
    {
        return 0;
    }
}

