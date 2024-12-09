#include "adc.h"
#include <string.h>

// Configure an ADC module with resolution, signal mode, channel, and specific SOC
void ADC_SetMode(Uint16 adc, Uint16 resolution, Uint16 signalMode, int channel, int soc)
{
    if (soc < 0 || soc > 15) return;

    if (adc == ADC_ADCA)
    {
        AdcaRegs.ADCCTL2.bit.PRESCALE = 6;  // Clock prescaler
        AdcaRegs.ADCCTL2.bit.RESOLUTION = (resolution == ADC_RESOLUTION_12BIT) ? 0 : 1;
        AdcaRegs.ADCCTL2.bit.SIGNALMODE = (signalMode == ADC_SIGNALMODE_SINGLE) ? 0 : 1;

        AdcaRegs.ADCCTL1.bit.INTPULSEPOS = 1; // Configure interrupt pulse position
        AdcaRegs.ADCCTL1.bit.ADCPWDNZ = 1;    // Power up ADC module

        (&AdcaRegs.ADCSOC0CTL)[soc].bit.CHSEL = channel;   // Select input channel
        (&AdcaRegs.ADCSOC0CTL)[soc].bit.ACQPS = 14;        // Set acquisition time
        (&AdcaRegs.ADCSOC0CTL)[soc].bit.TRIGSEL = 0;       // Software trigger

        AdcaRegs.ADCINTSEL1N2.bit.INT1SEL = soc;   // Set interrupt for SOC
        AdcaRegs.ADCINTSEL1N2.bit.INT1E = 1;       // Enable interrupt
    }
    else if (adc == ADC_ADCB)
    {
        AdcbRegs.ADCCTL2.bit.PRESCALE = 6;
        AdcbRegs.ADCCTL2.bit.RESOLUTION = (resolution == ADC_RESOLUTION_12BIT) ? 0 : 1;
        AdcbRegs.ADCCTL2.bit.SIGNALMODE = (signalMode == ADC_SIGNALMODE_SINGLE) ? 0 : 1;

        AdcbRegs.ADCCTL1.bit.INTPULSEPOS = 1;
        AdcbRegs.ADCCTL1.bit.ADCPWDNZ = 1;

        (&AdcbRegs.ADCSOC0CTL)[soc].bit.CHSEL = channel;
        (&AdcbRegs.ADCSOC0CTL)[soc].bit.ACQPS = 14;
        (&AdcbRegs.ADCSOC0CTL)[soc].bit.TRIGSEL = 0;

        AdcbRegs.ADCINTSEL1N2.bit.INT1SEL = soc;
        AdcbRegs.ADCINTSEL1N2.bit.INT1E = 1;
    }
    else if (adc == ADC_ADCC)
    {
        AdccRegs.ADCCTL2.bit.PRESCALE = 6;
        AdccRegs.ADCCTL2.bit.RESOLUTION = (resolution == ADC_RESOLUTION_12BIT) ? 0 : 1;
        AdccRegs.ADCCTL2.bit.SIGNALMODE = (signalMode == ADC_SIGNALMODE_SINGLE) ? 0 : 1;

        AdccRegs.ADCCTL1.bit.INTPULSEPOS = 1;
        AdccRegs.ADCCTL1.bit.ADCPWDNZ = 1;

        (&AdccRegs.ADCSOC0CTL)[soc].bit.CHSEL = channel;
        (&AdccRegs.ADCSOC0CTL)[soc].bit.ACQPS = 14;
        (&AdccRegs.ADCSOC0CTL)[soc].bit.TRIGSEL = 0;

        AdccRegs.ADCINTSEL1N2.bit.INT1SEL = soc;
        AdccRegs.ADCINTSEL1N2.bit.INT1E = 1;
    }
    else if (adc == ADC_ADCD)
    {
        AdcdRegs.ADCCTL2.bit.PRESCALE = 6;
        AdcdRegs.ADCCTL2.bit.RESOLUTION = (resolution == ADC_RESOLUTION_12BIT) ? 0 : 1;
        AdcdRegs.ADCCTL2.bit.SIGNALMODE = (signalMode == ADC_SIGNALMODE_SINGLE) ? 0 : 1;

        AdcdRegs.ADCCTL1.bit.INTPULSEPOS = 1;
        AdcdRegs.ADCCTL1.bit.ADCPWDNZ = 1;

        (&AdcdRegs.ADCSOC0CTL)[soc].bit.CHSEL = channel;
        (&AdcdRegs.ADCSOC0CTL)[soc].bit.ACQPS = 14;
        (&AdcdRegs.ADCSOC0CTL)[soc].bit.TRIGSEL = 0;

        AdcdRegs.ADCINTSEL1N2.bit.INT1SEL = soc;
        AdcdRegs.ADCINTSEL1N2.bit.INT1E = 1;
    }
}

// Initialize an ADC module
void ADC_Init(const char* adc_module, int channel, int soc)
{
    int adc_module_number;

    if (adc_module == NULL || soc < 0 || soc > 15) return;

    if (strcmp(adc_module, "A") == 0)
        adc_module_number = ADC_ADCA;
    else if (strcmp(adc_module, "B") == 0)
        adc_module_number = ADC_ADCB;
    else if (strcmp(adc_module, "C") == 0)
        adc_module_number = ADC_ADCC;
    else if (strcmp(adc_module, "D") == 0)
        adc_module_number = ADC_ADCD;
    else
        return;

    EALLOW;

    ADC_SetMode(adc_module_number, ADC_RESOLUTION_12BIT, ADC_SIGNALMODE_SINGLE, channel, soc);

    // Delay to allow ADC to power up
    DELAY_US(1000);

    EDIS;
}

// Read the result of a specific SOC
int ADC_ReadSOC(const char* adc_module, int soc)
{
    if (soc < 0 || soc > 15) return -1;

    if (strcmp(adc_module, "A") == 0)
    {
        AdcaRegs.ADCSOCFRC1.all = 1 << soc;       // Trigger SOC for ADC-A
        while (!AdcaRegs.ADCINTFLG.bit.ADCINT1);  // Wait for conversion to complete
        AdcaRegs.ADCINTFLGCLR.bit.ADCINT1 = 1;    // Clear the interrupt flag
        return (&AdcaResultRegs.ADCRESULT0)[soc]; // Return conversion result
    }
    else if (strcmp(adc_module, "B") == 0)
    {
        AdcbRegs.ADCSOCFRC1.all = 1 << soc;       // Trigger SOC for ADC-B
        while (!AdcbRegs.ADCINTFLG.bit.ADCINT1);
        AdcbRegs.ADCINTFLGCLR.bit.ADCINT1 = 1;
        return (&AdcbResultRegs.ADCRESULT0)[soc];
    }
    else if (strcmp(adc_module, "C") == 0)
    {
        AdccRegs.ADCSOCFRC1.all = 1 << soc;       // Trigger SOC for ADC-C
        while (!AdccRegs.ADCINTFLG.bit.ADCINT1);
        AdccRegs.ADCINTFLGCLR.bit.ADCINT1 = 1;
        return (&AdccResultRegs.ADCRESULT0)[soc];
    }
    else if (strcmp(adc_module, "D") == 0)
    {
        AdcdRegs.ADCSOCFRC1.all = 1 << soc;       // Trigger SOC for ADC-D
        while (!AdcdRegs.ADCINTFLG.bit.ADCINT1);
        AdcdRegs.ADCINTFLGCLR.bit.ADCINT1 = 1;
        return (&AdcdResultRegs.ADCRESULT0)[soc];
    }

    return -1;
}