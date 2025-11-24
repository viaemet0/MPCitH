from dataclasses import dataclass
from typing import List

from .finite_field import Fq, FqN
from .mq_problem import MqProblem


@dataclass(frozen=True)
class MQMPCParameter:
    q: int = 31  # Size of the base field F_q
    m: int = 49  # Number of unkowns
    n: int = 49  # Number of equations
    security_parameter_lambda: int = 128  # Security parameter
    N: int = 256  # Number of parties (number of shares)
    n1: int = 5  # Number of coordinates per chunks of x and w
    n2: int = 10  # Number of chunks in x and w
    eta: int = (
        10  # Extension degree for the field F_{q^eta} used in the MPC protocol
    )
    tau: int = 20  # Number of repetitions


def _dot_fq(row: List[Fq], x: List[Fq]) -> Fq:
    acc = Fq(0, row[0].q)
    for a, b in zip(row, x):
        acc += a * b
    return acc


def _mat_vec_fq(M: List[List[Fq]], x: List[Fq]) -> List[Fq]:
    n = len(x)
    if len(M) != n or any(len(rc) != n for rc in M):
        raise ValueError("A_i must be an n * n matrix")
    q = x[0].q
    result = [Fq(0, q) for _ in range(n)]
    for r in range(n):
        acc = Fq(0, q)
        row = M[r]
        for c in range(n):
            acc += row[c] * x[c]
        result[r] = acc
    return result


def compute_z_w(mq: MqProblem, param: MQMPCParameter):
    """
    z = sum_{i=1}^m gamma_i * (y_i - b_i^T x), with gamma_i in F_{q^eta}
    w = (sum_{i=1}^m gamma_i A_i) * x  in (F_{q^eta})^n
    """
    x: List[Fq] = mq.x
    y: List[Fq] = mq.y
    A: List[List[List[Fq]]] = mq.A
    b: List[List[Fq]] = mq.b

    q, eta = param.q, param.eta
    m, n = len(y), len(x)

    if len(b) != m or len(A) != m:
        raise ValueError("len(b) and len(A) must equal len(y)")
    if any(len(row) != n for row in b):
        raise ValueError("Each b[i] must have length len(x)")

    gamma = [FqN.random(q, eta) for _ in range(m)]
    z = FqN.zero(q, eta)
    w = [FqN.zero(q, eta) for _ in range(n)]

    for i in range(m):
        yi_minus_btx: Fq = y[i] - _dot_fq(b[i], x)
        z = z + gamma[i] * FqN.embed(yi_minus_btx, eta)

        u_i: List[Fq] = _mat_vec_fq(A[i], x)
        for j in range(n):
            w[j] = w[j] + gamma[i] * FqN.embed(u_i[j], eta)

    return z, w


def main():
    param = MQMPCParameter(
        q=31,
        m=4,
        n=3,
        security_parameter_lambda=128,
        N=3,
        n1=5,
        n2=10,
        eta=10,
        tau=20,
    )
    mq = MqProblem(n=param.n, m=param.m, q=param.q)
    z, w = compute_z_w(mq, param)
    print(f"z: {z}")
    print(f"w: {w}")

    xw = FqN.zero(param.q, param.eta)
    for x_element, w_element in zip(mq.x, w):
        xw += FqN.embed(x_element, param.eta) * w_element
    assert z == xw


if __name__ == "__main__":
    main()
