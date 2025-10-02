# MPC-in-the-Head（MPCitH）

## クラス

- `Fq`: 有限体
- `GroupElement`: 群
- `FieldShare`: 有限体で構成されるシェア
- `GroupShare`: 群で構成されるシェア

## 流れ

1. 加法型秘密分散法（Additive Secret Sharing）で秘密 x を`n`個のシェア（`x_1,x_2,...,x_n`）に分散

   `x=x_1+x_2+...+x_n`

2. 巡回群`<g>`の生成元`g`と`i`番目のシェア`x_i`で累乗計算`g^(x_i)`
3. `n`個の`g^(x_i)`の積を求めると、指数部分が加算となり、`g^x`と等しい結果が得られる

   `g^(x_1)*g^(x_2)*...*g^(x_n)=g^(x_1+x_2+...+x_n)=g^x`
