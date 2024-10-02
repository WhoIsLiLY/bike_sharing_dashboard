import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import streamlit as st

# Kita set tema seaborn
sns.set(style='darkgrid', font_scale=1.2)

def get_total_count_by_hour_df(hour_df):
    return hour_df.groupby(by="hours").agg({"count_cr": ["sum"]})

def count_by_day_df(day_df):
    return day_df.query(str('dteday >= "2011-01-01" and dteday < "2012-12-31"'))

def total_registered_df(day_df):
    reg_df = day_df.groupby(by="dteday").agg({"registered": "sum"}).reset_index()
    reg_df.rename(columns={"registered": "register_sum"}, inplace=True)
    return reg_df

def total_casual_df(day_df):
    cas_df = day_df.groupby(by="dteday").agg({"casual": "sum"}).reset_index()  # Ensure sum
    cas_df.rename(columns={"casual": "casual_sum"}, inplace=True)
    return cas_df

def sum_order(hour_df):
    return hour_df.groupby("hours").count_cr.sum().sort_values(ascending=False).reset_index()

def macem_season(day_df):
    return day_df.groupby(by="season").count_cr.sum().reset_index()

# Load data
days_df = pd.read_csv("dashboard/day_cleaned.csv")
hours_df = pd.read_csv("dashboard/hour_cleaned.csv")

datetime_columns = ["dteday"]
days_df.sort_values(by="dteday", inplace=True)
days_df.reset_index(inplace=True)

hours_df.sort_values(by="dteday", inplace=True)
hours_df.reset_index(inplace=True)

for column in datetime_columns:
    days_df[column] = pd.to_datetime(days_df[column])
    hours_df[column] = pd.to_datetime(hours_df[column])

# Buat sistem filtering
with st.sidebar:
    st.title('Interactive Visualization')
    st.write('**Data yang divisualisasikan dan informasi yang disampaikan akan mengikuti range tanggal di bawah**')

    # Tanggal input dengan minimal dan maksimal yang valid
    date_range = st.date_input(
        label='Select Date Range',
        min_value=days_df["dteday"].min(),
        max_value=days_df["dteday"].max(),
        value=[days_df["dteday"].min(), days_df["dteday"].max()],
        help="Pilih rentang tanggal."
    )

    # Memastikan ada dua tanggal yang dipilih dalam rentang (start dan end)
    if len(date_range) == 2:
        start_date, end_date = date_range
        st.success(f"Range tanggal dipilih dari {start_date} hingga {end_date}.")
    else:
        st.warning("Abaikan pesan error yang muncul. Mohon pilih rentang tanggal akhirnya (dua tanggal).")

try:
    # Filtering data berdasarkan tanggal awal dan tanggal akhir
    main_df_days = days_df[(days_df["dteday"] >= pd.to_datetime(str(start_date))) & 
                        (days_df["dteday"] <= pd.to_datetime(str(end_date)))]

    main_df_hour = hours_df[(hours_df["dteday"] >= pd.to_datetime(str(start_date))) & 
                            (hours_df["dteday"] <= pd.to_datetime(str(end_date)))]
    # Pengecekan jika tanggal tidak ditemukan data
    if main_df_days.empty or main_df_hour.empty:
        st.warning("Pilih target akhir untuk menampilkan visualisasi data")
    else:
        hour_count_df = get_total_count_by_hour_df(main_df_hour)
        day_df_count_2011 = count_by_day_df(main_df_days)
        reg_df = total_registered_df(main_df_days)
        cas_df = total_casual_df(main_df_days)
        sum_order_items_df = sum_order(main_df_hour)
        season_df = macem_season(main_df_days)

        # Main Header
        st.header(':bicyclist: **Bike Sharing Data Dashboard**')

        # KPI Section
        st.markdown("### Key Performance Indicators")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            total_orders = main_df_days['count_cr'].sum()
            st.metric("Total Bike Rentals", value=f"{total_orders:,}")

        with col2:
            avg_rentals_per_day = main_df_days['count_cr'].mean()
            st.metric("Avg Rentals/Day", value=f"{avg_rentals_per_day:.2f}")

        with col3:
            total_sum_registered = reg_df['register_sum'].sum()  # Convert Series to scalar
            st.metric("Total Registered Users", value=f"{total_sum_registered:,}")

        with col4:
            # After processing:
            total_sum_casual = cas_df['casual_sum'].sum()  # Make sure this is a scalar

            # Display metric correctly:
            st.metric("Total Casual Users", value=f"{total_sum_casual:,.0f}")  # Formatted as an integer

    # Membuat figure dengan ukuran yang besar
    plt.figure(figsize=(24, 5))

    # ============================================================================================================
    # Menghitung jumlah maksimum penyewaan sepeda per bulan
    max_monthly_rentals = main_df_days.groupby(main_df_days['dteday'])['count_cr'].max()

    # Membuat scatter plot untuk jumlah maksimum penyewaan per bulan dengan warna biru muda
    plt.scatter(max_monthly_rentals.index, max_monthly_rentals.values, color="#64B5F6", s=10, marker='o', label='Penyewaan Maksimum')

    # Membuat line plot untuk menunjukkan tren penyewaan
    plt.plot(max_monthly_rentals.index, max_monthly_rentals.values, linestyle='-', color='#1976D2', linewidth=1.5)

    # Mengatur label pada sumbu X
    plt.xlabel('Bulan')

    # Mengatur interval untuk sumbu X agar menunjukkan label setiap 1-2 bulan
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=2))
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))

    # Mengatur label pada sumbu Y
    plt.ylabel('Jumlah Maksimum Penyewaan')

    # Menambahkan judul
    plt.title('Jumlah Penyewaan Sepeda Maksimum per Bulan di Tahun 2011 - 2013')

    # Menambahkan legenda untuk menjelaskan plot
    plt.legend()

    # Menampilkan plot di Streamlit
    st.pyplot(plt)

    # Membuat bar chart untuk tren penjualan per tahun
    sales_trend_data = days_df.groupby('year')['count_cr'].sum()
    # menampilkan hasilnya
    sales_trend = {'2011': sales_trend_data[2011], '2012': sales_trend_data[2012]}
    years = list(sales_trend.keys())
    sales = list(sales_trend.values())

    plt.figure(figsize=(8, 5))
    plt.bar(years, sales, color=['#4CAF50', '#2196F3'])

    # Mengatur label dan judul
    plt.xlabel('Tahun', fontsize=12)
    plt.ylabel('Jumlah Penjualan (Sepeda Disewa)', fontsize=12)
    plt.title('Tren Penjualan Per Tahun', fontsize=14)

    # Menampilkan plot di Streamlit
    st.pyplot(plt)

    st.write("**General Information Terkini Untuk 2011-2012 (Tidak mengikuti date yang diubah)**")
    st.write("Penjualan sepeda mengalami peningkatan signifikan dari tahun 2011 ke 2012.")
    st.write("Pada tahun 2011, total sepeda yang disewa mencapai 1.243.103 unit.")
    st.write("Pada tahun 2012, terjadi peningkatan hingga 2.049.576 unit, menunjukkan pertumbuhan bisnis yang kuat.")

    # =================================================================================================================
    # Menghitung jumlah penyewaan sepeda per musim
    season_sales = main_df_days.groupby('season')['count_cr'].sum()

    # Mencari musim dengan penyewaan tertinggi dan terendah
    highest_season = season_sales.idxmax()  # Musim tertinggi
    lowest_season = season_sales.idxmin()   # Musim terendah

    # Menyusun urutan musim agar lebih mudah dibaca
    order_seasons = ['Spring', 'Summer', 'Fall', 'Winter']
    season_sales = season_sales.reindex(order_seasons)

    # Membuat warna default untuk setiap musim, highlight musim tertinggi dan terendah
    colors = ['#4CAF50' if season != highest_season else '#FF5733' for season in season_sales.index]

    # Membuat bar plot untuk menunjukkan jumlah penyewaan sepeda per musim
    st.subheader("Jumlah Penyewaan Sepeda di Setiap Musim")

    plt.figure(figsize=(10, 6))
    plt.bar(season_sales.index, season_sales.values, color=colors, alpha=0.8)

    # Menambahkan label dan judul
    plt.xlabel('Musim', fontsize=12)
    plt.ylabel('Total Penyewaan Sepeda', fontsize=12)
    plt.title('Jumlah Penyewaan Sepeda di Setiap Musim', fontsize=14)

    # Menambahkan grid untuk membantu visualisasi
    plt.grid(axis='y', linestyle='--', alpha=0.6)

    # Menampilkan plot di Streamlit
    st.pyplot(plt)

    st.write(f"Musim {highest_season} mencatat jumlah penyewaan sepeda tertinggi dibandingkan musim lainnya.")
    st.write(f"Total penyewaan pada musim {highest_season} mencapai {season_sales[highest_season]} unit, menyoroti musim ini sebagai periode paling sibuk untuk penyewaan sepeda.")

    # =================================================================================================================
    # Menghitung total casual dan registered
    total_casual = main_df_days['casual'].sum()
    total_registered = main_df_days['registered'].sum()
    label_dominant = "biasa"
    label_minor = "terdaftar"
    if total_registered > total_casual:
        label_dominant = "terdaftar"
        label_minor = "biasa"

    # Membuat data untuk pie plot
    data = [total_casual, total_registered]
    labels = ['Unregistered', 'Registered']

    # Warna untuk setiap kategori
    colors = ["#FF9999", "#66B2FF"]

    # Membuat pie plot dengan penyesuaian
    st.subheader("Perbandingan Penyewaan Sepeda: Unregistered vs Registered")

    plt.figure(figsize=(7, 7))
    plt.pie(data, labels=labels, autopct='%1.1f%%', explode=(0.05, 0), colors=colors,
            shadow=True, startangle=90, wedgeprops={'edgecolor': 'black', 'linewidth': 1.5})

    # Menambahkan judul pada plot
    plt.title('Perbandingan Penyewaan Sepeda: Unregistered vs Registered', fontsize=14)

    # Menampilkan pie plot di Streamlit
    st.pyplot(plt)

    st.write(f"Sebagian besar penyewa sepeda lebih memilih untuk menjadi pelanggan {label_dominant} dibandingkan pelanggan {label_minor}.")
    st.write(f"Jumlah penyewa {label_dominant} mencapai {total_registered} orang, sedangkan pelanggan {label_minor} hanya sebesar {total_casual} orang.")
    st.write(f"Ini menunjukkan preferensi yang kuat terhadap model pelanggan '{label_dominant}' di antara pelanggan.")

    # =================================================================================================================
    # Calculate total rentals per hour
    hourly_rentals = main_df_hour.groupby('hours')['count_cr'].sum()

    # Determine the peak and lowest hour dynamically based on current data
    peak_hour = hourly_rentals.idxmax()  # Peak hour
    lowest_hour = hourly_rentals.idxmin()  # Lowest hour

    # Define color palette, highlight peak and lowest hours dynamically
    colors = ['#4CAF50' if hour != peak_hour and hour != lowest_hour else '#FF3333' for hour in hourly_rentals.index]

    # Plot the total rentals per hour with customized colors
    st.subheader("Jumlah Penyewaan Sepeda di Setiap Jam")

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(hourly_rentals.index, hourly_rentals.values, color=colors, alpha=0.8)

    # Add labels, title, and grid
    ax.set_xlabel('Jam', fontsize=12)
    ax.set_ylabel('Total Penyewaan Sepeda', fontsize=12)
    ax.set_title('Jumlah Penyewaan Sepeda di Setiap Jam', fontsize=14)
    ax.grid(axis='y', linestyle='--', alpha=0.6)

    # Highlight peak and lowest hours with annotations
    ax.text(peak_hour, hourly_rentals[peak_hour] + 100, f'Puncak: {int(hourly_rentals[peak_hour])}', 
            ha='center', fontsize=12, color='black')
    ax.text(lowest_hour, hourly_rentals[lowest_hour] + 100, f'Terendah: {int(hourly_rentals[lowest_hour])}', 
            ha='center', fontsize=12, color='black')

    # Show the plot in Streamlit
    st.pyplot(fig)

    # Print peak and lowest hour details
    st.write(f"Penyewaan sepeda mencapai puncaknya pada jam {peak_hour}:00.")
    st.write(f"Penyewaan sepeda paling sedikit terjadi pada jam {lowest_hour}:00.")

    # =====================================================================================
    # Memfilter data untuk tahun 2011
    data_2011 = main_df_days[main_df_days['year'] == 2011]

    if data_2011.empty:
        st.write("Tidak ada data untuk 2011")
    else:
        # Menghitung jumlah penyewaan sepeda per bulan di tahun 2011
        monthly_sales_2011 = data_2011.groupby('month')['count_cr'].sum().reset_index()

        # Menyusun ulang urutan bulan agar lebih mudah dibaca
        order_months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        monthly_sales_2011['month'] = pd.Categorical(monthly_sales_2011['month'], categories=order_months, ordered=True)
        monthly_sales_2011 = monthly_sales_2011.sort_values('month')

        # Mendapatkan bulan dengan jumlah penyewaan tertinggi dan terendah
        max_month_2011 = monthly_sales_2011.loc[monthly_sales_2011['count_cr'].idxmax()]['month']
        min_month_2011 = monthly_sales_2011.loc[monthly_sales_2011['count_cr'].idxmin()]['month']

        colors = ['#FF3333' if month == max_month_2011 else ('#64B5F6' if month == min_month_2011 else '#4CAF50') for month in monthly_sales_2011['month']]

        # Membuat bar plot untuk melihat penjualan per bulan di tahun 2011
        st.subheader("Jumlah Penyewaan Sepeda per Bulan di Tahun 2011")

        plt.figure(figsize=(12, 6))
        plt.bar(monthly_sales_2011['month'], monthly_sales_2011['count_cr'], color=colors, alpha=0.7)

        # Menambahkan label dan judul
        plt.xlabel('Bulan', fontsize=12)
        plt.ylabel('Total Penyewaan Sepeda', fontsize=12)
        plt.title('Jumlah Penyewaan Sepeda per Bulan di Tahun 2012', fontsize=14)

        # Menambahkan grid untuk membantu visualisasi
        plt.grid(axis='y', linestyle='--', alpha=0.6)

        # Menampilkan plot di Streamlit
        st.pyplot(plt)

        # Menambahkan keterangan tambahan
        st.write(f"Bulan dengan penyewaan tertinggi di tahun 2011 adalah **{max_month_2011}**.")
        st.write(f"Bulan dengan penyewaan terendah di tahun 2011 adalah **{min_month_2011}**.")

    # Memfilter data untuk tahun 2012
    data_2012 = main_df_days[main_df_days['year'] == 2012]
    if data_2012.empty:
        st.subheader("Tidak ada data untuk 2012")
    else:
        # Menghitung jumlah penyewaan sepeda per bulan di tahun 2012
        monthly_sales_2012 = data_2012.groupby('month')['count_cr'].sum().reset_index()

        # Menyusun ulang urutan bulan agar lebih mudah dibaca
        order_months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        monthly_sales_2012['month'] = pd.Categorical(monthly_sales_2012['month'], categories=order_months, ordered=True)
        monthly_sales_2012 = monthly_sales_2012.sort_values('month')

        # Mendapatkan bulan dengan jumlah penyewaan tertinggi dan terendah
        max_month_2012 = monthly_sales_2012.loc[monthly_sales_2012['count_cr'].idxmax()]['month']
        min_month_2012 = monthly_sales_2012.loc[monthly_sales_2012['count_cr'].idxmin()]['month']
        colors = ['#FF3333' if month == max_month_2012 else ('#64B5F6' if month == min_month_2012 else '#4CAF50') for month in monthly_sales_2012['month']]

        # Membuat bar plot untuk melihat penjualan per bulan di tahun 2012
        st.subheader("Jumlah Penyewaan Sepeda per Bulan di Tahun 2012")

        plt.figure(figsize=(12, 6))
        plt.bar(monthly_sales_2012['month'], monthly_sales_2012['count_cr'], color=colors, alpha=0.7)

        # Menambahkan label dan judul
        plt.xlabel('Bulan', fontsize=12)
        plt.ylabel('Total Penyewaan Sepeda', fontsize=12)
        plt.title('Jumlah Penyewaan Sepeda per Bulan di Tahun 2012', fontsize=14)

        # Menambahkan grid untuk membantu visualisasi
        plt.grid(axis='y', linestyle='--', alpha=0.6)

        # Menampilkan plot di Streamlit
        st.pyplot(plt)

        # Menambahkan keterangan tambahan
        st.write(f"Bulan dengan penyewaan tertinggi di tahun 2012 adalah **{max_month_2012}**.")
        st.write(f"Bulan dengan penyewaan terendah di tahun 2012 adalah **{min_month_2012}**.")
except Exception as e:
    st.error(f"Pilih Tanggal Akhirnya")
