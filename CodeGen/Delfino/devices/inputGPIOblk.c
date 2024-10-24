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

#include "button.h"  
#include "pyblock.h"

static void init(python_block* block)
{
    Button_Init();
}

static void inout(python_block* block)
{
    // y[0] è il primo output del blocco
    double* y = block->y[0];

    if (Button_IsPressed()) {
        y[0] = 1.0;  // Imposta l'output a 1 se il pulsante è premuto
    }
    else {
        y[0] = 0.0;  // Imposta l'output a 0 se il pulsante non è premuto
    }
}

static void end(python_block* block)
{
    // Nessuna azione necessaria alla fine
}

void inputGPIOblk(int flag, python_block* block)
{
    if (flag == CG_OUT) {  /* Legge l'input */
        inout(block);
    }
    else if (flag == CG_END) {  /* Terminazione */
        end(block);
    }
    else if (flag == CG_INIT) {  /* Inizializzazione */
        init(block);
    }
}
