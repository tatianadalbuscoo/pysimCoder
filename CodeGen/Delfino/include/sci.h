/*
 * sci.h
 *
 *  Created on: 7 Dec 2024
 *      Author: lucia
 */

#ifndef SCI_H_
#define SCI_H_

#include "F28x_Project.h"


void scia_fifo_init(void);
void interrupt_fifo_setup(void);
void configure_gpio42_43_for_scia(void);
interrupt void sciaTxFifoIsr(void);
void PutToFifo(float floatToSend);
void add_signal_in_buffer(float value);



#endif /* SCI_H_ */
