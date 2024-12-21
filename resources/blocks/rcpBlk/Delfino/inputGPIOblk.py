from supsisim.RCPblk import RCPblk
from numpy import size

def inputGPIOblk(pout, gpio_number):

    """
    Call:   inputGPIOblk(pout, 6)

    Parameters
    ----------
       pout: Connected output port.
       gpio_number: The GPIO pin number (e.g., 6 for GPIO6).

    Returns
    -------
       blk: RCPblk
    """
    
    # Check if gpio_number is a positive integer
    if not isinstance(gpio_number, int) or gpio_number < 0:
        raise ValueError("GPIO pin number must be a positive integer; received %s." % str(gpio_number))

    # Check if pout is valid
    if(size(pout) != 1):
        raise ValueError("Block should have 1 output pin; received %i." % size(pout))
    
    blk = RCPblk('inputGPIOblk', [], pout, [0,0], 0, [], [gpio_number])
    return blk
