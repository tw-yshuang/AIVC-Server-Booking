import pandas as pd
grades = {
"name": ["Mike", "Sherry", "Cindy", "John"],
"math": [80, 75, 93, 86],
"chinese": [63, 90, 85, 70]
}
df = pd.DataFrame(grades)
print(df)
new_df = df.drop([0, 3], axis=0) # 刪除第一筆及第四筆資料
print("刪除第一筆及第四筆資料")
print(new_df)