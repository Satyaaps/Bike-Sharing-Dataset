import pandas as pd

# Membaca file day.csv dan hour.csv
day_df = pd.read_csv("day.csv")
hour_df = pd.read_csv("hour.csv")

# Menggabungkan kedua DataFrame
all_data = pd.concat([day_df, hour_df], ignore_index=True)

# Menyimpan gabungan data ke file main_data.csv
all_data.to_csv("main_data.csv", index=False)

print("Gabungan data berhasil disimpan ke main_data.csv")
