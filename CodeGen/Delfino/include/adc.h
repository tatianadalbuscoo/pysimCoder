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

void ADC_SetMode(Uint16 adc, Uint16 resolution, Uint16 signalMode, int channel, int soc);
void ADC_Init(const char* adc_module, int channel, int soc);
int ADC_ReadSOC(const char* adc_module, int soc);

#endif // ADC_H

