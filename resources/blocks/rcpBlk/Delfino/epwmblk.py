from supsisim.RCPblk import RCPblk
from numpy import size

def epwmblk(duty_cycle, pwm, TBPRD):

    """
    Call:   epwmblk(duty_cycle, pwm, TBPRD)

    Parameters
    ----------
        duty_cycle: The percentage of time the signal is high relative to the pwm period (input).
        pwm:        Connected output port name as a string for the PWM signal (e.g., "out1a").
        TBPRD:      Register used for pwm period. (formula: TBPRD = (Tpwm * 100MHz)/2.

    Returns
    -------
       blk: RCPblk
    """

    valid_pwm_outputs = ["out1a", "out1b", "out2a", "out2b", "out3a", "out3b", "out4a", "out4b", "out5a", "out5b", "out6a", "out6b", "out7a", "out7b", "out8a", "out8b", "out9a", "out9b", "out10a", "out10b", "out11a", "out11b", "out12a", "out12b"]
    
    # Check if pwm is a str type
    if not isinstance(pwm, str):
        raise ValueError(f"PWM parameter must be a string; received type {type(pwm).__name__}.")
    
    # Convert to lowercase
    pwm = pwm.lower()

    # Check if pwm is valid
    if not isinstance(pwm, str) or pwm not in valid_pwm_outputs:
        raise ValueError(f"PWM parameter should be one of {valid_pwm_outputs}; received {pwm}.")
    
    # Check if TBPRD is valid
    if TBPRD <= 0:
        raise ValueError(f"Time Base Period (TBPRD) should be a positive number; received {TBPRD}.")

    # Duty cycle control is done in the epwmblk.c file
    
    blk = RCPblk('epwmblk', duty_cycle, [], [0,0], 0, [], [TBPRD], pwm)
    return blk
