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
#include "pyblock.h"

static void init(python_block* block)
{
    char* adc_module = (char*)block->str;
    int channel = block->intPar[0];
    int soc = block->intPar[1];

    // Initialize ADC
#if STATE == 1 || STATE ==2
    ADC_Init(adc_module, channel, soc);
#endif   

#if STATE == 3 || STATE == 4
    int generateInterrupt = block->intPar[2];
    ADC_Init_main3_4(adc_module, channel, soc, generateInterrupt);
#endif

}

static void inout(python_block* block)
{
    char* adc_module = (char*)block->str;
    int soc = block->intPar[1];
    int generateInterrupt = block->intPar[2];
    double* y = block->y[0];

    // Read ADC value
    int adcResult = ADC_ReadSOC(adc_module, soc, generateInterrupt);
    *y = (double)adcResult;
}


static void end(python_block* block)
{

}

void adcblk(int flag, python_block* block)
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
