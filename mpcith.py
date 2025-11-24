import hashlib
from dataclasses import dataclass
from typing import List, Tuple

from finite_field import Fq
from group import GroupElement, Parameters, generate_parameters
from schnorr_fs import encode_message, int_to_bytes
from secret_sharing import FieldShare


@dataclass(frozen=True)
class MPCitHProof:
    """1ラウンドの証明データ"""

    commits: List[int]
    group_shares: List[GroupElement]
    hidden_party: int
    opened_party: List[Tuple[int, Fq]]  # (index, share)


@dataclass(frozen=True)
class WholeSignature:
    """M回のラウンドを含む全体の署名"""

    proofs: List[MPCitHProof]
    challenge_seed: bytes


def commitment(field_share: Fq, q_len: int) -> int:
    h = hashlib.sha256()
    h.update(int_to_bytes(field_share.value, q_len))
    digest = h.digest()
    return int.from_bytes(digest, "big") % field_share.q


def generate_challenges(seed_data: bytes, m: int, n: int) -> List[int]:
    # ハッシュ値からm個のチャレンジ（隠すパーティのインデックス）を生成
    shake = hashlib.shake_256()
    shake.update(seed_data)
    random_bytes = shake.digest(m)
    return [b % n for b in random_bytes]  # TODO: modulo bias


def verify_signature(
    sig: WholeSignature, message: bytes, params: Parameters, y: GroupElement
) -> bool:
    m = len(sig.proofs)
    if m == 0:
        return False

    h = hashlib.sha256()
    h.update(encode_message(message))

    for proof in sig.proofs:
        for c in proof.commits:
            h.update(int_to_bytes(c, params.q_len))
        for g_elem in proof.group_shares:
            h.update(int_to_bytes(g_elem.value, params.p_len))

    digest = h.digest()

    n = len(sig.proofs[0].commits)
    recomputed_challenges = generate_challenges(digest, m, n)

    for i, proof in enumerate(sig.proofs):
        if proof.hidden_party != recomputed_challenges[i]:
            print(f"Round {i}: Challenge mismatch")
            return False

        if not verify_single_round(proof, params, y):
            print(f"Round {i}: Single proof verification failed")
            return False

    return True


def verify_single_round(
    proof: MPCitHProof, params: Parameters, y: GroupElement
) -> bool:
    n = len(proof.commits)

    # シェアの数が正しいか
    if len(proof.group_shares) != n:
        return False
    # 開示されたパーティ数が正しいか (N-1)
    if len(proof.opened_party) != n - 1:
        return False

    opened_indices = [idx for idx, _ in proof.opened_party]

    # 隠すべきパーティが開示されていないか
    if proof.hidden_party in opened_indices:
        return False
    # インデックスの重複や範囲外チェック
    if len(set(opened_indices)) != n - 1:
        return False

    for idx, share in proof.opened_party:
        if commitment(share, params.q_len) != proof.commits[idx]:
            return False
        expected = params.g**share.value
        if expected != proof.group_shares[idx]:
            return False

    prod = proof.group_shares[0]
    for gs in proof.group_shares[1:]:
        prod = prod * gs
    if prod != y:
        return False

    return True


def sign(
    message: bytes, secret_val: int, params: Parameters, n: int, m: int
) -> WholeSignature:
    """
    message: 署名対象
    secret_val: 秘密鍵x
    n: パーティ数
    m: 繰り返し回数
    """

    all_round_data = []

    for _ in range(m):
        field_shares = FieldShare.additive_secret_sharing(
            secret_val, n=n, q=params.q
        )
        shares: List[Fq] = field_shares.shares

        commits = [commitment(s, params.q_len) for s in shares]

        group_share_obj = field_shares.exp(params.g)
        broadcast_values: List[GroupElement] = group_share_obj.shares

        all_round_data.append(
            {
                "shares": shares,
                "commits": commits,
                "group_shares": broadcast_values,
            }
        )

    # Fiat-Shamir
    h = hashlib.sha256()
    h.update(encode_message(message))

    for data in all_round_data:
        for c in data["commits"]:
            h.update(int_to_bytes(c, params.q_len))
        for g_elem in data["group_shares"]:
            h.update(int_to_bytes(g_elem.value, params.p_len))

    digest = h.digest()

    challenges = generate_challenges(digest, m, n)

    # Response
    proofs = []
    for i in range(m):
        data = all_round_data[i]
        hidden_idx = challenges[i]

        opened_party = [
            (idx, s)
            for idx, s in enumerate(data["shares"])
            if idx != hidden_idx
        ]

        proof = MPCitHProof(
            commits=data["commits"],
            group_shares=data["group_shares"],
            hidden_party=hidden_idx,
            opened_party=opened_party,
        )
        proofs.append(proof)

    return WholeSignature(proofs=proofs, challenge_seed=digest)


if __name__ == "__main__":
    params = generate_parameters(q_bits=16)
    secret = 42
    party_num = 5
    repetition = 50

    y = params.g**secret
    message = b"Hello MPC-in-the-Head"

    print(f"公開鍵 y = {y.value}")
    print(f"メッセージ: {message}")
    sig = sign(message, secret, params, n=party_num, m=repetition)
    print(f"署名の証明数: {len(sig.proofs)}")

    is_valid = verify_signature(sig, message, params, y)
    if is_valid:
        print("署名は有効")
    else:
        print("署名は無効")

    print("--- 改ざん検知 ---")
    is_valid_fake = verify_signature(sig, b"Fake Message", params, y)
    assert not is_valid_fake, "改ざん検知失敗"
    print("改ざん検知成功")
