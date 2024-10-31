/*
COPYRIGHT (C) 2022  Roberto Bucher (roberto.bucher@supsi.ch)

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
#include "pyblock.h"


static void init(python_block* block)
{
    int pin = block->intPar[0];  // Number of pin
    LED_Init(pin);
}

static void inout(python_block* block)
{
    int pin = block->intPar[0];  // Number of pin
    double* u = block->u[0];     // u[0] first input of the block

    // Check input and set the Led state
    if (u[0] > 0.5) 
        LED_On(pin);    // Turn on Led
    else {
        LED_Off(pin);   // Turn off Led
    }
}

static void end(python_block* block)
{
    int pin = block->intPar[0];  // Number of pin
    LED_Off(pin);                // Turn off led
}

void outputGPIOblk(int flag, python_block* block)
{
    if (flag == CG_OUT) {  
        inout(block);
    }
    else if (flag == CG_END) {    
        end(block);
    }
    else if (flag == CG_INIT) {    
        init(block);
    }
}
