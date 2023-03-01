# -*- coding: utf-8 -*-
"""
@author: Yi Zhang
@contact: zhangyi_aero@hotmail.com
@time: 11/26/2022 2:56 PM
"""
import sys

if './' not in sys.path:
    sys.path.append('./')

from src.config import get_embedding_space_dim
from src.spaces.main import _new, set_mesh


def wedge(s1, s2):
    """"""
    if s1.__class__.__name__ == 'ScalarValuedFormSpace' and s2.__class__.__name__ == 'ScalarValuedFormSpace':

        assert s1.mesh == s2.mesh, f"two entries have different meshes."

        k = s1.k
        l = s2.k

        assert k + l <= get_embedding_space_dim()

        set_mesh(s1.mesh)   # let the `space.mesh` become the current mesh.
        return _new('Omega', k + l, s1.p + s2.p)

    else:
        raise NotImplementedError()


def Hodge(s):
    """A not well-defined one"""
    if s.__class__.__name__ == 'ScalarValuedFormSpace':
        n = get_embedding_space_dim()
        set_mesh(s.mesh)   # let the `space.mesh` become the current mesh.
        return _new('Omega', n - s.k, s.p)
    else:
        raise NotImplementedError()


def d(space):
    """the range of exterior derivative operator on `space`."""
    if space.__class__.__name__ == 'ScalarValuedFormSpace':
        assert space.k < get_embedding_space_dim(), f'd of top-form is 0.'
        set_mesh(space.mesh)   # let the `space.mesh` become the current mesh.
        return _new('Omega', space.k + 1, space.p)
    else:
        raise NotImplementedError()


def codifferential(space):
    """the range of exterior derivative operator on `space`."""
    if space.__class__.__name__ == 'ScalarValuedFormSpace':
        assert space.k > 0, f'd of 0-form is 0.'
        set_mesh(space.mesh)   # let the `space.mesh` become the current mesh.
        return _new('Omega', space.k - 1, space.p)
    else:
        raise NotImplementedError()
