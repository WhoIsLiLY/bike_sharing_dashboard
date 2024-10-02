# Bike Sharing Dashboard - Willy Himawan Dicoding Submission ✨

## Deskripsi Proyek
Dashboard ini menampilkan visualisasi interaktif dari data penyewaan sepeda, memungkinkan pengguna untuk menganalisis pola penyewaan berdasarkan tanggal dan waktu.

## Struktur Proyek
- `dashboard.py`: File utama untuk menjalankan Streamlit app.
- `requirements.txt`: Berisi daftar dependencies yang diperlukan.
- `data/`: Folder tempat menyimpan dataset.

## Menyiapkan Data
Sumber data dapat dilihat dari [sumber data](https://www.kaggle.com/datasets/lakshmi25npathi/bike-sharing-dataset).

## Dependencies
- `Streamlit`: Untuk membangun aplikasi web interaktif.
- `Pandas`: Untuk memanipulasi dan menganalisis data.
- `Matplotlib`: Untuk mengvisualisasikan data.
- `Numpy`: Untuk melakukan perhitungan matematis.
- `Seaborn`: Untuk mengatur tema.

## Setup Environment - Anaconda
```
conda create --name main-ds python=3.9
conda activate main-ds
pip install -r requirements.txt
```

## Setup Environment - Shell/Terminal
```
mkdir proyek_analisis_data
cd proyek_analisis_data
pipenv install
pipenv shell
pip install -r requirements.txt
```

## Run steamlit app
```
streamlit run dashboard.py
```

## Kontribusi
Jika menemukan bug atau ingin berkontribusi, silakan buat pull request atau ajukan issue.
