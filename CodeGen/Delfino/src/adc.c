#include "adc.h"
#include <string.h>

// Configure an ADC module with resolution, signal mode, channel, and specific SOC
#include "adc.h"
#include <string.h>

// Configure an ADC module with resolution, signal mode, channel, and specific SOC
void ADC_SetMode(Uint16 adc, Uint16 resolution, Uint16 signalMode, int channel, int soc)
{
    if (soc < 0 || soc > 15) return;

    volatile struct ADC_REGS* adc_regs;

    // Map the ADC module to the correct register
    if (adc == ADC_ADCA)
        adc_regs = &AdcaRegs;
    else if (adc == ADC_ADCB)
        adc_regs = &AdcbRegs;
    else if (adc == ADC_ADCC)
        adc_regs = &AdccRegs;
    else if (adc == ADC_ADCD)
        adc_regs = &AdcdRegs;
    else
        return;

    // Configure ADC module settings
    adc_regs->ADCCTL2.bit.PRESCALE = 6;  // Clock prescaler
    adc_regs->ADCCTL2.bit.RESOLUTION = (resolution == ADC_RESOLUTION_12BIT) ? 0 : 1;
    adc_regs->ADCCTL2.bit.SIGNALMODE = (signalMode == ADC_SIGNALMODE_SINGLE) ? 0 : 1;

    adc_regs->ADCCTL1.bit.INTPULSEPOS = 1; // Interrupt pulse at end of conversion
    adc_regs->ADCCTL1.bit.ADCPWDNZ = 1;    // Power up ADC module

    // Configure the SOC for the given channel
    (&adc_regs->ADCSOC0CTL)[soc].bit.CHSEL = channel;   // Select input channel
    (&adc_regs->ADCSOC0CTL)[soc].bit.ACQPS = 14;        // Set acquisition time
    (&adc_regs->ADCSOC0CTL)[soc].bit.TRIGSEL = 0;       // Software trigger

    // Dynamically assign an interrupt (INT1 or INT2) based on availability
    if (!adc_regs->ADCINTSEL1N2.bit.INT1E) {
        adc_regs->ADCINTSEL1N2.bit.INT1SEL = soc;  // Map SOC to ADCINT1
        adc_regs->ADCINTSEL1N2.bit.INT1E = 1;      // Enable ADCINT1
    }
    else if (!adc_regs->ADCINTSEL1N2.bit.INT2E) {
        adc_regs->ADCINTSEL1N2.bit.INT2SEL = soc;  // Map SOC to ADCINT2
        adc_regs->ADCINTSEL1N2.bit.INT2E = 1;      // Enable ADCINT2
    }
    else if (!adc_regs->ADCINTSEL3N4.bit.INT3E) {
        adc_regs->ADCINTSEL3N4.bit.INT3SEL = soc;  // Map SOC to ADCINT3
        adc_regs->ADCINTSEL3N4.bit.INT3E = 1;      // Enable ADCINT3
    }
    else if (!adc_regs->ADCINTSEL3N4.bit.INT4E) {
        adc_regs->ADCINTSEL3N4.bit.INT4SEL = soc;  // Map SOC to ADCINT4
        adc_regs->ADCINTSEL3N4.bit.INT4E = 1;      // Enable ADCINT4
    }
    else {
        // If both interrupts are in use, return or handle error
        return;
    }

    // Clear any existing interrupt flags
    adc_regs->ADCINTFLGCLR.bit.ADCINT1 = 1;
    adc_regs->ADCINTFLGCLR.bit.ADCINT2 = 1;
    adc_regs->ADCINTFLGCLR.bit.ADCINT3 = 1;
    adc_regs->ADCINTFLGCLR.bit.ADCINT4 = 1;
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

int ADC_ReadSOC(const char* adc_module, int soc, int generateInterrupt)
{
    if (soc < 0 || soc > 15)
    {
        return -1;
    }

    // for main1 and main2
    volatile struct ADC_REGS* adc_regs;


    volatile Uint16* adc_result;

    // Map ADC module
    if (strcmp(adc_module, "A") == 0)
    {
        adc_result = &AdcaResultRegs.ADCRESULT0;
        adc_regs = &AdcaRegs;
    }
    else if (strcmp(adc_module, "B") == 0)
    {
        adc_result = &AdcbResultRegs.ADCRESULT0;
        adc_regs = &AdcbRegs;
    }
    else if (strcmp(adc_module, "C") == 0)
    {
        adc_result = &AdccResultRegs.ADCRESULT0;
        adc_regs = &AdccRegs;
    }
    else if (strcmp(adc_module, "D") == 0)
    {
        adc_result = &AdcdResultRegs.ADCRESULT0;
        adc_regs = &AdcdRegs;
    }
    else
    {
        return -1;  // Invalid ADC module
    }

#if STATE == 1 || STATE == 2
    adc_regs->ADCSOCFRC1.all = 1 << soc;

    // Check which interrupt is linked to this SOC
    if (adc_regs->ADCINTSEL1N2.bit.INT1SEL == soc && adc_regs->ADCINTSEL1N2.bit.INT1E)
    {
        while (!adc_regs->ADCINTFLG.bit.ADCINT1);
        adc_regs->ADCINTFLGCLR.bit.ADCINT1 = 1;
    }
    else if (adc_regs->ADCINTSEL1N2.bit.INT2SEL == soc && adc_regs->ADCINTSEL1N2.bit.INT2E)
    {

        while (!adc_regs->ADCINTFLG.bit.ADCINT2);
        adc_regs->ADCINTFLGCLR.bit.ADCINT2 = 1;
    }
    else if (adc_regs->ADCINTSEL3N4.bit.INT3SEL == soc && adc_regs->ADCINTSEL3N4.bit.INT3E)
    {
        while (!adc_regs->ADCINTFLG.bit.ADCINT3);
        adc_regs->ADCINTFLGCLR.bit.ADCINT3 = 1;
    }
    else if (adc_regs->ADCINTSEL3N4.bit.INT4SEL == soc && adc_regs->ADCINTSEL3N4.bit.INT4E)
    {
        while (!adc_regs->ADCINTFLG.bit.ADCINT4);
        adc_regs->ADCINTFLGCLR.bit.ADCINT4 = 1;
    }
    else
    {
        return -1;  // SOC not linked to any interrupt
    }
    return adc_result[soc];
#endif

#if STATE == 3
    return adc_result[soc];
#endif

}



/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


void ADC_SetMode_main3(Uint16 adc, Uint16 resolution, Uint16 signalMode, int channel, int soc, int generate_interrupt)
{
    if (soc < 0 || soc > 15) return;

    volatile struct ADC_REGS* adc_regs;

    // Map the ADC module to the correct register
    if (adc == ADC_ADCA)
        adc_regs = &AdcaRegs;
    else if (adc == ADC_ADCB)
        adc_regs = &AdcbRegs;
    else if (adc == ADC_ADCC)
        adc_regs = &AdccRegs;
    else if (adc == ADC_ADCD)
        adc_regs = &AdcdRegs;
    else
        return;

    // Configure ADC module settings
    adc_regs->ADCCTL2.bit.PRESCALE = 6;  // Clock prescaler
    adc_regs->ADCCTL2.bit.RESOLUTION = (resolution == ADC_RESOLUTION_12BIT) ? 0 : 1;
    adc_regs->ADCCTL2.bit.SIGNALMODE = (signalMode == ADC_SIGNALMODE_SINGLE) ? 0 : 1;

    adc_regs->ADCCTL1.bit.INTPULSEPOS = 1; // Interrupt pulse at end of conversion
    adc_regs->ADCCTL1.bit.ADCPWDNZ = 1;    // Power up ADC module

    // Configure the SOC for the given channel
    (&adc_regs->ADCSOC0CTL)[soc].bit.CHSEL = channel;   // Select input channel
    (&adc_regs->ADCSOC0CTL)[soc].bit.ACQPS = 14;        // Set acquisition time
    if (generate_interrupt == 0) {
        (&adc_regs->ADCSOC0CTL)[soc].bit.TRIGSEL = 1;       // trigger da timer 0
    }

    // Dynamically assign an interrupt (INT1 or INT2) based on availability
    if (generate_interrupt == 1) {
        (&adc_regs->ADCSOC0CTL)[soc].bit.TRIGSEL = 0;       // software trigger
        adc_regs->ADCINTSEL1N2.bit.INT1SEL = soc;  // Map SOC to ADCINT1
        adc_regs->ADCINTSEL1N2.bit.INT1E = 1;      // Enable ADCINT1
    }

    // Clear any existing interrupt flags
    adc_regs->ADCINTFLGCLR.bit.ADCINT1 = 1;

}


// Initialize an ADC module
void ADC_Init_main3(const char* adc_module, int channel, int soc, int generate_interrurpt)
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

    ADC_SetMode_main3(adc_module_number, ADC_RESOLUTION_12BIT, ADC_SIGNALMODE_SINGLE, channel, soc, generate_interrurpt);

    // Delay to allow ADC to power up
    DELAY_US(1000);

    EDIS;
}



