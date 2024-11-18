
from supsisim.RCPblk import RCPblk
from numpy import size

def epwmblk():
    """

    Call:   epwmblk()

    Parameters
    ----------
        : PWM
        : TBPRD

    Returns
    -------
       blk: RCPblk

    """

    blk = RCPblk('epwmb', [], [], [0,0], 0, [], [])
    return blk
