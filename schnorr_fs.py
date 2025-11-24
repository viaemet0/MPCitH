import hashlib
from dataclasses import dataclass

from finite_field import Fq
from group import GroupElement, Parameters, generate_parameters


@dataclass(frozen=True)
class KeyPair:
    x: Fq  # x: secret key
    y: GroupElement  # g^x: public key


@dataclass(frozen=True)
class Signature:
    u: GroupElement
    c: Fq
    z: Fq


def int_to_bytes(x: int, length: int) -> bytes:
    return x.to_bytes(length, "big")


def encode_element(params: Parameters, g: GroupElement) -> bytes:
    return int_to_bytes(g.value, params.p_len)


def encode_message(m: bytes) -> bytes:
    # length (4 bytes) + data
    if len(m) > 2**32 - 1:
        raise ValueError("Message too long.")
    return len(m).to_bytes(4, "big") + m


def compute_challenge(
    params: Parameters,
    y: GroupElement,
    u: GroupElement,
    m: bytes,
    hash_fn=hashlib.sha256,
) -> Fq:
    """
    c = H(p || q || g || y || u || len(m)||m ) mod q
    """
    h = hash_fn()
    h.update(int_to_bytes(params.p, params.p_len))
    h.update(int_to_bytes(params.q, params.q_len))
    h.update(encode_element(params, params.g))
    h.update(encode_element(params, y))
    h.update(encode_element(params, u))
    h.update(encode_message(m))
    digest = h.digest()
    c_int = int.from_bytes(digest, "big") % params.q

    return Fq(c_int, params.q)


def keygen(params: Parameters) -> KeyPair:
    x = Fq.random(params.q)
    y = params.g**x
    return KeyPair(x=x, y=y)


def sign(
    params: Parameters, x: Fq, y: GroupElement, message: bytes
) -> Signature:
    """
    Schnorr→FS変換→署名:
      1) r ←$ Z_q
      2) u = g^r
      3) c = H(..., u, message)
      4) z = r + c * x mod q
      署名: (u, c, z)
    """
    r = Fq.random(params.q)
    u = params.g**r
    c = compute_challenge(params, y, u, message)
    z = r + c * x
    return Signature(u=u, c=c, z=z)


def verify(
    params: Parameters, y: GroupElement, message: bytes, sig: Signature
) -> bool:
    c2 = compute_challenge(params, y, sig.u, message)
    if sig.c != c2:
        return False
    return params.g**sig.z == sig.u * (y**c2)


if __name__ == "__main__":
    params = generate_parameters(q_bits=160)
    kp = keygen(params)
    print(f"公開鍵 y = {kp.y.value}")

    message = b"Hello Schnorr"
    print(f"メッセージ = {message}")

    sig = sign(params, kp.x, kp.y, message)
    print(f"署名: (u={sig.u.value}, c={sig.c.value}, z={sig.z.value})")

    assert verify(params, kp.y, message, sig)
