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

#ifndef SCI_H_
#define SCI_H_

#include "F28x_Project.h"

// Function Prototypes
void configure_gpio42_43_for_scia(void);
void scia_fifo_init(void);
void interrupt_fifo_setup(void);
void init_buffer(void);
void add_signal_in_buffer(float value);
interrupt void sciaTxFifoIsr(void);


#endif /* SCI_H_ */
