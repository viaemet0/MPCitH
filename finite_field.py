import secrets
import galois

_GALOIS_GF_CACHE = {}


def _get_gf(p: int, n: int):
    key = (int(p), int(n))
    gf = _GALOIS_GF_CACHE.get(key)
    if gf is None:
        gf = galois.GF(p**n)
        _GALOIS_GF_CACHE[key] = gf
    return gf


class Fq:
    __slots__ = ("value", "q")

    def __init__(self, value: int, q: int):
        if q < 2:
            raise ValueError("q must be a prime >= 2.")
        self.q = q
        self.value = value % q

    def _check(self, other: "Fq"):
        if not isinstance(other, Fq) or self.q != other.q:
            raise TypeError("Mismatched Fq modulus.")

    def __add__(self, other: "Fq") -> "Fq":
        self._check(other)
        return Fq(self.value + other.value, self.q)

    def __sub__(self, other: "Fq") -> "Fq":
        self._check(other)
        return Fq(self.value - other.value, self.q)

    def __mul__(self, other: "Fq") -> "Fq":
        self._check(other)
        return Fq(self.value * other.value, self.q)

    def __truediv__(self, other: "Fq") -> "Fq":
        self._check(other)
        return self * other.inv()

    def __pow__(self, exp) -> "Fq":
        if isinstance(exp, Fq):
            if exp.q != self.q:
                raise TypeError("Exponent field mismatch.")
            e = exp.value
        elif isinstance(exp, int):
            e = exp
        else:
            raise TypeError("Exponent must be int or Fq.")
        return Fq(pow(self.value, e, self.q), self.q)

    def inv(self) -> "Fq":
        return Fq(pow(self.value, -1, self.q), self.q)

    def __and__(self, other: "Fq") -> "Fq":
        self._check(other)
        return Fq(self.value & other.value, self.q)

    def __or__(self, other: "Fq") -> "Fq":
        self._check(other)
        return Fq(self.value | other.value, self.q)

    def __eq__(self, other) -> bool:
        return (
            isinstance(other, Fq)
            and self.q == other.q
            and self.value == other.value
        )

    def __lt__(self, other) -> bool:
        self._check(other)
        return self.value < other.value

    def __le__(self, other) -> bool:
        self._check(other)
        return self.value <= other.value

    def __gt__(self, other) -> bool:
        self._check(other)
        return self.value > other.value

    def __ge__(self, other) -> bool:
        self._check(other)
        return self.value >= other.value

    def __neg__(self) -> "Fq":
        return Fq(-self.value, self.q)

    def __str__(self):
        return f"{self.value}"

    def __repr__(self):
        return f"Fq({self.value} mod {self.q})"

    def to_bytes(self) -> bytes:
        ln = (self.q.bit_length() + 7) // 8
        return self.value.to_bytes(ln, "big")

    @classmethod
    def random(cls, q: int) -> "Fq":
        return cls(secrets.randbelow(q), q)


class FqN:
    __slots__ = ("coeffs", "p", "modulus", "_g", "_x", "n")

    def __init__(self, value_or_coeffs, p: int, n: int):
        self.p = int(p)
        self.n = int(n)
        if self.p < 2 or self.n < 1:
            raise ValueError("p >= 2 and n >= 1 required.")
        self._g = _get_gf(self.p, self.n)
        if isinstance(value_or_coeffs, int):
            v = int(value_or_coeffs) % (self.p**self.n)
        else:
            v = 0
            pp = 1
            for c in value_or_coeffs:
                v += (int(c) % self.p) * pp
                pp *= self.p
            v %= self.p**self.n
        self._x = self._g(v)

    # F_q -> F_{q^n}
    @classmethod
    def embed(cls, base: "Fq", modulus: int) -> "FqN":
        if not isinstance(base, Fq):
            raise TypeError("embed expects an Fq element.")
        p = base.q
        return cls(base.value, p, int(modulus))

    @classmethod
    def zero(cls, p: int, n: int) -> "FqN":
        return cls(0, p, n)

    @classmethod
    def one(cls, p: int, n: int) -> "FqN":
        return cls(1, p, n)

    @classmethod
    def random(cls, p: int, modulus) -> "FqN":
        if isinstance(modulus, int):
            n = int(modulus)
            coeffs = [secrets.randbelow(p) for _ in range(n)]
            return cls(coeffs, p, n)
        raise TypeError

    def _check(self, other: "FqN"):
        if not isinstance(other, FqN) or self.p != other.p or self.n != other.n:
            raise TypeError("Mismatched FqN field parameters.")

    def __eq__(self, other) -> bool:
        return (
            isinstance(other, FqN)
            and self.p == other.p
            and self.n == other.n
            and int(self._x) == int(other._x)
        )

    def __neg__(self) -> "FqN":
        return FqN(int(-self._x), self.p, self.n)

    def __add__(self, other: "FqN") -> "FqN":
        self._check(other)
        return FqN(int(self._x + other._x), self.p, self.n)

    def __sub__(self, other: "FqN") -> "FqN":
        self._check(other)
        return FqN(int(self._x - other._x), self.p, self.n)

    def __mul__(self, other) -> "FqN":
        if isinstance(other, FqN):
            self._check(other)
            return FqN(int(self._x * other._x), self.p, self.n)
        if isinstance(other, Fq):
            if other.q != self.p:
                raise TypeError("Base field mismatch.")
            return FqN(int(self._x * self._g(other.value)), self.p, self.n)
        if isinstance(other, int):
            return FqN(
                int(self._x * self._g(other % (self.p**self.n))), self.p, self.n
            )
        raise TypeError("Unsupported multiplicand type.")

    def __truediv__(self, other) -> "FqN":
        if isinstance(other, FqN):
            self._check(other)
            return FqN(int(self._x / other._x), self.p, self.n)
        if isinstance(other, Fq):
            if other.q != self.p:
                raise TypeError("Base field mismatch.")
            return FqN(int(self._x / self._g(other.value)), self.p, self.n)
        if isinstance(other, int):
            return FqN(
                int(self._x / self._g(other % (self.p**self.n))), self.p, self.n
            )
        raise TypeError("Unsupported divisor type.")

    def inv(self) -> "FqN":
        if not self:
            raise ZeroDivisionError("inverse of zero")
        return FqN(int(self._x**-1), self.p, self.n)

    def __pow__(self, exp) -> "FqN":
        if not isinstance(exp, int):
            raise TypeError("Exponent must be int.")
        return FqN(int(self._x**exp), self.p, self.n)

    def to_bytes(self) -> bytes:
        q = self.p**self.n
        ln = (q.bit_length() + 7) // 8
        return int(self._x).to_bytes(ln, "big")

    def __repr__(self):
        return f"FqN(p={self.p}, n={self.n}, value={int(self._x)})"

    def __str__(self):
        return f"{int(self._x)}"
