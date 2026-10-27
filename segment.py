import pandas as pd

input_file = "input.csv"

df = pd.read_csv(input_file)

# 第五列：Python 索引是 4
col = df.columns[4]

for i in range(36, 37):
    ep_value = f"EP{i:02d}"  # 构造 EP01, EP02, ..., EP35
    subset = df[df[col] == ep_value]
    
    # 输出文件名：例如 "1.csv", "2.csv", ..., "35.csv"
    subset.to_csv(f"{i}.csv", index=False)