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


// esegue l'inizializzazione del GPIO in input e la lettura dello stato del GPIO (alto o basso).

#include <pyblock.h>
#include <F2837xD_device.h>   // Libreria specifica per Delfino
#include <F2837xD_gpio.h>     // Funzioni GPIO per Delfino



static void init(python_block* block)
{
    int* intPar = block->intPar;
    int gpioPin = intPar[1];  // Numero del GPIO passato come parametro


    GPIO_SetupPinMux(gpioPin, GPIO_MUX_CPU1, 0);
    GPIO_SetupPinOptions(gpioPin, GPIO_INPUT, GPIO_PULLUP);

    intPar[1] = gpioPin;  // Salva il numero di GPIO configurato
}

static void inout(python_block* block)
{
    double* realPar = block->realPar;
    int* intPar = block->intPar;
    double* y = block->y[0];  // Output del blocco (stato del GPIO)

    int gpioPin = intPar[1];  // Numero del GPIO

    // Leggi lo stato del GPIO usando il numero di pin passato come parametro
    if (gpioPin < 32 && GpioDataRegs.GPADAT.all & (1 << gpioPin)) {
        y[0] = 1.0;  // Imposta l'output a 1 se il GPIO è alto
    }
    else {
        y[0] = 0.0;  // Imposta l'output a 0 se il GPIO è basso
    }
}

static void end(python_block* block)
{

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
