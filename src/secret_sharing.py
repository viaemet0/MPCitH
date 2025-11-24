from dataclasses import dataclass
from typing import List

from .finite_field import Fq
from .group import GroupElement, generate_parameters


@dataclass(frozen=True)
class FieldShare:
    shares: List[Fq]
    q: int

    def reconstruct(self) -> int:
        sum_ = Fq(0, self.q)
        for s in self.shares:
            sum_ += s
        return sum_.value

    def exp(self, g: GroupElement) -> "GroupShare":
        if g.q != self.q:
            raise ValueError(
                "Mismatch between field modulus q and group order q."
            )
        exp_shares = [g**s.value for s in self.shares]
        return GroupShare(exp_shares, g.p, g.q)

    @classmethod
    def additive_secret_sharing(
        cls, secret: int, n: int, q: int
    ) -> "FieldShare":
        if n < 2:
            raise ValueError("Number of shares n must be >= 2.")
        shares = [Fq(0, q) for _ in range(n)]
        sum_ = Fq(0, q)
        for i in range(n - 1):
            shares[i] = Fq.random(q)
            sum_ += shares[i]
        shares[-1] = Fq(secret, q) - sum_
        return cls(shares=shares, q=q)


@dataclass(frozen=True)
class GroupShare:
    shares: List[GroupElement]
    p: int
    q: int

    def product(self) -> GroupElement:
        prod = self.shares[0]
        for s in self.shares[1:]:
            prod = prod * s
        return prod


if __name__ == "__main__":
    params = generate_parameters(8)
    secret = 42
    print(f"g^{secret} = {params.g ** secret}")

    field_shares = FieldShare.additive_secret_sharing(secret, n=5, q=params.q)
    print(f"FieldShare = {field_shares.shares}")
    print(f"reconstruct = {field_shares.reconstruct()}")

    group_shares = field_shares.exp(params.g)
    print(f"GroupShare = {group_shares.shares}")
    prod = group_shares.product()
    print(f"product = {prod}")
    assert prod == params.g**secret
    print("ok")
