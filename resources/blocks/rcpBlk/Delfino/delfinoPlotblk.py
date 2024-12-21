from supsisim.RCPblk import RCPblk
from numpy import size

def delfinoPlotblk(signal):

    """
    Call:   epwmblk(1.2)

    Parameters
    ----------
        signal: connected input port. The signal you want to plot (float).

    Returns
    -------
       blk: RCPblk
    """

    # Check if signal is valid
    if(size(signal) != 1):
        raise ValueError("Block should have 1 input signal; received %i." % size(signal))
    
    blk = RCPblk('delfinoPlotblk', signal, [], [0,0], 0, [], [])
    return blk
