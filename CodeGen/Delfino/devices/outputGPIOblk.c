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

//#include <pyblock.h>
#include <F2837xD_device.h>   // Libreria specifica per Delfino
#include <F2837xD_gpio.h>     // Funzioni GPIO per Delfino

static void init(python_block* block)
{
    int* intPar = block->intPar;
    int gpioPin = intPar[1];  // Numero del GPIO passato come parametro

    GPIO_SetupPinMux(gpioPin, GPIO_MUX_CPU1, 0);
    GPIO_SetupPinOptions(gpioPin, GPIO_OUTPUT, GPIO_PUSHPULL);

    intPar[1] = gpioPin;
}

static void inout(python_block* block)
{
    double* realPar = block->realPar;
    int* intPar = block->intPar;
    double* u = block->u[0];

    int gpioPin = intPar[1];  // Numero del GPIO

    // Controlla l'input e imposta lo stato del GPIO passato come parametro
    if (u[0] > realPar[0]) {
        if (gpioPin < 32) {
            GpioDataRegs.GPASET.all |= (1 << gpioPin);  // Imposta il pin alto
        }
        else if (gpioPin < 64) {
            GpioDataRegs.GPBSET.all |= (1 << (gpioPin - 32));  // Imposta il pin alto per GPIOB
        }
    }
    else {
        if (gpioPin < 32) {
            GpioDataRegs.GPACLEAR.all |= (1 << gpioPin);  // Imposta il pin basso
        }
        else if (gpioPin < 64) {
            GpioDataRegs.GPBCLEAR.all |= (1 << (gpioPin - 32));  // Imposta il pin basso per GPIOB
        }
    }
}

static void end(python_block* block)
{
    int* intPar = block->intPar;
    int gpioPin = intPar[1];  // Numero del GPIO

    // Spegni il GPIO alla fine
    if (gpioPin < 32) {
        GpioDataRegs.GPACLEAR.all |= (1 << gpioPin);  // Imposta il pin basso
    }
    else if (gpioPin < 64) {
        GpioDataRegs.GPBCLEAR.all |= (1 << (gpioPin - 32));  // Imposta il pin basso per GPIOB
    }
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
