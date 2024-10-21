from supsisim.RCPblk import RCPblk
from numpy import size

def outputGPIOblk(pin, gpio_number):
    """
    Call:   outputGPIOblk(pin, gpio_number)

    Parameters
    ----------
       pin: connected input port(s)
       gpio_number: the GPIO pin number (e.g., 31 for GPIO31)

    Returns
    -------
       blk: RCPblk
    """
    
    if(size(pin) != 1):
        raise ValueError("Block should have 1 input pin; received %i." % size(pin))
    
    # blk creation with pin, gpio_number
    blk = RCPblk('outputGPIOblk', pin, [], [0,0], 0, [], [gpio_number])
    return blk
