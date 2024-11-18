#ifndef EPWM_H
#define EPWM_H

#include "F28x_Project.h"


void EnableEPWMClock(int epwm_number);
void ConfigureGPIOForEPWM(int gpio_number, char channel);
void ConfigureEPWMRegisters(volatile struct EPWM_REGS* EPwmRegs, int tbprd, int cmpa);
void ConfigureEPWM(const char* pwm_output, int tbprd, int duty_cycle);

#endif // EPWM_H
