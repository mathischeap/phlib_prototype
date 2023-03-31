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
        return self._mapping

    @mapping.setter
    def mapping(self, mp):
        """"""
        self._mapping = mp
