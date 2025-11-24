"""
module for PPP-RTK positioning
"""

import numpy as np
from cssrlib.pppssr import pppos


class ppprtkpos(pppos):
    """ class for PPP-RTK processing """

    def __init__(self, nav, pos0=np.zeros(3), logfile=None, config=None):
        """ initialize variables for PPP-RTK """

        # trop, iono from cssr
        # phase windup model is local/regional
        super().__init__(nav=nav, pos0=pos0, logfile=logfile, config=config)

        # self.nav.eratio = np.ones(self.nav.nf)*50  # [-] factor
        # self.nav.err = [0, 0.01, 0.005]/np.sqrt(2)  # [m] sigma
        # self.nav.sig_p0 = 30.0  # [m]
        # self.nav.thresar = 2.0  # AR acceptance threshold
        # self.nav.armode = 3     # AR is enabled
