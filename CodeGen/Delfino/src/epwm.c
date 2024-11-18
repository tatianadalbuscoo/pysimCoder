#include "epwm.h"
#include <string.h>

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
    switch (gpio_number) {
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
    if (channel == 'A') {
        switch (gpio_number) {
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
    else if (channel == 'B') {
        switch (gpio_number) {
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
}

// Main function to configure a specific ePWM channel
void ConfigureEPWM(const char* pwm_output, int tbprd, int duty_cycle) 
{

    // Invert duty cycle
    duty_cycle = 100 - duty_cycle;

    // Calculate CMPA value
    int cmpa = (int)(((float)duty_cycle / 100) * tbprd);

    int epwm_number = 0;
    int gpio_number = 0;
    char channel = 0;

    // Map PWM output to ePWM module, GPIO number, and channel
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
    else 
    {

        // Invalid output
        return;
    }

    // Enable ePWM clock
    EnableEPWMClock(epwm_number);

    // Configure GPIO for the specific ePWM output
    ConfigureGPIOForEPWM(gpio_number, channel);

    // Get the appropriate ePWM register set
    volatile struct EPWM_REGS* EPwmRegs = NULL;
    switch (epwm_number) {
    case 1: EPwmRegs = &EPwm1Regs; break;
    case 2: EPwmRegs = &EPwm2Regs; break;
    case 3: EPwmRegs = &EPwm3Regs; break;
    case 4: EPwmRegs = &EPwm4Regs; break;
    case 5: EPwmRegs = &EPwm5Regs; break;
    case 6: EPwmRegs = &EPwm6Regs; break;
    case 8: EPwmRegs = &EPwm8Regs; break;
    }

    // Configure ePWM registers
    if (EPwmRegs) {
        ConfigureEPWMRegisters(EPwmRegs, tbprd, cmpa);
        if (channel == 'A') {
            EPwmRegs->AQCTLA.bit.CAU = AQ_SET;   // Set high on count up
            EPwmRegs->AQCTLA.bit.CAD = AQ_CLEAR; // Set low on count down
        }
        else if (channel == 'B') {
            EPwmRegs->AQCTLB.bit.CAU = AQ_SET;   // Set high on count up
            EPwmRegs->AQCTLB.bit.CAD = AQ_CLEAR; // Set low on count down
        }
    }
}

