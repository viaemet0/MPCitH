from typing import List, Dict, Tuple
from dataclasses import dataclass, field
from itertools import combinations_with_replacement
from finite_field import Fq

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

    def __repr__(self) -> str:
        problem_text = f"{'MQ' if self.is_mq else 'MP'} Problem(n={self.n}, m={self.m}, q={self.q}, deg={self.deg})"
        var_list = ", ".join(f"x{i+1}" for i in range(self.n))
        lines = [
            problem_text + f", Variables: ({var_list}) in F_{self.q}^{self.n}"
        ]
        for i, (poly, di) in enumerate(zip(self.coeffs, self.d), start=1):
            poly_str = self._poly_to_str(poly)
            lines.append(
                f"p{i}({var_list}) = {di.value}\t where p{i}(x) = {poly_str}"
            )
        return ("\n" + " " * 4).join(lines)

    @property
    def is_linear(self) -> bool:
        return self.deg == 1  # 線形

    @property
    def is_mq(self) -> bool:
        return self.deg == 2  # MQ


class MqProblem(MpProblem):
    def __init__(self, n: int, m: int, q: int):
        super().__init__(n=n, m=m, q=q, deg=2)


if __name__ == "__main__":
    # 線形
    mp_linear = MpProblem(n=5, m=3, q=31, deg=1)
    print(mp_linear)

    # MQ
    mq = MqProblem(n=2, m=4, q=31)
    print(mq)

    # 3次
    mp_cubic = MpProblem(n=3, m=2, q=31, deg=3)
    print(mp_cubic)
