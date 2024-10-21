from supsisim.RCPblk import RCPblk
from numpy import size

def inputGPIOblk(pout, gpio_number):
    """
    Call:   inputGPIOblk(pout, gpio_number)

    Parameters
    ----------
       pout: connected output port(s)
       gpio_number: the GPIO pin number (e.g., 6 for GPIO6)

    Returns
    -------
       blk: RCPblk
    """
    
    if(size(pout) != 1):
        raise ValueError("Block should have 1 output pin; received %i." % size(pout))
    
    # blk creation with pout (output), gpio_number (input pin)
    blk = RCPblk('inputGPIOblk', [], pout, [0,0], 0, [], [gpio_number])
    return blk
