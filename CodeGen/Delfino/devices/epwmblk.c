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
#include "pyblock.h"

static void init(python_block* block)
{
    char* pwm_output = (char*)block->str; 
    int tbprd = block->intPar[0];  

    // Duty-cycle input (0.0 to 1.0 range)
    double* u = block->u[0];

    // Invert the input value, to have the percentage of high time incoming and not low time
    double duty_cycle = 1 - u[0];

    // Ensure the input duty-cycle is within valid bounds
    if (duty_cycle < 0.0) duty_cycle = 0.0;
    if (duty_cycle > 1.0) duty_cycle = 1.0;

    // Convert the duty-cycle to a percentage
    int duty_cycle_percentage = (int)(duty_cycle * 100);
    ConfigureEPWM(pwm_output, tbprd, duty_cycle_percentage);

}


static void inout(python_block* block)
{
    char* pwm_output = (char*)block->str;
    int tbprd = block->intPar[0];

    // Duty-cycle input (0.0 to 1.0 range)
    double* u = block->u[0];

    // Invert the input value, to have the percentage of high time incoming and not low time
    double duty_cycle = 1 - u[0];

    // Ensure the duty-cycle input is within valid bounds
    if (duty_cycle < 0.0) duty_cycle = 0.0;
    if (duty_cycle > 1.0) duty_cycle = 1.0;

    // Convert the duty-cycle to a percentage and update the ePWM module
    int duty_cycle_percentage = (int)(duty_cycle * 100);
    UpdateEPWMDutyCycle(pwm_output, tbprd, duty_cycle_percentage);
}


static void end(python_block* block)
{
    char* pwm_output = (char*)block->str;
    int tbprd = block->intPar[0];

    // Set duty-cycle to 0% on termination
    UpdateEPWMDutyCycle(pwm_output, tbprd, 0);
}

void epwmblk(int flag, python_block* block)
{
    if (flag == CG_OUT) 
    {
        inout(block);
    }
    else if (flag == CG_END) 
    {
        end(block);
    }
    else if (flag == CG_INIT) 
    {
        init(block);
    }
}
