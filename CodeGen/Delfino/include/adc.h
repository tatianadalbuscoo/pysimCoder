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

#ifndef ADC_H
#define ADC_H

#include "F28x_Project.h"

// ADC modules
#define ADC_ADCA 0
#define ADC_ADCB 1
#define ADC_ADCC 2
#define ADC_ADCD 3

// Resolution
#define ADC_RESOLUTION_12BIT 0
#define ADC_RESOLUTION_16BIT 1

// Signal mode
#define ADC_SIGNALMODE_SINGLE 0
#define ADC_SIGNALMODE_DIFFERENTIAL 1

// Function for main1 and main2
void ADC_Init(const char* adc_module, int channel, int soc);

// Function Prototypes for main3 and main4
void ADC_Init_main3_4(const char* adc_module, int channel, int soc, int generate_interrurpt);

// Function Prototypes for all main 1,2,3,4
int ADC_ReadSOC(const char* adc_module, int soc, int generateInterrupt);

#endif // ADC_H

