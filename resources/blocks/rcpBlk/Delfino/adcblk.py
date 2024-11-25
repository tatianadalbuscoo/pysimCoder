from supsisim.RCPblk import RCPblk

def adcblk(pout, adc, channel, SOC):
    """
    Call:   adcblk(pout, adc, channel, SOC)

    Parameters
    ----------
        pout:    Connected adc and channel.
        adc:     The ADC module as a string (e.g., "A", "B")
        channel: Channel number (integer from 0 to 5).
        SOC:     SOC number for ADC (e.g., 0, 1, etc.).

    Returns
    -------
        blk: RCPblk
    """
    valid_adc_modules = ["A", "B", "C", "D"]
    max_channels = 5  # Maximum channel for ADCINA (channels 0 to 5)

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
    if not isinstance(SOC, int) or SOC < 0:
        raise ValueError(f"SOC must be a non-negative integer; received {SOC}.")

    blk = RCPblk('adcblk', [], pout, [0,0], 0, [], [channel, SOC], adc)
    return blk
