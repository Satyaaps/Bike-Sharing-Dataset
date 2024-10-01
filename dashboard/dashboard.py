import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency

# Membaca file day.csv dan hour.csv
day_df = pd.read_csv("data/day.csv")
hour_df = pd.read_csv("data/hour.csv")

# Menampilkan nama kolom untuk debugging
print("Kolom di day_df:", day_df.columns)
print("Kolom di hour_df:", hour_df.columns)

# Menggabungkan kedua DataFrame
main_data = pd.concat([day_df, hour_df], ignore_index=True)

# Menyimpan gabungan data ke file main_data.csv
main_data.to_csv("main_data.csv", index=False)
print("Gabungan data berhasil disimpan ke main_data.csv")

# Mengatur gaya visual
sns.set(style='dark')

# Fungsi untuk menyiapkan DataFrame harian
def create_daily_orders_df(df):
    daily_orders_df = df.resample(rule='D', on='dteday').agg({
        "cnt": "sum"  # Mengagregasi total count
    })
    daily_orders_df = daily_orders_df.reset_index()
    daily_orders_df.rename(columns={
        "cnt": "order_count",
        "dteday": "order_date"
    }, inplace=True)
    return daily_orders_df

# Load data
all_df = pd.read_csv("main_data.csv")  # Mengganti all_data.csv dengan main_data.csv

# Cek kolom yang ada dalam DataFrame
print("Kolom di all_df:", all_df.columns)  # Untuk debug, lihat nama kolom

# Konversi kolom ke tipe datetime jika kolom ada
if 'dteday' in all_df.columns:
    all_df['dteday'] = pd.to_datetime(all_df['dteday'], errors='coerce')
else:
    st.error("Kolom 'dteday' tidak ditemukan!")

# Mengurutkan DataFrame berdasarkan dteday jika kolom ada
if 'dteday' in all_df.columns:
    all_df.sort_values(by="dteday", inplace=True)
    all_df.reset_index(drop=True, inplace=True)
else:
    st.error("Kolom 'dteday' tidak ditemukan!")

# Filter berdasarkan tanggal
if 'dteday' in all_df.columns:
    min_date = all_df["dteday"].min()
    max_date = all_df["dteday"].max()

    with st.sidebar:
        st.image("dashboard/data/a1.png")
        start_date, end_date = st.date_input(
            label='Rentang Waktu',
            min_value=min_date,
            max_value=max_date,
            value=[min_date, max_date]
        )

    main_df = all_df[(all_df["dteday"] >= str(start_date)) & 
                      (all_df["dteday"] <= str(end_date))]
else:
    st.error("Kolom 'dteday' tidak ditemukan!")

# Cek apakah main_df didefinisikan dan tidak kosong
if 'main_df' in locals() and not main_df.empty:
    daily_orders_df = create_daily_orders_df(main_df)

    # Header dashboard
    st.header('Renting Bike Chart :bike:')

    # Daily Orders
    st.subheader('Daily Orders')
    col1, col2 = st.columns(2)

    with col1:
        total_orders = daily_orders_df.order_count.sum()
        st.metric("Total jumlah penyewaan seluruhnya", value=total_orders)

    # with col2:
    #     total_revenue = format_currency(total_orders, "AUD", locale='es_CO')  
    #     st.metric("Total Revenue", value=total_revenue)

    fig, ax = plt.subplots(figsize=(16, 8))
    ax.plot(daily_orders_df["order_date"], daily_orders_df["order_count"], marker='o', linewidth=2, color="#90CAF9")
    ax.tick_params(axis='y', labelsize=30)
    ax.tick_params(axis='x', labelsize=15)

    st.pyplot(fig)

    # Best & Worst Performing Product
    st.subheader("Best & Worst Performing Product")

    # Filter data berdasarkan season 3 dan tahun 2011 atau 2012
    season_data = main_df[(main_df['season'] == 3) & (main_df['yr'].isin([0, 1]))]

    # Hitung total penyewaan untuk tahun 2011 dan 2012
    total_2011 = season_data[season_data['yr'] == 0]['cnt'].sum()
    total_2012 = season_data[season_data['yr'] == 1]['cnt'].sum()

    # Hitung persentase kenaikan/penurunan
    if total_2011 != 0:  # Cek agar tidak terjadi pembagian dengan nol
        percentage_change = ((total_2012 - total_2011) / total_2011) * 100
    else:
        percentage_change = None

    # Mencari tahun dengan penyewaan tertinggi di season 3 pada tahun 2011 dan 2012
    highest_rentals = season_data.groupby('yr')['cnt'].sum().idxmax()
    highest_value = season_data.groupby('yr')['cnt'].sum().max()

    # Menampilkan hasil ke dalam Streamlit
    st.write(f"Tahun dengan penyewaan tertinggi: {highest_rentals + 2011} dengan jumlah {highest_value}")
    st.write(f"Total penyewaan sepeda di tahun 2011: {total_2011}")
    st.write(f"Total penyewaan sepeda di tahun 2012: {total_2012}")
    if percentage_change is not None:
        st.write(f"Persentase kenaikan/penurunan dari 2011 ke 2012: {percentage_change:.2f}%")

    # Tampilkan grafik batang untuk total penyewaan per tahun
    fig, ax = plt.subplots()
    years = ['Musim ke-3 (2011)', 'Musim ke-3 (2012)']
    totals = [total_2011, total_2012]
    sns.barplot(x=years, y=totals, ax=ax, palette='viridis')
    ax.set_title('Total Penyewaan Sepeda pada musim ke-3 (2011 vs 2012)')
    ax.set_ylabel('Jumlah Penyewaan')
    ax.set_xlabel('Tahun')
    st.pyplot(fig)  # Menampilkan grafik di Streamlit

    # Customer Demographics
    st.subheader("Customer Demographics")

    # Pastikan untuk mengecek apakah kolom 'dteday' ada dan kita bisa mengambil tahun dari sana
    if 'dteday' in hour_df.columns:
        hour_df['dteday'] = pd.to_datetime(hour_df['dteday'])

        # Tambahkan kolom 'year' jika belum ada, ekstrak dari kolom 'dteday'
        if 'year' not in hour_df.columns:
            hour_df['year'] = hour_df['dteday'].dt.year

        # Pastikan kolom 'weekday' ada, jika tidak, periksa nama yang benar (misal 'day' atau lainnya)
        if 'weekday' not in hour_df.columns:
            hour_df['weekday'] = hour_df['dteday'].dt.weekday

        # Memfilter data untuk musim pertama di tahun 2012
        first_season_2012 = hour_df[(hour_df['year'] == 2012) & (hour_df['season'] == 1)]

        # Menghitung rata-rata penyewaan per jam
        average_hourly_rentals = first_season_2012['cnt'].mean()
        st.write(f"Rata-rata per jam penyewaan pada musim pertama 2012: {average_hourly_rentals:.2f}")

        # Mengelompokkan data berdasarkan hari dan menghitung total penyewaan untuk masing-masing hari
        rentals_by_day = first_season_2012.groupby('weekday')['cnt'].sum().sort_values(ascending=False)

        # Tampilkan grafik batang untuk penyewaan berdasarkan hari
        fig2, ax2 = plt.subplots()
        days = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu']
        rentals = rentals_by_day.values
        sns.barplot(x=days, y=rentals, ax=ax2, palette='coolwarm')
        ax2.set_title('Total Penyewaan Sepeda per Hari')
        ax2.set_ylabel('Jumlah Penyewaan')
        ax2.set_xlabel('Hari')
        st.pyplot(fig2)  # Menampilkan grafik di Streamlit

    # RFM Parameters
    st.subheader("Best Customer Based on RFM Parameters")

    # Tambahkan logika untuk menampilkan parameter RFM
    # Misalkan kita hanya menunjukkan pelanggan terbaik berdasarkan total penyewaan
    rfm_data = main_df.groupby('instant').agg({
        'cnt': 'sum',
    }).reset_index()

    rfm_data.rename(columns={'cnt': 'total_rentals'}, inplace=True)
    best_customer = rfm_data.loc[rfm_data['total_rentals'].idxmax()]

    st.write(f"Pelanggan terbaik memiliki total penyewaan sebanyak: {best_customer['total_rentals']}")

    st.write("")
    st.write("")

    st.write("Copyright - I Gede Satya Ariya Putra Sangjaya")

else:
    st.error("Tidak ada data untuk ditampilkan.")
    
 