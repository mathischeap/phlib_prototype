# -*- coding: utf-8 -*-
"""
pH-lib@RAM-EEMCS-UT
created at: 3/8/2023 12:05 PM
"""
import sys

if './' not in sys.path:
    sys.path.append('./')

from src.tools.frozen import Frozen
from typing import Dict
import matplotlib.pyplot as plt
import matplotlib
plt.rcParams.update({
    "text.usetex": True,
    "font.family": "DejaVu Sans",
    "text.latex.preamble": r"\usepackage{amsmath}"
})
matplotlib.use('TkAgg')

from src.config import _global_lin_repr_setting
from src.config import _parse_lin_repr
from src.form.operators import wedge
from src.config import _check_sym_repr
from src.form.parameters import constant_scalar
from src.config import _global_operator_lin_repr_setting
from src.config import _global_operator_sym_repr_setting

_global_forms = dict()
_global_root_forms_lin_dict = dict()
_global_form_variables = {
    'update_cache': True
}


class Form(Frozen):
    """The form class."""

    def __init__(
            self, space,
            sym_repr, lin_repr,
            is_root,
            orientation,
    ):
        if is_root is None:  # we will parse is_root from lin_repr
            assert isinstance(lin_repr, str) and len(lin_repr) > 0, f"lin_repr={lin_repr} illegal."
            is_root, lin_repr = self._parse_is_root(lin_repr)
        else:
            pass
        assert isinstance(is_root, bool), f"is_root must be bool."
        self._space = space

        if is_root:  # we check the `sym_repr` only for root forms.
            lin_repr, self._pure_lin_repr = _parse_lin_repr('form', lin_repr)
            for form_id in _global_forms:
                form = _global_forms[form_id]
                assert sym_repr != form._sym_repr, \
                    f"root form symbolic representation={sym_repr} is taken. Pls use another one."
                assert lin_repr != form._lin_repr, \
                    f"root form linguistic representation={lin_repr} is taken. Pls use another one."
        else:
            self._pure_lin_repr = None

        sym_repr = _check_sym_repr(sym_repr)
        self._sym_repr = sym_repr
        self._lin_repr = lin_repr
        self._is_root = is_root
        self._efs = None   # elementary elements
        assert orientation in ('inner', 'outer', 'i', 'o', None, 'None'), \
            f"orientation={orientation} is wrong, must be one of ('inner', 'outer', 'i', 'o', None)."
        if orientation == 'i':
            orientation = 'inner'
        elif orientation == 'o':
            orientation = 'outer'
        elif orientation is None:
            orientation = 'None'
        else:
            pass
        self._orientation = orientation
        if _global_form_variables['update_cache']:  # cache it
            _global_forms[id(self)] = self
            if self._is_root:
                _global_root_forms_lin_dict[self._lin_repr] = self
            else:
                pass
        else:
            pass
        self._pAti_form: Dict = {
            'base_form': None,
            'ats': None,
            'ati': None
        }
        self._abstract_forms = dict()   # the abstract forms based on this form.
        self._freeze()

    @staticmethod
    def _parse_is_root(lin_repr):
        """Study is_root through lin_repr."""
        try:
            _parse_lin_repr('form', lin_repr)
        except Exception:
            pass
        else:
            return True, lin_repr

        start, end = _global_lin_repr_setting['form']

        if lin_repr[:len(start)] == start and lin_repr[-len(end):] == end:

            try:
                _parse_lin_repr('form', lin_repr[len(start):-len(end)])
            except Exception:
                return False, lin_repr
            else:
                return True, lin_repr[len(start):-len(end)]

        else:
            return False, lin_repr

    def print_representations(self):
        """Print this form with matplotlib and latex."""
        my_id = r'\texttt{' + str(id(self)) + '}'
        if self._pAti_form['base_form'] is None:
            pti_text = ''
        else:
            base_form, ats, ati = self._pAti_form['base_form'], self._pAti_form['ats'], self._pAti_form['ati']
            pti_text = rf"\\(${base_form._sym_repr}$ at abstract time instant ${ati._sym_repr}$"
        space_text = f'spaces: ${self.space._sym_repr}$'
        space_text += rf"\ \ \ \ on ({self.mesh._lin_repr})"
        plt.figure(figsize=(3 + len(self._sym_repr)/4, 4))
        plt.axis([0, 1, 0, 5])
        plt.text(0, 4.5, f'form id: {my_id}', ha='left', va='center', size=15)
        plt.text(0, 3.5, space_text, ha='left', va='center', size=15)
        plt.text(0, 2.5, rf'\noindent symbolic : ' + f"${self._sym_repr}$" + pti_text, ha='left', va='center', size=15)
        plt.text(0, 1.5, 'linguistic : ' + self._lin_repr, ha='left', va='center', size=15)
        root_text = rf'is_root: {self.is_root()}'
        plt.text(0, 0.5, root_text, ha='left', va='center', size=15)
        plt.axis('off')
        plt.show()

    def print(self):
        """A wrapper of print_representations"""
        return self.print_representations()

    def __repr__(self):
        """"""
        super_repr = super().__repr__().split('object')[-1]
        return '<Form ' + self._sym_repr + super_repr  # this will be unique.

    @property
    def elementary_forms(self):
        """parse the elementary_forms from the linguistic representation only. A texting solution only!"""
        if self._efs is None:
            efs = list()
            for root_lin_repr in _global_root_forms_lin_dict:
                if root_lin_repr in self._lin_repr:
                    efs.append(_global_root_forms_lin_dict[root_lin_repr])
            self._efs = set(efs)
        return self._efs

    @property
    def orientation(self):
        """The orientation of this form."""
        return self._orientation

    def is_root(self):
        """Return True this form is a root form."""
        return self._is_root

    @property
    def space(self):
        """The space this form is in."""
        return self._space

    @property
    def mesh(self):
        """The mesh this form is on."""
        return self.space.mesh

    def wedge(self, other):
        """Return a form representing `self` wedge `other`."""
        return wedge(self, other)

    def __neg__(self):
        """- self"""
        raise NotImplementedError()

    def __add__(self, other):
        """self + other"""
        if other.__class__.__name__ == 'Form':
            assert other.mesh == self.mesh, f"mesh does not match."
            assert self.orientation == other.orientation
            assert self.space == other.space
            self_lr = self._lin_repr
            self_sr = self._sym_repr
            other_lr = other._lin_repr
            other_sr = other._sym_repr

            operator_lin = _global_operator_lin_repr_setting['plus']
            operator_sym = _global_operator_sym_repr_setting['plus']

            lin_repr = self_lr + operator_lin + other_lr
            sym_repr = self_sr + operator_sym + other_sr

            f = Form(
                self.space,  # space
                sym_repr,          # symbolic representation
                lin_repr,          # linguistic representation
                False,       # must not be a root-form anymore.
                self.orientation,
            )
            return f

        else:
            raise NotImplementedError(f"{other}")

    def __sub__(self, other):
        """self-other"""
        if other.__class__.__name__ == 'Form':
            assert other.mesh == self.mesh, f"mesh does not match."
            assert self.orientation == other.orientation
            assert self.space == other.space
            self_lr = self._lin_repr
            self_sr = self._sym_repr
            other_lr = other._lin_repr
            other_sr = other._sym_repr

            operator_lin = _global_operator_lin_repr_setting['minus']
            operator_sym = _global_operator_sym_repr_setting['minus']

            lin_repr = self_lr + operator_lin + other_lr
            sym_repr = self_sr + operator_sym + other_sr

            f = Form(
                self.space,  # space
                sym_repr,          # symbolic representation
                lin_repr,          # linguistic representation
                False,       # must not be a root-form anymore.
                self.orientation,
            )
            return f

        else:
            raise NotImplementedError(f"{other}")

    def __mul__(self, other):
        """self * other"""
        raise NotImplementedError()

    def __rmul__(self, other):
        """other * self"""
        raise NotImplementedError()

    def __truediv__(self, other):
        """self / other"""
        operator_lin = _global_operator_lin_repr_setting['divided']
        if isinstance(other, (int, tuple)):
            cs = constant_scalar(other)
            return self / cs

        elif other.__class__.__name__ == 'AbstractTimeInterval':
            ati = other
            return self / ati._as_scalar()

        elif other.__class__.__name__ == 'ConstantScalar0Form':
            lr = self._lin_repr
            sr = self._sym_repr
            cs = other
            if self.is_root():
                lr = lr + operator_lin + cs._lin_repr
            else:
                lr = '[' + lr + ']' + operator_lin + cs._lin_repr
            sr = r"\dfrac{" + sr + r"}{" + cs._sym_repr + "}"
            f = Form(
                self.space,  # space
                sr,          # symbolic representation
                lr,          # linguistic representation
                False,       # not a root-form anymore.
                self.orientation,
            )
            return f

        else:
            raise NotImplementedError(f"form divided by <{other.__class__.__name__}> is not implemented.")

    def _evaluate_at(self, other):
        """evaluate_at"""
        if other.__class__.__name__ == 'AbstractTimeInstant':
            ati = other
            assert self.is_root(), f"Can only evaluate a root form at an abstract time instant."
            sym_repr = self._sym_repr
            lin_repr = self._pure_lin_repr
            sym_repr = r"\left." + sym_repr + r"\right|^{(" + ati.k + ')}'
            lin_repr += "@" + ati._pure_lin_repr

            if lin_repr in self._abstract_forms:   # we must cache it, this is very important.
                pass
            else:
                ftk = Form(
                    self._space,
                    sym_repr, lin_repr,
                    self._is_root,
                    self._orientation,
                )
                ftk._pAti_form['base_form'] = self
                ftk._pAti_form['ats'] = ati.time_sequence
                ftk._pAti_form['ati'] = ati
                self._abstract_forms[lin_repr] = ftk

            return self._abstract_forms[lin_repr]

        else:
            raise NotImplementedError(f"Cannot evaluate {self} at {other}.")

    def __matmul__(self, other):
        """self @ other"""
        return self._evaluate_at(other)

    def replace(self, f, by, which='all'):
        """replace `which` `f` by `by`."""
        assert by.space == f.space, f"spaces do not match."
        if f._lin_repr not in self._lin_repr:
            return self
        elif self._lin_repr == f._lin_repr:
            return by

        else:
            if which == 'all':
                lin_repr = self._lin_repr.replace(f._lin_repr, by._lin_repr)
                sym_repr = self._sym_repr.replace(f._sym_repr, by._sym_repr)
            else:
                raise NotImplementedError()

            return Form(
                self.space,
                sym_repr,
                lin_repr,
                None,
                self.orientation
            )

    def reform(self, into):
        """reform self into `forms`."""
        raise NotImplementedError()
