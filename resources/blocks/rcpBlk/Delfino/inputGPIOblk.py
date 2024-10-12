from supsisim.RCPblk import RCPblk
from numpy import size

def inputGPIOblk(pout, gpio_number, state):
    """
    Call:   inputGPIOblk(pout, gpio_number, state)

    Parameters
    ----------
       pout: connected output port(s)
       gpio_number: the GPIO pin number (e.g., 6 for GPIO6)
       state: the current state of the GPIO (0 or 1)

    Returns
    -------
       blk: RCPblk
    """
    
    if(size(pout) != 1):
        raise ValueError("Block should have 1 output pin; received %i." % size(pout))
    
    # blk creation with pout (output), gpio_number (input pin), and state
    blk = RCPblk('inputGPIOb', [], pout, [state, gpio_number], 0, [], [])
    return blk
