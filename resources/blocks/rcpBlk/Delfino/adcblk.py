from supsisim.RCPblk import RCPblk
from numpy import size

def adcblk(pout, adc, channel, SOC, generateInterrupt):

    """
    Call:   adcblk(pout, "A", 5, 2, 0)

    Parameters
    ----------
        pout:              Connected output port.
        adc:               The ADC module as a string (e.g., "A", "B").
        channel:           Channel number (integer from 0 to 5).
        SOC:               SOC number for ADC (integer from 0 to 15).
        generateInterrupt: Indicates if the block generates an interrupt when the conversion is complete.

    Returns
    -------
        blk: RCPblk
    """

    valid_adc_modules = ["A", "B", "C", "D"]

    # Maximum values for channels and SOC
    max_channels = 5
    max_SOC = 15

    # Check if ADC module is valid
    if not isinstance(adc, str):
        raise ValueError(f"ADC parameter must be a string; received type {type(adc).__name__}.")
    
    adc = adc.upper()
    if adc not in valid_adc_modules:
        raise ValueError(f"ADC parameter must be one of {valid_adc_modules}; received {adc}.")

    # Check if channel is valid
    if not isinstance(channel, int) or not (0 <= channel <= max_channels):
        raise ValueError(f"Channel must be an integer between 0 and {max_channels}; received {channel}.")

    # Check if SOC is valid
    if not isinstance(SOC, int) or not (0 <= SOC <= max_SOC):
        raise ValueError(f"SOC must be an integer between 0 and {max_SOC}; received {SOC}.")

    # Check if generateInterrupt is valid
    if not isinstance(generateInterrupt, int) or generateInterrupt not in [0, 1]:
        raise ValueError(f"generateInterrupt must be 0 or 1; received {generateInterrupt}.")

    # Check if pout is valid
    if(size(pout) != 1):
        raise ValueError("Block should have 1 output pin; received %i." % size(pout))

    blk = RCPblk('adcblk', [], pout, [0,0], 0, [], [channel, SOC, generateInterrupt], adc)
    return blk
