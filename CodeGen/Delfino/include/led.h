#ifndef LED_H
#define LED_H

#include "F28x_Project.h"

// Define the LED GPIO pin
#define LED_GPIO_BLUE 31

// Function Prototypes
void LED_Init(void);
void LED_On(void);
void LED_Off(void);

#endif // LED_H
