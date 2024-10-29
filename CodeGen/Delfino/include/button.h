#ifndef BUTTON_H
#define BUTTON_H

#include "F28x_Project.h"

// Define the Button GPIO pin
//#define BUTTON_GPIO_PIN 6

// Function Prototypes
void Button_Init(int pin);
Uint16 Button_IsPressed(int pin);

#endif // BUTTON_H
