/*
 * sci.h
 *
 *  Created on: 7 Dec 2024
 *      Author: lucia
 */

#ifndef SCI_H_
#define SCI_H_

#include "F28x_Project.h"


void scia_init(void);
void scia_fifo_init(void);
void scia_xmit(int a);
void scia_send_message(const char* msg);
void configure_gpio42_43_for_scia(void);
void loop();



#endif /* SCI_H_ */
