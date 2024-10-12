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

#include <pyblock.h>
#include <F2837xD_device.h>   // Libreria specifica per Delfino
#include <F2837xD_gpio.h>     // Funzioni GPIO per Delfino

static void init(python_block* block)
{
    int* intPar = block->intPar;
    int gpioPin = intPar[1];  // Numero del GPIO passato come parametro

    // Configura il GPIO come output
    EALLOW;
    GpioCtrlRegs.GPAMUX1.bit.GPIO031 = 0; 
    GpioCtrlRegs.GPADIR.bit.GPIO31 = 1;  // Imposta come output
    EDIS;

    intPar[1] = gpioPin;
}

static void inout(python_block* block)
{
    double* realPar = block->realPar;
    int* intPar = block->intPar;
    double* u = block->u[0];

    int gpioPin = intPar[1];  // Numero del GPIO

    // Controlla l'input e imposta lo stato del GPIO
    if (u[0] > realPar[0]) {
        GpioDataRegs.GPASET.bit.GPIO31 = 1;  
    }
    else {
        GpioDataRegs.GPACLEAR.bit.GPIO31 = 1;  
    }
}

static void end(python_block* block)
{
    int* intPar = block->intPar;
    int gpioPin = intPar[1];  // Numero del GPIO

    // Spegni il GPIO alla fine
    GpioDataRegs.GPACLEAR.bit.GPIO31 = 1;  // Sostituisci con il numero di GPIO
}

void outputGPIOblk(int flag, python_block* block)
{
    if (flag == CG_OUT) {          /* gestione input/output */
        inout(block);
    }
    else if (flag == CG_END) {     /* terminazione */
        end(block);
    }
    else if (flag == CG_INIT) {    /* inizializzazione */
        init(block);
    }
}
