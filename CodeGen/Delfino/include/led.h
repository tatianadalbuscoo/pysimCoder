#ifndef LED_H
#define LED_H

#include "F28x_Project.h"

// Define the LED GPIO pin
//#define LED_GPIO_BLUE 31

// Function Prototypes
void LED_Init(int pin);
void LED_On(int pin);
void LED_Off(int pin);

#endif // LED_H
