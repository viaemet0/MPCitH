import secrets


class Fq:
    __slots__ = ("value", "q")

    def __init__(self, value: int, q: int):
        if q < 3:
            raise ValueError("q must be a prime >= 3.")
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
        return isinstance(other, Fq) and self.q == other.q and self.value == other.value

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
