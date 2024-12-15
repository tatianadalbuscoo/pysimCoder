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

#include "sci.h"
#include "pyblock.h"

static void init(python_block* block)
{

    configure_gpio42_43_for_scia();

    // Mappa gli interrupt SCIA nella tabella PIE
    EALLOW;
    PieVectTable.SCIA_TX_INT = &sciaTxFifoIsr;
    EDIS;

    scia_fifo_init();  // Inizializza la FIFO di SCIA
    interrupt_fifo_setup();  // Configura gli interrupt e invia i dati iniziali

    PieCtrlRegs.PIECTRL.bit.ENPIE = 1;
    IER |= M_INT9;
    //EINT;

}


static void inout(python_block* block)
{
    double* u = block->u[0];
    float signal = u[0];

    add_signal_in_buffer(signal);

}


static void end(python_block* block)
{

}

void delfinoPlotblk(int flag, python_block* block)
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
