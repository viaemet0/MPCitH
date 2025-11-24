from dataclasses import dataclass, field
from itertools import combinations_with_replacement
from typing import Dict, List, Tuple

from .finite_field import Fq

Monomial = Tuple[int, ...]


@dataclass(frozen=True)
class MpProblem:
    n: int
    m: int
    q: int
    deg: int = 1
    x: List[Fq] = field(init=False)
    coeffs: List[Dict[Monomial, Fq]] = field(init=False)
    d: List[Fq] = field(init=False)

    def __post_init__(self):
        if self.deg < 1:
            raise ValueError("deg must be >= 1.")
        object.__setattr__(self, "x", self._gen_x())
        object.__setattr__(self, "coeffs", self._gen_coeffs())
        object.__setattr__(self, "d", self._evaluate_d())

    def _gen_x(self) -> List[Fq]:
        return [Fq.random(self.q) for _ in range(self.n)]

    def _monomials(self) -> List[Monomial]:
        monos: List[Monomial] = [()]  # () -> 定数項
        for d in range(1, self.deg + 1):
            monos.extend(combinations_with_replacement(range(self.n), d))
        return monos

    def _gen_coeffs(self) -> List[Dict[Monomial, Fq]]:
        monos = self._monomials()
        polys: List[Dict[Monomial, Fq]] = []
        for _ in range(self.m):
            poly: Dict[Monomial, Fq] = {}
            for mono in monos:
                poly[mono] = Fq.random(self.q)
            polys.append(poly)
        return polys

    def _evaluate_d(self):
        res: List[Fq] = []
        for poly in self.coeffs:
            acc = Fq(0, self.q)
            for mono, c in poly.items():
                if c.value == 0:
                    continue
                for idx in mono:
                    c *= self.x[idx]
                acc += c
            res.append(acc)
        return res

    def _poly_to_str(self, poly: Dict[Monomial, Fq]) -> str:
        terms = []
        for mono, c in poly.items():
            if c.value == 0:
                continue
            if len(mono) == 0:  # 定数項
                terms.append(f"{c.value}")
                continue
            vars_part = "*".join(f"x{idx+1}" for idx in mono)
            if c.value == 1:
                terms.append(vars_part)
            else:
                terms.append(f"{c.value}*{vars_part}")
        if not terms:
            return "0"

        return " + ".join(terms)

    def mq_to_matrix_vector(self):
        """
        x A_i x^T + x b_i^T = y_i
        """
        if not self.is_mq:
            raise ValueError("only for MQ problem (deg=2).")

        forms = []
        for poly, yi in zip(self.coeffs, self.d):
            A = [[Fq(0, self.q) for _ in range(self.n)] for _ in range(self.n)]
            b = [Fq(0, self.q) for _ in range(self.n)]
            c = Fq(0, self.q)
            for mono, coeff in poly.items():
                if coeff.value == 0:
                    continue
                deg = len(mono)
                if deg == 0:
                    c += coeff
                elif deg == 1:  # to b vector
                    i = mono[0]  # mono = (i,)
                    b[i] += coeff
                elif deg == 2:  # to A matrix
                    i, j = mono  # mono = (i, j) with i <= j
                    if i == j:  # x_i^2
                        A[i][i] += coeff
                    else:  # x_i * x_j
                        if i < j:
                            A[i][j] += coeff  # A[i][j] + A[j][i] = coeff + 0
                        else:
                            # raise RuntimeError("not expected")
                            A[j][i] += coeff  # A[i][j] + A[j][i] = 0 + coeff
                else:
                    raise ValueError("deg should be <= 2.")
            # x A x^T + x b^T = y  (y = yi - c)
            y_no_const = yi - c
            forms.append({"A": A, "b": b, "c": c, "y": y_no_const})
        return forms

    def pretty_matrix_form(self) -> str:
        if not self.is_mq:
            return ""

        lines = ["Matrix form:"]
        forms = self.mq_to_matrix_vector()
        for idx, f in enumerate(forms, 1):  # idx: [1, m]
            deg2 = []
            A = f["A"]
            b = f["b"]
            y = f["y"]
            for i in range(self.n):
                if A[i][i].value != 0:
                    deg2.append(f"{A[i][i].value}*x{i+1}^2")
                for j in range(i + 1, self.n):
                    if A[i][j].value != 0:
                        deg2.append(f"{A[i][j].value}*x{i+1}*x{j+1}")
            deg1 = [
                f"{b[i].value}*x{i+1}" for i in range(self.n) if b[i].value != 0
            ]
            expr = " + ".join(deg2 + deg1) if (deg2 or deg1) else "0"
            lines.append(
                f"x A{idx} x^T + x b{idx}^T = {y.value}\t (where: {expr})"
            )
        return ("\n" + " " * 4).join(lines)

    def __repr__(self) -> str:
        problem_text = f"{'MQ' if self.is_mq else 'MP'} Problem(n={self.n}, m={self.m}, q={self.q}, deg={self.deg})"
        var_list = ", ".join(f"x{i+1}" for i in range(self.n))
        lines = [
            problem_text + f", Variables: ({var_list}) in F_{self.q}^{self.n}"
        ]
        for i, (poly, di) in enumerate(zip(self.coeffs, self.d), start=1):
            poly_str = self._poly_to_str(poly)
            lines.append(
                f"p{i}({var_list}) = {di.value}\t (where: p{i}(x) = {poly_str})"
            )
        base = ("\n" + " " * 4).join(lines)
        if self.is_mq:
            matrix_part = self.pretty_matrix_form()
            if matrix_part:
                return base + "\n" + matrix_part
        return base

    @property
    def is_linear(self) -> bool:
        return self.deg == 1  # 線形

    @property
    def is_mq(self) -> bool:
        return self.deg == 2  # MQ


class MqProblem(MpProblem):
    def __init__(self, n: int, m: int, q: int):
        super().__init__(n=n, m=m, q=q, deg=2)
        self.A: List[List[List[Fq]]] = []
        self.b: List[List[Fq]] = []
        self.y: List[Fq] = []
        forms = self.mq_to_matrix_vector()
        for f in forms:
            self.A.append(f["A"])
            self.b.append(f["b"])
            self.y.append(f["y"])


if __name__ == "__main__":
    # 線形
    # mp_linear = MpProblem(n=5, m=3, q=31, deg=1)
    # print(mp_linear)

    # MQ
    mq = MqProblem(n=2, m=4, q=31)
    print(mq)

    # 3次
    # mp_cubic = MpProblem(n=3, m=2, q=31, deg=3)
    # print(mp_cubic)
