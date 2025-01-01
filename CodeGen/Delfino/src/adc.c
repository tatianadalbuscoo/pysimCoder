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

#include "adcDelfino.h"
#include <string.h>

// Function Prototypes
void ADC_SetMode(Uint16 adc, Uint16 resolution, Uint16 signalMode, int channel, int soc);
void ADC_SetMode_main3_4(Uint16 adc, Uint16 resolution, Uint16 signalMode, int channel, int soc, int generate_interrupt);

// Main1 and Main2

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

    // Dynamically assign an interrupt based on availability
    if (!adc_regs->ADCINTSEL1N2.bit.INT1E) 
    {
        adc_regs->ADCINTSEL1N2.bit.INT1SEL = soc;  // Map SOC to ADCINT1
        adc_regs->ADCINTSEL1N2.bit.INT1E = 1;      // Enable ADCINT1
    }
    else if (!adc_regs->ADCINTSEL1N2.bit.INT2E) 
    {
        adc_regs->ADCINTSEL1N2.bit.INT2SEL = soc;  // Map SOC to ADCINT2
        adc_regs->ADCINTSEL1N2.bit.INT2E = 1;      // Enable ADCINT2
    }
    else if (!adc_regs->ADCINTSEL3N4.bit.INT3E) 
    {
        adc_regs->ADCINTSEL3N4.bit.INT3SEL = soc;  // Map SOC to ADCINT3
        adc_regs->ADCINTSEL3N4.bit.INT3E = 1;      // Enable ADCINT3
    }
    else if (!adc_regs->ADCINTSEL3N4.bit.INT4E) 
    {
        adc_regs->ADCINTSEL3N4.bit.INT4SEL = soc;  // Map SOC to ADCINT4
        adc_regs->ADCINTSEL3N4.bit.INT4E = 1;      // Enable ADCINT4
    }
    else 
    {
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


/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


// Main3 and Main4

// Configure an ADC module with resolution, signal mode, channel, trigger and specific SOC
void ADC_SetMode_main3_4(Uint16 adc, Uint16 resolution, Uint16 signalMode, int channel, int soc, int generate_interrupt)
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
#if STATE == 3
        (&adc_regs->ADCSOC0CTL)[soc].bit.TRIGSEL = 1;       // Trigger given by timer0
# endif

#if STATE == 4
    #if defined(NREPWMTRIGGERADC)

            // Trigger given by the number of epwm chosen in the configuration
            (&adc_regs->ADCSOC0CTL)[soc].bit.TRIGSEL = NREPWMTRIGGERADC;    
    #endif
#endif
    }

    if (generate_interrupt == 1) {

#if STATE == 4
        #if defined(NREPWMTRIGGERADC)
                    (&adc_regs->ADCSOC0CTL)[soc].bit.TRIGSEL = NREPWMTRIGGERADC;
        #endif
#endif
        adc_regs->ADCINTSEL1N2.bit.INT1SEL = soc;  // Map SOC to ADCINT1
        adc_regs->ADCINTSEL1N2.bit.INT1E = 1;      // Enable ADCINT1
    }

    // Clear any existing interrupt flags
    adc_regs->ADCINTFLGCLR.bit.ADCINT1 = 1;

}


// Initialize an ADC module
void ADC_Init_main3_4(const char* adc_module, int channel, int soc, int generate_interrurpt)
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

    ADC_SetMode_main3_4(adc_module_number, ADC_RESOLUTION_12BIT, ADC_SIGNALMODE_SINGLE, channel, soc, generate_interrurpt);

    // Delay to allow ADC to power up
    DELAY_US(1000);

    EDIS;
}


//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


// Function for all main 1,2,3,4

// reads the value of a specified ADC channel (module and SOC), forcing conversion and waiting for 
// completion via interrupt or directly returning the result depending on the STATE.
int ADC_ReadSOC(const char* adc_module, int soc, int generateInterrupt)
{
    if (soc < 0 || soc > 15)
    {
        return -1;
    }

    // For main1 and main2
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

#if STATE == 3 || STATE == 4
    return adc_result[soc];
#endif

}

