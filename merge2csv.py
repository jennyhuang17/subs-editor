import pandas as pd

epi = 22
fn = str(epi) + "_marked.csv"
char1 = "范云"
char2 = "齐峥"

df1 = pd.read_csv(char1 + fn)
df2 = pd.read_csv(char2 + fn)

df1["角色"] = df1["角色"].combine_first(df2["角色"])

df1.to_csv(f"{epi}_merged.csv", index=False, encoding="utf-8-sig")