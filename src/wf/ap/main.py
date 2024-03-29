# -*- coding: utf-8 -*-
"""
@author: Yi Zhang
@contact: zhangyi_aero@hotmail.com
@time: 11/26/2022 2:56 PM
"""
import sys

if './' not in sys.path:
    sys.path.append('./')
import matplotlib.pyplot as plt
import matplotlib
plt.rcParams.update({
    "text.usetex": True,
    "font.family": "DejaVu Sans",
    "text.latex.preamble": r"\usepackage{amsmath, amssymb}",
})
matplotlib.use('TkAgg')

from src.tools.frozen import Frozen


class AlgebraicProxy(Frozen):
    """"""

    def __init__(self, wf):
        self._parse_terms(wf)
        self._parse_unknowns_test_vectors(wf)
        self._wf = wf
        self._bc = wf._bc
        self._evs = None
        self._freeze()

    def _parse_terms(self, wf):
        """"""
        wf_td = wf._term_dict
        wf_sd = wf._sign_dict
        term_dict = dict()   # the terms for the AP equation
        sign_dict = dict()   # the signs for the AP equation
        ind_dict = dict()
        indexing = dict()
        linear_dict = dict()
        self._is_linear = True
        for i in wf_td:
            term_dict[i] = ([], [])
            sign_dict[i] = ([], [])
            ind_dict[i] = ([], [])
            linear_dict[i] = ([], [])
            k = 0
            for j, terms in enumerate(wf_td[i]):
                for m, term in enumerate(terms):
                    old_sign = wf_sd[i][j][m]
                    try:
                        ap, new_sign = term.ap(test_form=wf.test_forms[i])
                        new_sign = self._parse_sign(new_sign, old_sign)

                        if ap._is_linear():
                            linear = True
                        else:
                            linear = False
                            self._is_linear = False

                    except NotImplementedError:

                        ap = term
                        new_sign = old_sign
                        linear = 'unknown'
                        self._is_linear = False

                    index = str(i) + '-' + str(k)
                    k += 1
                    indexing[index] = (new_sign, ap)
                    ind_dict[i][j].append(index)
                    term_dict[i][j].append(ap)
                    sign_dict[i][j].append(new_sign)
                    linear_dict[i][j].append(linear)

        self._term_dict = term_dict
        self._sign_dict = sign_dict
        self._indexing = indexing
        self._ind_dict = ind_dict
        self._linear_dict = linear_dict

    def is_linear(self):
        """If we have a linear system?"""
        return self._is_linear

    @staticmethod
    def _parse_sign(s0, s1):
        """parse sign"""
        return '+' if s0 == s1 else '-'

    def _parse_unknowns_test_vectors(self, wf):
        """parse unknowns test vectors."""
        assert wf.unknowns is not None, f"pls first set unknowns of the weak formulation."
        assert wf.test_forms is not None, f"Weak formulation should have specify test forms."

        self._unknowns = list()
        for wfu in wf.unknowns:
            self._unknowns.append(wfu._ap)

        self._tvs = list()
        for tf in wf.test_forms:
            self._tvs.append(tf._ap)

    @property
    def unknowns(self):
        """unknowns"""
        return self._unknowns

    @property
    def test_vectors(self):
        """test vectors."""
        return self._tvs

    @property
    def elementary_vectors(self):
        """elementary vectors."""
        if self._evs is None:
            self._evs = list()
            for ef in self._wf.elementary_forms:
                self._evs.append(ef.ap())
            self._evs = tuple(self._evs)
        return self._evs

    def pr(self, indexing=True):
        """Print the representations"""
        seek_text = self._wf._mesh.manifold._manifold_text()
        seek_text += r'seek $\left('
        form_sr_list = list()
        space_sr_list = list()
        for un in self.unknowns:
            form_sr_list.append(rf' {un._sym_repr}')
            space_sr_list.append(rf"{un._shape_text()}")
        seek_text += ','.join(form_sr_list)
        seek_text += r'\right) \in '
        seek_text += r'\times '.join(space_sr_list)
        seek_text += '$, such that\n'
        symbolic = ''
        number_equations = len(self._term_dict)
        for i in self._term_dict:
            for t, terms in enumerate(self._term_dict[i]):
                if len(terms) == 0:
                    symbolic += '0'
                else:

                    for j, term in enumerate(terms):
                        sign = self._sign_dict[i][t][j]
                        term = self._term_dict[i][t][j]

                        term_sym_repr = term._sym_repr

                        if indexing:
                            index = self._ind_dict[i][t][j].replace('-', r'\text{-}')
                            term_sym_repr = r'\underbrace{' + term_sym_repr + r'}_{' + \
                                rf"{index}" + '}'
                        else:
                            pass

                        if j == 0:
                            if sign == '+':
                                symbolic += term_sym_repr
                            elif sign == '-':
                                symbolic += '-' + term_sym_repr
                            else:
                                raise Exception()
                        else:
                            symbolic += ' ' + sign + ' ' + term_sym_repr

                if t == 0:
                    symbolic += ' &= '

            symbolic += r'\quad &&\forall ' + \
                        self.test_vectors[i]._sym_repr + \
                        r'\in' + \
                        self.test_vectors[i]._shape_text()

            if i < number_equations - 1:
                symbolic += r',\\'
            else:
                symbolic += '.'

        symbolic = r"$\left\lbrace\begin{aligned}" + symbolic + r"\end{aligned}\right.$"
        if self._bc is None or len(self._bc) == 0:
            bc_text = ''
        else:
            bc_text = self._bc._bc_text()

        if indexing:
            figsize = (12, 3 * len(self._term_dict))
        else:
            figsize = (12, 3 * len(self._term_dict))

        plt.figure(figsize=figsize)
        plt.axis([0, 1, 0, 1])
        plt.axis('off')
        plt.text(0.05, 0.5, seek_text + '\n' + symbolic + bc_text, ha='left', va='center', size=15)
        plt.tight_layout()
        plt.show()


if __name__ == '__main__':
    # python src/wf/ap/rct.py
    import __init__ as ph

    samples = ph.samples

    oph = samples.pde_canonical_pH(n=3, p=3)[0]
    a3, b2 = oph.unknowns
    # oph.pr()

    a31 = a3 @ 1

    # wf = oph.test_with(oph.unknowns, sym_repr=[r'v^3', r'u^2'])
    # wf = wf.derive.integration_by_parts('1-1')
    # # wf.pr(indexing=True)
    #
    # td = wf.td
    # td.set_time_sequence()  # initialize a time sequence
    #
    # td.define_abstract_time_instants('k-1', 'k-1/2', 'k')
    # td.differentiate('0-0', 'k-1', 'k')
    # td.average('0-1', b2, ['k-1', 'k'])
    #
    # td.differentiate('1-0', 'k-1', 'k')
    # td.average('1-1', a3, ['k-1', 'k'])
    # td.average('1-2', a3, ['k-1/2'])
    # dt = td.time_sequence.make_time_interval('k-1', 'k')
    #
    # wf = td()
    #
    # # wf.pr()
    #
    # wf.unknowns = [
    #     a3 @ td.time_sequence['k'],
    #     b2 @ td.time_sequence['k'],
    # ]
    #
    # wf = wf.derive.split(
    #     '0-0', 'f0',
    #     [a3 @ td.ts['k'], a3 @ td.ts['k-1']],
    #     ['+', '-'],
    #     factors=[1/dt, 1/dt],
    # )
    #
    # wf = wf.derive.split(
    #     '0-2', 'f0',
    #     [ph.d(b2 @ td.ts['k-1']), ph.d(b2 @ td.ts['k'])],
    #     ['+', '+'],
    #     factors=[1/2, 1/2],
    # )
    #
    # wf = wf.derive.split(
    #     '1-0', 'f0',
    #     [b2 @ td.ts['k'], b2 @ td.ts['k-1']],
    #     ['+', '-'],
    #     factors=[1/dt, 1/dt]
    # )
    #
    # wf = wf.derive.split(
    #     '1-2', 'f0',
    #     [a3 @ td.ts['k-1'], a3 @ td.ts['k']],
    #     ['+', '+'],
    #     factors=[1/2, 1/2],
    # )
    #
    # wf = wf.derive.rearrange(
    #     {
    #         0: '0, 3 = 1, 2',
    #         1: '3, 0 = 2, 1, 4',
    #     }
    # )
    #
    # ph.space.finite(3)
    #
    # # ph.list_spaces()
    #
    # # (a3 @ td.ts['k']).ap(r"\vec{\alpha}")
    #
    # # wf.pr()
    #
    # ap = wf.ap()
    # ap.pr()
    #
    #
    #
    # # ap.pr()
    # # print(wf.unknowns, wf.test_forms)
    # # print(ap.test_vectors)
