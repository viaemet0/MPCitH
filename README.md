# MPC-in-the-Head（MPCitH）

## MPCitH

```bash
python3 mpcith.py
```

<details>
<summary>実行結果</summary>

```bash
公開鍵 y = 18354465632584
メッセージ: b'Hello MPC-in-the-Head'
署名の証明数: 50
署名は有効
--- 改ざん検知 ---
Round 1: Challenge mismatch
改ざん検知成功
```

</details>

MPCitH 証明生成

1. 秘密を加法型秘密分散
2. 各 share をコミット
3. g^{share} を計算し全公開
4. ランダムに 1 パーティ隠し他を開示

MPCitH は、以下に示している技術の、[MPC](#mpcmulti-party-computationを仮想的に実行) から構築した[ゼロ知識証明を Fiat-Shamir 変換することで署名方式を構築](#シュノア識別プロトコルschnorrs-identification-protocol)するフレームワークである。

## MPC（Multi-Party Computation）を仮想的に実行

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

多変数多項式求解問題（MP 問題; 連立方程式を解く問題）のうち、各多項式の次数が最大で 2 であるものを一般に「MQ 問題」と呼ぶ。

MPCitH の方式のひとつである [MQ on my Mind (MQOM)](https://mqom.org/) は、MQ 問題の計算困難性を利用して構成される。

## 参考文献

- [https://www.cryptrec.go.jp/report/cryptrec-gl-2007-2024.pdf](https://www.cryptrec.go.jp/report/cryptrec-gl-2007-2024.pdf)
- [https://csrc.nist.gov/csrc/media/Projects/post-quantum-cryptography/documents/pqc-seminars/presentations/13-intro-mpc-in-the-head-05212024.pdf](https://csrc.nist.gov/csrc/media/Projects/post-quantum-cryptography/documents/pqc-seminars/presentations/13-intro-mpc-in-the-head-05212024.pdf)
- [https://www.gavo.t.u-tokyo.ac.jp/~mine/japanese/IT/Takagi_20181226.pdf](https://www.gavo.t.u-tokyo.ac.jp/~mine/japanese/IT/Takagi_20181226.pdf)
- 高木剛 著. 暗号と量子コンピュータ : 耐量子計算機暗号入門, オーム社, 2019.8. 978-4-274-22410-2. [https://ndlsearch.ndl.go.jp/books/R100000002-I029871173](https://ndlsearch.ndl.go.jp/books/R100000002-I029871173)
- [https://csrc.nist.gov/csrc/media/Projects/pqc-dig-sig/documents/round-1/spec-files/MQOM-spec-web.pdf](https://csrc.nist.gov/csrc/media/Projects/pqc-dig-sig/documents/round-1/spec-files/MQOM-spec-web.pdf)
