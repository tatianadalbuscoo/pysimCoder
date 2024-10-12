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

    // Configura il GPIO come input
    EALLOW;
    GpioCtrlRegs.GPAMUX1.bit.GPIO6 = 0;  // Configura GPIO come GPIO generico
    GpioCtrlRegs.GPADIR.bit.GPIO6 = 0;    // Imposta come input
    EDIS;

    intPar[1] = gpioPin;  // Salva il numero di GPIO configurato
}

static void inout(python_block* block)
{
    double* realPar = block->realPar;
    int* intPar = block->intPar;
    double* y = block->y[0];  // Output del blocco (stato del GPIO)

    int gpioPin = intPar[1];  // Numero del GPIO

    // Leggi lo stato del GPIO
    if (GpioDataRegs.GPADAT.bit.GPIO6 == 1) {
        y[0] = 1.0;  // Imposta l'output a 1 se il GPIO è alto
    }
    else {
        y[0] = 0.0;  // Imposta l'output a 0 se il GPIO è basso
    }
}

static void end(python_block* block)
{
    int* intPar = block->intPar;
    int gpioPin = intPar[1];  // Numero del GPIO

    // Puoi fare una pulizia del blocco qui, se necessario
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
