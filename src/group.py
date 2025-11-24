import secrets
from dataclasses import dataclass

from sympy import isprime, randprime

from .finite_field import Fq


class GroupElement:
    __slots__ = ("value", "p", "q")

    def __init__(self, value: int, p: int, q: int):
        self.p = p
        self.q = q
        self.value = value % p

    def _check(self, other: "GroupElement"):
        if (
            not isinstance(other, GroupElement)
            or self.p != other.p
            or self.q != other.q
        ):
            raise TypeError("Group mismatch.")

    def __mul__(self, other: "GroupElement") -> "GroupElement":
        self._check(other)
        return GroupElement((self.value * other.value) % self.p, self.p, self.q)

    def __pow__(self, exp) -> "GroupElement":
        if isinstance(exp, Fq):
            if exp.q != self.q:
                raise TypeError("Exponent Fq mismatch.")
            e = exp.value
        elif isinstance(exp, int):
            e = exp % self.q
        else:
            raise TypeError("Exponent must be int or Fq.")
        return GroupElement(pow(self.value, e, self.p), self.p, self.q)

    def __eq__(self, other) -> bool:
        return (
            isinstance(other, GroupElement)
            and self.p == other.p
            and self.q == other.q
            and self.value == other.value
        )

    def __str__(self):
        return f"{self.value}"

    def __repr__(self):
        return f"GroupElement({self.value} mod {self.p})"


@dataclass(frozen=True)
class Parameters:
    p: int
    q: int
    g: GroupElement
    p_len: int
    q_len: int


def generate_parameters(q_bits: int = 256, max_k: int = 2**32) -> Parameters:
    if q_bits < 8:
        raise ValueError("q_bits should be >= 8.")
    q = int(randprime(2 ** (q_bits - 1), 2**q_bits))  # type: ignore
    while True:
        k = secrets.randbelow(max_k) + 2
        p = k * q + 1
        if isprime(p):
            break
    while True:
        a = secrets.randbelow(p - 3) + 2
        g_val = pow(a, k, p)
        if g_val != 1:
            g = GroupElement(g_val, p, q)
            break
    p_len = (p.bit_length() + 7) // 8
    q_len = (q.bit_length() + 7) // 8
    return Parameters(p=p, q=q, g=g, p_len=p_len, q_len=q_len)
