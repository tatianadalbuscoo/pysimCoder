from supsisim.RCPblk import RCPblk
from numpy import size

def delfinoPlotblk(signal):

    """
    Call:   epwmblk(signal)

    Parameters
    ----------
        signal: The signal you want to plot
        data: 

    Returns
    -------
       blk: RCPblk
    """

    
    blk = RCPblk('delfinoPlotblk', signal, [], [0,0], 0, [], [])
    return blk
