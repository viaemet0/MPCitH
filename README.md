# MPC-in-the-Head（MPCitH）

## MPCitH

```bash
python3 mpcith.py
```

```bash
公開鍵 y = 18354465632584
メッセージ: b'Hello MPC-in-the-Head'
署名の証明数: 50
署名は有効
--- 改ざん検知 ---
Round 1: Challenge mismatch
改ざん検知成功
```

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

```bash
g^42 = 44297456736
FieldShare = [Fq(82 mod 163), Fq(14 mod 163), Fq(147 mod 163), Fq(98 mod 163), Fq(27 mod 163)]
reconstruct = 42
GroupShare = [GroupElement(32541919874 mod 50857683791), GroupElement(28961208938 mod 50857683791), GroupElement(40869685257 mod 50857683791), GroupElement(20239889543 mod 50857683791), GroupElement(9463779890 mod 50857683791)]
product = 44297456736
ok
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

```bash
公開鍵 y = 1518902272723967863669890105839591477644211597460852197034
メッセージ = b'Hello Schnorr'
署名: (u=2344591716106405827104733872735240967034872954588326111797, c=664897452803676259314387341447007669025840972427, z=1026468641905427409698695352320983466588123611769)
```

ゼロ知識証明を Fiat-Shamir 変換し、署名とする例

## MQ 問題

```bash
python3 mq_problem.py
```

```bash
MQ Problem(n=2, m=4, q=31, deg=2), Variables: (x1, x2) in F_31^2
    p1(x1, x2) = 26      (where: p1(x) = 1 + 17*x1 + 29*x2 + 12*x1*x1 + 4*x1*x2 + 22*x2*x2)
    p2(x1, x2) = 14      (where: p2(x) = 27 + 27*x1 + 10*x2 + 12*x1*x1 + 30*x1*x2 + 26*x2*x2)
    p3(x1, x2) = 9       (where: p3(x) = 3 + 23*x1 + 22*x2 + 30*x1*x1 + 30*x1*x2 + 22*x2*x2)
    p4(x1, x2) = 5       (where: p4(x) = 9 + 11*x1 + 9*x2 + 2*x1*x1 + x1*x2 + 20*x2*x2)
Matrix form:
    x A1 x^T + x b1^T = 25       (where: 12*x1^2 + 4*x1*x2 + 22*x2^2 + 17*x1 + 29*x2)
    x A2 x^T + x b2^T = 18       (where: 12*x1^2 + 30*x1*x2 + 26*x2^2 + 27*x1 + 10*x2)
    x A3 x^T + x b3^T = 6        (where: 30*x1^2 + 30*x1*x2 + 22*x2^2 + 23*x1 + 22*x2)
    x A4 x^T + x b4^T = 27       (where: 2*x1^2 + 1*x1*x2 + 20*x2^2 + 11*x1 + 9*x2)
```

多変数多項式求解問題（MP 問題; 連立方程式を解く問題）のうち、各多項式の次数が最大で 2 であるものを一般に「MQ 問題」と呼ぶ。

MPCitH の方式のひとつである [MQ on my Mind (MQOM)](https://mqom.org/) は、MQ 問題の計算困難性を利用して構成される。

## 参考文献

- [https://www.cryptrec.go.jp/report/cryptrec-gl-2007-2024.pdf](https://www.cryptrec.go.jp/report/cryptrec-gl-2007-2024.pdf)
- [https://csrc.nist.gov/csrc/media/Projects/post-quantum-cryptography/documents/pqc-seminars/presentations/13-intro-mpc-in-the-head-05212024.pdf](https://csrc.nist.gov/csrc/media/Projects/post-quantum-cryptography/documents/pqc-seminars/presentations/13-intro-mpc-in-the-head-05212024.pdf)
- [https://www.gavo.t.u-tokyo.ac.jp/~mine/japanese/IT/Takagi_20181226.pdf](https://www.gavo.t.u-tokyo.ac.jp/~mine/japanese/IT/Takagi_20181226.pdf)
- 高木剛 著. 暗号と量子コンピュータ : 耐量子計算機暗号入門, オーム社, 2019.8. 978-4-274-22410-2. [https://ndlsearch.ndl.go.jp/books/R100000002-I029871173](https://ndlsearch.ndl.go.jp/books/R100000002-I029871173)
- [https://csrc.nist.gov/csrc/media/Projects/pqc-dig-sig/documents/round-1/spec-files/MQOM-spec-web.pdf](https://csrc.nist.gov/csrc/media/Projects/pqc-dig-sig/documents/round-1/spec-files/MQOM-spec-web.pdf)
