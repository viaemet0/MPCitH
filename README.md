# MPC-in-the-Head（MPCitH）

## MPCitH

```bash
python3 mpcith.py
```

MPCitH 証明生成

1. 秘密を加法型秘密分散
2. 各 share をコミット
3. g^{share} を計算し全公開
4. ランダムに 1 パーティ隠し他を開示

MPCitH は、[MPC](#mpc-を仮想的に実行) から構築した[ゼロ知識証明を Fiat-Shamir 変換することで署名方式を構築](#シュノア識別プロトコルschnorrs-identification-protocol)するフレームワークである。

## MPC を仮想的に実行

```bash
python3 secret_sharing.py
```

1. 加法型秘密分散法（Additive Secret Sharing）で秘密 x を`n`個のシェア（`x_1,x_2,...,x_n`）に分散

   `x=x_1+x_2+...+x_n`

2. 巡回群`<g>`の生成元`g`と`i`番目のシェア`x_i`で累乗計算`g^(x_i)`
3. `n`個の`g^(x_i)`の積を求めると、指数部分が加算となり、`g^x`と等しい結果が得られる

   `g^(x_1)*g^(x_2)*...*g^(x_n)=g^(x_1+x_2+...+x_n)=g^x`

## シュノア識別プロトコル（Schnorr’s identification protocol）

```bash
python3 schnorr_fs.py
```

ゼロ知識証明を Fiat-Shamir 変換し、署名とする例

## MQ 問題

```bash
python3 mq_problem.py
```

多変数多項式求解問題（MP 問題; 連立方程式を解くような問題）のうち、すべての項の次数が 2 となるのが「MQ 問題」と呼ばれる。

MPCitH の方式のひとつである[MQ on my Mind (MQOM)](https://mqom.org/)は、この MQ 問題の困難性に基づいている。

## 参考文献

- [https://www.cryptrec.go.jp/report/cryptrec-gl-2007-2024.pdf](https://www.cryptrec.go.jp/report/cryptrec-gl-2007-2024.pdf)
- [https://csrc.nist.gov/csrc/media/Projects/post-quantum-cryptography/documents/pqc-seminars/presentations/13-intro-mpc-in-the-head-05212024.pdf](https://csrc.nist.gov/csrc/media/Projects/post-quantum-cryptography/documents/pqc-seminars/presentations/13-intro-mpc-in-the-head-05212024.pdf)
