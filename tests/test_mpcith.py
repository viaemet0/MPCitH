import pytest

from src.group import generate_parameters
from src.mpcith import KeyPair, keygen, sign, verify_signature


@pytest.fixture(scope="module")
def params():
    """テスト全体で使い回すパラメータ（計算コスト削減）"""
    return generate_parameters(q_bits=16)


@pytest.fixture(scope="module")
def key_pair(params) -> KeyPair:
    """テスト用の鍵ペア"""
    return keygen(params)


def test_sign_and_verify_success(params, key_pair):
    """正しい署名が検証を通過"""
    message = b"Test Message for MPC"
    n = 5  # パーティ数
    m = 20  # 繰り返し回数

    # 署名
    signature = sign(
        message=message, secret_val=key_pair.secret, params=params, n=n, m=m
    )

    # 検証
    is_valid = verify_signature(
        sig=signature, message=message, params=params, y=key_pair.public
    )

    assert is_valid is True


def test_verify_fails_with_wrong_message(params, key_pair):
    """メッセージが改ざんされた場合に検証失敗"""
    message = b"Original Message"
    n = 5
    m = 10

    signature = sign(message, key_pair.secret, params, n, m)

    wrong_message = b"Tampered Message"
    is_valid = verify_signature(
        signature, wrong_message, params, key_pair.public
    )

    assert is_valid is False


def test_verify_fails_with_wrong_key(params, key_pair):
    """違う公開鍵で検証した場合に失敗"""
    message = b"Hello"
    n = 5
    m = 10

    signature = sign(message, key_pair.secret, params, n, m)

    # 別の公開鍵を生成
    other_key_pair = keygen(params)

    is_valid = verify_signature(
        signature, message, params, other_key_pair.public
    )

    assert is_valid is False
