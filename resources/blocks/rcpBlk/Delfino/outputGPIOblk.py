from supsisim.RCPblk import RCPblk
from numpy import size

def outputGPIOblk(pin, gpio_number, state):
    """
    Call:   outputGPIOblk(pin, gpio_number, state)

    Parameters
    ----------
       pin: connected input port(s)
       gpio_number: the GPIO pin number (e.g., 31 for GPIO31)
       state: the state of the GPIO (0 to turn off, 1 to turn on)

    Returns
    -------
       blk: RCPblk
    """
    
    if(size(pin) != 1):
        raise ValueError("Block should have 1 input pin; received %i." % size(pin))
    
    # blk creation with pin, gpio_number, and state
    blk = RCPblk('outputGPIOb', pin, [], [state, gpio_number], 0, [], [])
    return blk
