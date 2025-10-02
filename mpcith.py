from dataclasses import dataclass
from typing import List, Tuple
import secrets
import hashlib
from group import generate_parameters, GroupElement, Parameters
from secret_sharing import FieldShare, GroupShare
from schnorr_fs import int_to_bytes
from finite_field import Fq


@dataclass(frozen=True)
class MPCitHProof:
    commits: List[int]
    group_shares: List[GroupElement]
    hidden_party: int
    opened_party: List[Tuple[int, Fq]]


def commitment(field_share: Fq, q_len: int) -> int:
    h = hashlib.sha256()
    h.update(int_to_bytes(field_share.value, q_len))
    digest = h.digest()
    return int.from_bytes(digest, "big") % field_share.q


def broadcast(group_shares: GroupShare) -> List[GroupElement]:
    # 本来は送信
    return group_shares.shares


def choose_party(n: int) -> int:
    return secrets.randbelow(n)


def verify(proof: MPCitHProof, params: Parameters, y: GroupElement) -> bool:
    n = len(proof.commits)

    if len(proof.group_shares) != n:
        return False
    if len(proof.opened_party) != n - 1:
        return False

    opened_party_indices = [i for i, _ in proof.opened_party]
    if len(set(opened_party_indices)) != len(opened_party_indices):
        return False
    if any(i < 0 or i >= n for i in opened_party_indices):
        return False
    if proof.hidden_party in opened_party_indices:
        return False

    for i, share in proof.opened_party:
        if commitment(share, params.q_len) != proof.commits[i]:
            return False
        expected = params.g**share.value
        if expected != proof.group_shares[i]:
            return False

    prod = proof.group_shares[0]
    for gs in proof.group_shares[1:]:
        prod = prod * gs
    if prod != y:
        return False

    return True


def mpcith_prove(secret: int, params: Parameters, n: int) -> MPCitHProof:
    field_shares = FieldShare.additive_secret_sharing(secret, n=n, q=params.q)
    commits = [commitment(fs, params.q_len) for fs in field_shares.shares]
    group_share_obj = field_shares.exp(params.g)
    hidden_party = choose_party(n)
    opened_party = [
        (i, s) for i, s in enumerate(field_shares.shares) if i != hidden_party
    ]
    return MPCitHProof(
        commits=commits,
        group_shares=broadcast(group_share_obj),
        hidden_party=hidden_party,
        opened_party=opened_party,
    )


if __name__ == "__main__":
    params = generate_parameters(8)
    secret = 42
    party_num = 5
    y = params.g**secret
    print(f"公開値 y = g^{secret} = {y}")
    proof = mpcith_prove(secret, params, party_num)
    print(proof)
    assert verify(proof, params, y)
