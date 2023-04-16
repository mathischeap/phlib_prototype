# -*- coding: utf-8 -*-
"""
finite element setting

pH-lib@RAM-EEMCS-UT
created at: 3/30/2023 5:35 PM
"""

import sys

if './' not in sys.path:
    sys.path.append('./')

from src.manifold import _global_manifolds  # [manifold_sym_repr] -> manifold
from src.mesh import _global_meshes   # [mesh_sym_repr] -> mesh
from src.spaces.main import _space_set  # [mesh_sym_repr][space_sym_repr] -> space
from src.form.main import _global_root_forms_lin_dict  # [root-form_lin_repr] -> root-form
import msepy.main as msepy


_implemented_finite_elements = {
    'msepy': msepy,   # mimetic spectral elements
}


_finite_elements_setup = dict()


def apply(fe_name, obj_dict):
    """"""
    assert fe_name in _implemented_finite_elements, \
        f"finite element name={fe_name} is wrong, should be one of {_implemented_finite_elements.keys()}"

    implementation = _implemented_finite_elements[fe_name]
    implementation._check_config()
    implementation._parse_manifolds(_global_manifolds)
    implementation._parse_meshes(_global_meshes)
    implementation._parse_spaces(_space_set)
    implementation._parse_root_forms(_global_root_forms_lin_dict)

    obj_space = dict()
    for obj_name in obj_dict:
        obj = obj_dict[obj_name]
        particular_obj = _parse_obj(implementation, obj)
        if particular_obj is not None:
            obj_space[obj_name] = particular_obj
        else:
            pass

    return implementation, obj_space


def _parse_obj(implementation, obj):
    """"""
    base = implementation.base
    if hasattr(obj, "_sym_repr"):   # manifolds, meshes, spaces and (root-)forms are produced anyway!
        sym_repr = obj._sym_repr
        if sym_repr in base['manifolds']:
            return base['manifolds'][sym_repr]
        elif sym_repr in base['meshes']:
            return base['meshes'][sym_repr]
        elif sym_repr in base['spaces']:
            return base['spaces'][sym_repr]
        elif sym_repr in base['forms']:
            return base['forms'][sym_repr]
        else:
            return implementation._parse(obj)
    else:
        return implementation._parse(obj)


if __name__ == '__main__':
    # python src/fem.py
    import __init__ as ph

    samples = ph.samples

    periodic = False
    oph = samples.pde_canonical_pH(n=3, p=3, periodic=periodic)[0]
    a3, b2 = oph.unknowns
    # oph.pr()

    wf = oph.test_with(oph.unknowns, sym_repr=[r'v^3', r'u^2'])

    wf = wf.derive.integration_by_parts('1-1')
    # wf.pr(indexing=True)
    if periodic is False:

        td = wf.td
        td.set_time_sequence()  # initialize a time sequence

        td.define_abstract_time_instants('k-1', 'k-1/2', 'k')
        td.differentiate('0-0', 'k-1', 'k')
        td.average('0-1', b2, ['k-1', 'k'])

        td.differentiate('1-0', 'k-1', 'k')
        td.average('1-1', a3, ['k-1', 'k'])
        td.average('1-2', a3, ['k-1/2'])
        dt = td.time_sequence.make_time_interval('k-1', 'k')

        wf = td()

        # wf.pr()

        wf.unknowns = [
            a3 @ td.time_sequence['k'],
            b2 @ td.time_sequence['k'],
        ]

        wf = wf.derive.split(
            '0-0', 'f0',
            [a3 @ td.ts['k'], a3 @ td.ts['k-1']],
            ['+', '-'],
            factors=[1/dt, 1/dt],
        )

        wf = wf.derive.split(
            '0-2', 'f0',
            [ph.d(b2 @ td.ts['k-1']), ph.d(b2 @ td.ts['k'])],
            ['+', '+'],
            factors=[1/2, 1/2],
        )

        wf = wf.derive.split(
            '1-0', 'f0',
            [b2 @ td.ts['k'], b2 @ td.ts['k-1']],
            ['+', '-'],
            factors=[1/dt, 1/dt]
        )

        wf = wf.derive.split(
            '1-2', 'f0',
            [a3 @ td.ts['k-1'], a3 @ td.ts['k']],
            ['+', '+'],
            factors=[1/2, 1/2],
        )

        wf = wf.derive.rearrange(
            {
                0: '0, 3 = 2, 1',
                1: '3, 0 = 2, 1, 4',
            }
        )

        ph.space.finite(3)

        mp = wf.mp()
        # mp.parse([
        #     a3 @ td.time_sequence['k-1'],
        #     b2 @ td.time_sequence['k-1']]
        # )
        ls = mp.ls()

    else:

        td = wf.td
        td.set_time_sequence()  # initialize a time sequence

        td.define_abstract_time_instants('k-1', 'k-1/2', 'k')
        td.differentiate('0-0', 'k-1', 'k')
        td.average('0-1', b2, ['k-1', 'k'])

        td.differentiate('1-0', 'k-1', 'k')
        td.average('1-1', a3, ['k-1', 'k'])
        dt = td.time_sequence.make_time_interval('k-1', 'k')

        wf = td()

        # wf.pr()

        wf.unknowns = [
            a3 @ td.time_sequence['k'],
            b2 @ td.time_sequence['k'],
            ]

        wf = wf.derive.split(
            '0-0', 'f0',
            [a3 @ td.ts['k'], a3 @ td.ts['k-1']],
            ['+', '-'],
            factors=[1/dt, 1/dt],
        )

        wf = wf.derive.split(
            '0-2', 'f0',
            [ph.d(b2 @ td.ts['k-1']), ph.d(b2 @ td.ts['k'])],
            ['+', '+'],
            factors=[1/2, 1/2],
        )

        wf = wf.derive.split(
            '1-0', 'f0',
            [b2 @ td.ts['k'], b2 @ td.ts['k-1']],
            ['+', '-'],
            factors=[1/dt, 1/dt]
        )

        wf = wf.derive.split(
            '1-2', 'f0',
            [a3 @ td.ts['k-1'], a3 @ td.ts['k']],
            ['+', '+'],
            factors=[1/2, 1/2],
        )

        wf = wf.derive.rearrange(
            {
                0: '0, 3 = 2, 1',
                1: '3, 0 = 2, 1',
            }
        )

        ph.space.finite(3)

        mp = wf.mp()
        # mp.parse([
        #     a3 @ td.time_sequence['k-1'],
        #     b2 @ td.time_sequence['k-1']]
        # )
        ls = mp.ls()

    # ls.pr()
    mesh = oph.mesh
    msepy, obj = ph.fem.apply('msepy', locals())

    print(obj)
