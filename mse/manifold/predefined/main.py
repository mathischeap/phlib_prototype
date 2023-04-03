# -*- coding: utf-8 -*-
"""
@author: Yi Zhang
@contact: zhangyi_aero@hotmail.com
@time: 11/26/2022 2:56 PM
"""

import sys

if './' not in sys.path:
    sys.path.append('./')
from src.tools.frozen import Frozen


class RegionMapping(Frozen):
    """"""

    def __init__(self):
        self._mapping = None
        self._freeze()

    @property
    def mapping(self):
        """A mapping that maps the reference region[0,1]^n to a physical region."""
        return self._mapping

    @mapping.setter
    def mapping(self, mp):
        """Do not change it once it is set."""
        assert self._mapping is None, f"change a mapping is dangerous."
        self._mapping = mp