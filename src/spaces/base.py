# -*- coding: utf-8 -*-
"""
@author: Yi Zhang
@contact: zhangyi_aero@hotmail.com
@time: 11/26/2022 2:56 PM
"""

from src.tools.frozen import Frozen
from src.config import get_embedding_space_dim
from src.form.main import Form
from src.form.main import _global_form_variables
from src.spaces.finite import SpaceFiniteSetting


class SpaceBase(Frozen):
    """"""

    def __init__(self, mesh, orientation):
        """"""
        self._mesh = mesh
        assert orientation in ('inner', 'outer', 'i', 'o', None, 'None'), \
            f"orientation={orientation} is wrong, must be one of ('inner', 'outer', 'i', 'o', None)."
        if orientation == 'i':
            orientation = 'inner'
        elif orientation == 'o':
            orientation = 'outer'
        elif orientation in (None, 'unknown'):
            orientation = 'unknown'
        else:
            pass
        self._orientation = orientation
        self._finite = None  # the finite setting
        self._instances = list()

    @property
    def mesh(self):
        """"""
        return self._mesh

    @property
    def manifold(self):
        return self.mesh.manifold

    @property
    def orientation(self):
        return self._orientation

    @property
    def n(self):
        """"""
        return get_embedding_space_dim()

    def make_form(self, sym_repr, lin_repr):
        """"""
        assert isinstance(sym_repr, str), f"symbolic representation must be a str."
        f = Form(
            self, sym_repr, lin_repr,
            True,  # is_root
        )
        if _global_form_variables['update_cache']:
            self._instances.append(f)

        return f

    def __eq__(self, other):
        """"""
        return self.__repr__() == other.__repr__()

    @staticmethod
    def _is_space():
        """A private tag."""
        return True

    @property
    def finite(self):
        if self._finite is None:
            self._finite = SpaceFiniteSetting(self)
        return self._finite
