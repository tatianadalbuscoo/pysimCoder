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
#include "pyblock.h"

static void init(python_block* block)
{

    // Number of pin
    int pin = block->intPar[0];
    Button_Init(pin);           
}


static void inout(python_block* block)
{
    // Number of pin
    int pin = block->intPar[0];

    // y[0] is first output of the block
    double* y = block->y[0];

    if (Button_IsPressed(pin)) 
    {
        // output = 1 if button is pressed
        y[0] = 1.0;
    }
    else 
    {
        // output = 0 if button is not pressed
        y[0] = 0.0;
    }
}

static void end(python_block* block)
{

}

void inputGPIOblk(int flag, python_block* block)
{
    if (flag == CG_OUT) 
    {  
        inout(block);
    }
    else if (flag == CG_END) 
    {  
        end(block);
    }
    else if (flag == CG_INIT) 
    {  
        init(block);
    }
}

