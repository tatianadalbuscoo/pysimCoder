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

#include "epwm.h"
#include <string.h>

// Function Prototypes
void EnableEPWMClock(int epwm_number);
void ConfigureGPIOForEPWM(int gpio_number, char channel);
void ConfigureEPWMRegisters(volatile struct EPWM_REGS* EPwmRegs, int tbprd, int cmpa);


// Helper function to enable clock for a specific ePWM module
void EnableEPWMClock(int epwm_number)
{
    EALLOW;
    CpuSysRegs.PCLKCR2.all |= (1 << (epwm_number - 1));
    EDIS;
}

// Helper function to configure GPIO for ePWM output
void ConfigureGPIOForEPWM(int gpio_number, char channel)
{
    EALLOW;

    // Disable internal pull-up for GPIO
    switch (gpio_number) 
    {
        case 0: GpioCtrlRegs.GPAPUD.bit.GPIO0 = 1; break;
        case 1: GpioCtrlRegs.GPAPUD.bit.GPIO1 = 1; break;
        case 2: GpioCtrlRegs.GPAPUD.bit.GPIO2 = 1; break;
        case 3: GpioCtrlRegs.GPAPUD.bit.GPIO3 = 1; break;
        case 4: GpioCtrlRegs.GPAPUD.bit.GPIO4 = 1; break;
        case 5: GpioCtrlRegs.GPAPUD.bit.GPIO5 = 1; break;
        case 6: GpioCtrlRegs.GPAPUD.bit.GPIO6 = 1; break;
        case 7: GpioCtrlRegs.GPAPUD.bit.GPIO7 = 1; break;
        case 8: GpioCtrlRegs.GPAPUD.bit.GPIO8 = 1; break;
        case 9: GpioCtrlRegs.GPAPUD.bit.GPIO9 = 1; break;
        case 10: GpioCtrlRegs.GPAPUD.bit.GPIO10 = 1; break;
        case 11: GpioCtrlRegs.GPAPUD.bit.GPIO11 = 1; break;
        case 14: GpioCtrlRegs.GPAPUD.bit.GPIO14 = 1; break;
        case 15: GpioCtrlRegs.GPAPUD.bit.GPIO15 = 1; break;
        default: return; // Invalid gpio_number
    }

    // Configure MUX for ePWM output
    if (channel == 'A') 
    {
        switch (gpio_number) 
        {
            case 0: GpioCtrlRegs.GPAMUX1.bit.GPIO0 = 1; break;
            case 1: GpioCtrlRegs.GPAMUX1.bit.GPIO1 = 1; break;
            case 2: GpioCtrlRegs.GPAMUX1.bit.GPIO2 = 1; break;
            case 3: GpioCtrlRegs.GPAMUX1.bit.GPIO3 = 1; break;
            case 4: GpioCtrlRegs.GPAMUX1.bit.GPIO4 = 1; break;
            case 5: GpioCtrlRegs.GPAMUX1.bit.GPIO5 = 1; break;
            case 6: GpioCtrlRegs.GPAMUX1.bit.GPIO6 = 1; break;
            case 7: GpioCtrlRegs.GPAMUX1.bit.GPIO7 = 1; break;
            case 8: GpioCtrlRegs.GPAMUX1.bit.GPIO8 = 1; break;
            case 9: GpioCtrlRegs.GPAMUX1.bit.GPIO9 = 1; break;
            case 10: GpioCtrlRegs.GPAMUX1.bit.GPIO10 = 1; break;
            case 11: GpioCtrlRegs.GPAMUX1.bit.GPIO11 = 1; break;
            case 14: GpioCtrlRegs.GPAMUX1.bit.GPIO14 = 1; break;
            case 15: GpioCtrlRegs.GPAMUX1.bit.GPIO15 = 1; break;
            default: return; // Invalid gpio_number
        }
    }
    else if (channel == 'B') 
    {
        switch (gpio_number) 
        {
            case 0: GpioCtrlRegs.GPAMUX1.bit.GPIO0 = 1; break;
            case 1: GpioCtrlRegs.GPAMUX1.bit.GPIO1 = 1; break;
            case 2: GpioCtrlRegs.GPAMUX1.bit.GPIO2 = 1; break;
            case 3: GpioCtrlRegs.GPAMUX1.bit.GPIO3 = 1; break;
            case 4: GpioCtrlRegs.GPAMUX1.bit.GPIO4 = 1; break;
            case 5: GpioCtrlRegs.GPAMUX1.bit.GPIO5 = 1; break;
            case 6: GpioCtrlRegs.GPAMUX1.bit.GPIO6 = 1; break;
            case 7: GpioCtrlRegs.GPAMUX1.bit.GPIO7 = 1; break;
            case 8: GpioCtrlRegs.GPAMUX1.bit.GPIO8 = 1; break;
            case 9: GpioCtrlRegs.GPAMUX1.bit.GPIO9 = 1; break;
            case 10: GpioCtrlRegs.GPAMUX1.bit.GPIO10 = 1; break;
            case 11: GpioCtrlRegs.GPAMUX1.bit.GPIO11 = 1; break;
            case 14: GpioCtrlRegs.GPAMUX1.bit.GPIO14 = 1; break;
            case 15: GpioCtrlRegs.GPAMUX1.bit.GPIO15 = 1; break;
            default: return; // Invalid gpio_number
        }
    }

    EDIS;
}

// Helper function to configure ePWM registers
void ConfigureEPWMRegisters(volatile struct EPWM_REGS* EPwmRegs, int tbprd, int cmpa)
{
    EPwmRegs->TBPRD = tbprd;                        // Set PWM period
    EPwmRegs->CMPA.bit.CMPA = cmpa;                 // Set duty cycle
    EPwmRegs->TBCTL.bit.CTRMODE = TB_COUNT_UPDOWN;  // Set up-down count mode
    EPwmRegs->TBCTL.bit.PHSEN = TB_DISABLE;         // Disable phase
    EPwmRegs->TBCTL.bit.HSPCLKDIV = TB_DIV1;        // No high-speed clock division
    EPwmRegs->TBCTL.bit.CLKDIV = TB_DIV1;           // No clock division
    EPwmRegs->ETSEL.bit.INTSEL = ET_CTR_ZERO;       // Trigger interrupt a TBCTR = 0
    EPwmRegs->ETSEL.bit.INTEN = 1;                  // Abilita l'interrupt
    EPwmRegs->ETPS.bit.INTPRD = ET_1ST;             // Genera interrupt ad ogni evento
}

// Function to dynamically update the duty cycle
void UpdateEPWMDutyCycle(const char* pwm_output, int tbprd, double duty_cycle)
{
    
    // Calculate CMPA
    int cmpa = (int)(((float)duty_cycle / 100) * tbprd);

    volatile struct EPWM_REGS* EPwmRegs = NULL;
    if (strcmp(pwm_output, "out1a") == 0 || strcmp(pwm_output, "out1b") == 0) 
    {
        EPwmRegs = &EPwm1Regs;
    }
    else if (strcmp(pwm_output, "out2a") == 0 || strcmp(pwm_output, "out2b") == 0) 
    {
        EPwmRegs = &EPwm2Regs;
    }
    else if (strcmp(pwm_output, "out3a") == 0 || strcmp(pwm_output, "out3b") == 0) 
    {
        EPwmRegs = &EPwm3Regs;
    }
    else if (strcmp(pwm_output, "out4a") == 0 || strcmp(pwm_output, "out4b") == 0) 
    {
        EPwmRegs = &EPwm4Regs;
    }
    else if (strcmp(pwm_output, "out5a") == 0 || strcmp(pwm_output, "out5b") == 0) 
    {
        EPwmRegs = &EPwm5Regs;
    }
    else if (strcmp(pwm_output, "out6a") == 0 || strcmp(pwm_output, "out6b") == 0) 
    {
        EPwmRegs = &EPwm6Regs;
    }
    else if (strcmp(pwm_output, "out8a") == 0 || strcmp(pwm_output, "out8b") == 0) 
    {
        EPwmRegs = &EPwm8Regs;
    }
    else 
    {

        // PWM output is invalid
        return;
    }

    // Update the duty-cycle
    if (EPwmRegs) 
    {
        EPwmRegs->CMPA.bit.CMPA = cmpa;
    }
}

// Main function to configure a specific ePWM channel
void ConfigureEPWM(const char* pwm_output, int tbprd, int duty_cycle) {
    
    // Configure initial duty-cycle
    UpdateEPWMDutyCycle(pwm_output, tbprd, duty_cycle);

    // Map PWM output to ePWM module, GPIO number, and channel
    int epwm_number = 0;
    int gpio_number = 0;
    char channel = 0;

    if (strcmp(pwm_output, "out1a") == 0) { epwm_number = 1; gpio_number = 0; channel = 'A'; }
    else if (strcmp(pwm_output, "out1b") == 0) { epwm_number = 1; gpio_number = 1; channel = 'B'; }
    else if (strcmp(pwm_output, "out2a") == 0) { epwm_number = 2; gpio_number = 2; channel = 'A'; }
    else if (strcmp(pwm_output, "out2b") == 0) { epwm_number = 2; gpio_number = 3; channel = 'B'; }
    else if (strcmp(pwm_output, "out3a") == 0) { epwm_number = 3; gpio_number = 4; channel = 'A'; }
    else if (strcmp(pwm_output, "out3b") == 0) { epwm_number = 3; gpio_number = 5; channel = 'B'; }
    else if (strcmp(pwm_output, "out4a") == 0) { epwm_number = 4; gpio_number = 6; channel = 'A'; }
    else if (strcmp(pwm_output, "out4b") == 0) { epwm_number = 4; gpio_number = 7; channel = 'B'; }
    else if (strcmp(pwm_output, "out5a") == 0) { epwm_number = 5; gpio_number = 8; channel = 'A'; }
    else if (strcmp(pwm_output, "out5b") == 0) { epwm_number = 5; gpio_number = 9; channel = 'B'; }
    else if (strcmp(pwm_output, "out6a") == 0) { epwm_number = 6; gpio_number = 10; channel = 'A'; }
    else if (strcmp(pwm_output, "out6b") == 0) { epwm_number = 6; gpio_number = 11; channel = 'B'; }
    else if (strcmp(pwm_output, "out8a") == 0) { epwm_number = 8; gpio_number = 14; channel = 'A'; }
    else if (strcmp(pwm_output, "out8b") == 0) { epwm_number = 8; gpio_number = 15; channel = 'B'; }
    else {
        return; // Invalid output
    }

    // Enable ePWM clock
    EnableEPWMClock(epwm_number);

    // Configure GPIO for the specific ePWM output
    ConfigureGPIOForEPWM(gpio_number, channel);

    // Get the appropriate ePWM register set
    volatile struct EPWM_REGS* EPwmRegs = NULL;
    switch (epwm_number) 
    {
        case 1: EPwmRegs = &EPwm1Regs; break;
        case 2: EPwmRegs = &EPwm2Regs; break;
        case 3: EPwmRegs = &EPwm3Regs; break;
        case 4: EPwmRegs = &EPwm4Regs; break;
        case 5: EPwmRegs = &EPwm5Regs; break;
        case 6: EPwmRegs = &EPwm6Regs; break;
        case 8: EPwmRegs = &EPwm8Regs; break;
    }

    // Configure ePWM registers
    if (EPwmRegs) 
    {
        ConfigureEPWMRegisters(EPwmRegs, tbprd, EPwmRegs->CMPA.bit.CMPA);
        if (channel == 'A') 
        {
            EPwmRegs->AQCTLA.bit.CAU = AQ_SET;   // Set high on count up
            EPwmRegs->AQCTLA.bit.CAD = AQ_CLEAR; // Set low on count down
        }
        else if (channel == 'B') 
        {
            EPwmRegs->AQCTLB.bit.CAU = AQ_SET;   // Set high on count up
            EPwmRegs->AQCTLB.bit.CAD = AQ_CLEAR; // Set low on count down
        }
    }
}

