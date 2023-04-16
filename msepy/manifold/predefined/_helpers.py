# -*- coding: utf-8 -*-
"""
@author: Yi Zhang
@contact: zhangyi_aero@hotmail.com
"""
from src.tools.frozen import Frozen


class _LinearTransformation(Frozen):
    """
    [0, 1]^n -> [x0, x1] x [y0, y1] x ...

    x0, x1, y0, y1 ... = * xb_yb_zb

    len(xb_yb_zb) = 2 * n

    """

    def __init__(self, *xb_yb_zb):
        """"""
        assert len(xb_yb_zb) % 2 == 0 and len(xb_yb_zb) >= 2, f"axis bounds must be even number and > 2."
        self._low_bounds = list()
        self._delta = list()
        for i in range(0, len(xb_yb_zb), 2):
            lb, ub = xb_yb_zb[i], xb_yb_zb[i+1]  # with `i` being axis
            assert ub > lb, f"lb={lb}, ub={ub} of {i}th axis is wrong. Must have lb < up."
            self._low_bounds.append(lb)
            self._delta.append(ub - lb)
        J = tuple()
        for i in range(len(self._low_bounds)):
            xr = list(0 for _ in range(len(self._low_bounds)))
            xr[i] = self._delta[i]
            J += (xr, )
        self._J = J
        self._freeze()

    def mapping(self, *rst):
        """"""
        assert len(rst) == len(self._low_bounds), f"rst dimensions wrong."
        x = list()
        for i, r in enumerate(rst):
            lb = self._low_bounds[i]
            delta = self._delta[i]
            x.append(r * delta + lb)
        return x

    def Jacobian_matrix(self, *rst):
        assert len(rst) == len(self._low_bounds), f"rst dimensions wrong."
        return self._J