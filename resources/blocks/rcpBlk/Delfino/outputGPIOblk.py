from supsisim.RCPblk import RCPblk
from numpy import size

def outputGPIOblk(pin, gpio_number):

    """
    Call:   outputGPIOblk(pin, 31)

    Parameters
    ----------
       pin: connected input port.
       gpio_number: the GPIO pin number (e.g., 31 for GPIO31)

    Returns
    -------
       blk: RCPblk
    """
    
    # Check if gpio_number is a positive integer
    if not isinstance(gpio_number, int) or gpio_number < 0:
        raise ValueError("GPIO pin number must be a positive integer; received %s." % str(gpio_number))
    
    # Check if pin is valid
    if(size(pin) != 1):
        raise ValueError("Block should have 1 input pin; received %i." % size(pin))
    
    blk = RCPblk('outputGPIOblk', pin, [], [0,0], 0, [], [gpio_number])
    return blk
