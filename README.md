# MPC-in-the-Head（MPCitH）

## MPCitH

```bash
python3 mpcith.py
```

MPCitH 証明生成

1. 秘密を加法秘密分散
2. 各 share をコミット
3. g^{share} を計算し全公開
4. ランダムに 1 パーティ隠し他を開示

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

シュノア識別プロトコルを Fiat-Shamir 変換し、署名とするアルゴリズム
