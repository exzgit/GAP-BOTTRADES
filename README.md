# GAP-BOTTRADES

GAP-BOTTRADES adalah bot perdagangan otomatis yang dirancang untuk memprediksi dan memanfaatkan gap pada pasar kripto di Binance. Bot ini akan membeli aset ketika terjadi gap tertentu dan menjualnya saat gap tersebut tertutup, memungkinkan otomatisasi strategi trading gap.

## Fitur Utama
- **Deteksi Gap**: Bot ini mampu mendeteksi gap harga berdasarkan data historis dan menetapkan threshold untuk mengambil keputusan perdagangan.
- **Automasi Perdagangan**: Setelah mendeteksi gap, bot akan secara otomatis mengeksekusi order beli dan menjualnya ketika gap tertutup, atau menahan aset jika gap belum tertutup.
- **Konfigurasi Mudah**: Bot ini dapat dikonfigurasi melalui file `CONFIG.json`, yang menyimpan kunci API Binance, limit rate, dan pengaturan lainnya.

## Cara Kerja
1. **Konfigurasi**: File `CONFIG.json` berisi informasi API dan pengaturan penting lainnya.
2. **Pengumpulan Data**: Bot mengambil data OHLCV dari Binance untuk pasangan perdagangan yang telah ditentukan.
3. **Deteksi Anomali**: Menggunakan logika yang telah ditentukan, bot mendeteksi gap pada harga.
4. **Eksekusi Order**: Saat gap terdeteksi dan memenuhi syarat, bot akan melakukan pembelian dan memantau harga hingga gap tertutup, lalu melakukan penjualan.

## Cara Memulai
1. Clone repository ini:
    ```bash
    git clone https://github.com/username/gap-bottrades.git
    ```
2. Install dependensi:
    ```bash
    pip install -r requirements.txt
    ```
3. Buat file `CONFIG.json` Anda berdasarkan template berikut:
    ```json
    {
        "APIKEYS": "YourAPIKey",
        "SCREETS": "YourAPISecret",
        "ENABLERATELIMIT": true
    }
    ```
4. Jalankan bot:
    ```bash
    python gap_bottrades.py
    ```

## GNU General Public License
Proyek ini dilisensikan di bawah GNU General Public License v3.0. Anda diperbolehkan untuk menyalin, mendistribusikan, dan memodifikasi perangkat lunak ini, asalkan modifikasi dan distribusi tetap berada di bawah lisensi yang sama.

Untuk informasi lebih lanjut tentang hak dan batasan, lihat [GNU General Public License](https://www.gnu.org/licenses/gpl-3.0.html).

## Kontribusi
Kontribusi dalam bentuk pull request dan issue sangat disambut. Harap pastikan semua kontribusi mengikuti panduan gaya kode dan lisensi yang telah ditetapkan.

---

**DISCLAIMER**: Perdagangan kripto melibatkan risiko finansial yang tinggi. Gunakan bot ini dengan pertimbangan dan tanggung jawab Anda sendiri.
