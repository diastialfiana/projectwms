# Kisi-Kisi Interview Proyek WMS

Panduan ini merangkum struktur dan alur utama proyek Warehouse Management System (WMS) berbasis Django. Gunakan sebagai bahan belajar dan latihan menjelaskan proyek dengan kata-kata sendiri, bukan untuk menghafal setiap baris kode.

## 1. Ringkasan proyek

Proyek ini adalah aplikasi web untuk membantu operasional gudang, terutama:

- Mengelola data master produk dan gudang.
- Melihat saldo stok produk pada masing-masing gudang.
- Mencatat barang masuk dan barang keluar.
- Melihat riwayat pergerakan stok.
- Mencatat stock opname dan menyetujui penyesuaian stok.
- Menampilkan ringkasan dashboard, stok rendah, dan laporan.
- Menyimpan audit log untuk beberapa aktivitas perubahan stok.

Teknologi utama yang terlihat dari proyek:

- Python dan Django.
- Django ORM untuk berinteraksi dengan database.
- PostgreSQL sebagai konfigurasi default; SQLite dapat dipakai untuk validasi lokal melalui konfigurasi environment.
- Django Templates dan Bootstrap untuk antarmuka.
- Django authentication untuk login dan sesi pengguna.

### Contoh penjelasan proyek selama 30 detik

> “Proyek ini adalah aplikasi WMS berbasis Django untuk mengelola produk, gudang, saldo stok, transaksi barang masuk dan keluar, serta stock opname. Aplikasi dibagi menjadi beberapa Django app berdasarkan domain. View menerima request dan memproses form, sedangkan aturan perubahan stok ditempatkan pada service layer. Perubahan saldo dicatat sebagai movement dan audit log.”

## 2. Peta folder dan tanggung jawab

```text
wmsproject/
├── manage.py
├── requirements.txt
├── db.sqlite3
├── wms/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── accounts/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── signals.py
│   └── migrations/
├── products/
│   ├── models.py
│   ├── forms.py
│   ├── views.py
│   ├── urls.py
│   └── migrations/
├── warehouses/
│   ├── models.py
│   ├── forms.py
│   ├── views.py
│   ├── urls.py
│   └── migrations/
├── inventory/
│   ├── models.py
│   ├── forms.py
│   ├── services.py
│   ├── views.py
│   ├── urls.py
│   ├── tests.py
│   ├── management/commands/seed_demo_data.py
│   └── migrations/
├── templates/
│   ├── base.html
│   ├── dashboard.html
│   ├── accounts/
│   ├── products/
│   ├── warehouses/
│   └── inventory/
└── static/
```

### Fungsi bagian penting

| Bagian | Tanggung jawab | Contoh yang perlu dipahami |
|---|---|---|
| `manage.py` | Menjalankan perintah manajemen Django | `runserver`, `migrate`, `test`, `createsuperuser` |
| `wms/settings.py` | Konfigurasi proyek | `INSTALLED_APPS`, database, template, middleware, timezone |
| `wms/urls.py` | Router tingkat proyek | Menghubungkan prefix URL ke `accounts`, `products`, `warehouses`, `inventory` |
| `accounts/` | Login, dashboard, dan setup grup/permission | `views.py`, `signals.py` |
| `products/` | Data master produk | Model, form, daftar, tambah, dan edit produk |
| `warehouses/` | Data master gudang | Model, form, daftar, tambah, dan edit gudang |
| `inventory/` | Operasi stok dan laporan | Model stok, service transaksi, view, URL, dan test |
| `templates/` | HTML untuk halaman aplikasi | `base.html` menjadi kerangka halaman bersama |
| `static/` | File aset statis | CSS, JavaScript, atau gambar lokal |
| `migrations/` | Riwayat perubahan skema database | File migration yang dihasilkan Django |
| `requirements.txt` | Daftar dependency Python | Django, driver PostgreSQL, `python-dotenv` |
| `db.sqlite3` | Database SQLite lokal | Data lokal; bukan kode aplikasi |

### Pola dasar tiap Django app

- `models.py`: struktur data dan aturan level database.
- `forms.py`: input pengguna dan validasi form.
- `views.py`: menghubungkan request, form/model, dan response/template.
- `urls.py`: nama dan pola URL yang ditangani app.
- `services.py`: aturan bisnis yang ingin dipisahkan dari view; pada proyek ini paling penting untuk inventory.
- `tests.py`: pengujian perilaku aplikasi.
- `admin.py`: konfigurasi tampilan model di Django Admin.
- `migrations/`: perubahan struktur database dari waktu ke waktu.

## 3. Arsitektur request Django

Saat pengguna membuka halaman atau mengirim form, gambaran umumnya:

```text
Browser
  -> wms/urls.py
  -> urls.py milik app
  -> view
  -> form/model/service
  -> database
  -> view memilih template dan mengirim context
  -> HTML response ke browser
```

Pada proyek ini, `wms/urls.py` mengarahkan root URL ke accounts, lalu memakai prefix seperti `/products/`, `/warehouses/`, dan `/inventory/` untuk app lain.

### Istilah yang sebaiknya bisa diterangkan

- **Request**: permintaan dari browser, misalnya GET untuk membuka halaman atau POST untuk mengirim form.
- **URL routing**: pemetaan alamat URL ke fungsi view.
- **View**: bagian yang mengatur alur request dan response.
- **Template**: file HTML yang dirender dengan context dari view.
- **Model**: representasi data dan tabel melalui Django ORM.
- **ORM**: cara melakukan query database menggunakan objek Python, bukan menulis SQL untuk setiap operasi.
- **Migration**: perubahan skema database yang dapat diterapkan secara bertahap.
- **Middleware**: komponen yang memproses request/response di tingkat proyek, misalnya authentication dan CSRF.

## 4. Domain dan model data

### Product

Menyimpan master produk, termasuk SKU, nama, kategori, unit, batas minimum stok, deskripsi, dan status aktif.

Hal yang penting:

- SKU harus unik.
- `minimum_stock` dipakai untuk mengenali produk yang stoknya perlu diperhatikan.
- Produk nonaktif tidak seharusnya dipakai untuk transaksi stok baru menurut service transaksi.

### Warehouse

Menyimpan master gudang, seperti kode, nama, lokasi, deskripsi, dan status aktif.

Kode gudang dibuat unik. Gudang adalah bagian dari identitas lokasi saldo stok.

### InventoryStock

Menyimpan saldo untuk pasangan produk dan gudang.

Konsep penting:

- Satu produk dapat memiliki saldo pada banyak gudang.
- Satu gudang dapat menyimpan banyak produk.
- Unique constraint pada pasangan `product` dan `warehouse` menjaga agar hanya ada satu baris saldo untuk setiap pasangan.
- Check constraint menjaga `quantity` agar tidak negatif.
- Kuantitas memakai `DecimalField`, cocok untuk satuan yang dapat memiliki pecahan.

Secara konsep, hubungan produk dan gudang adalah many-to-many yang memiliki data tambahan, yaitu kuantitas. Data tambahan itu disimpan pada model perantara `InventoryStock`.

### StockMovement

Mencatat kejadian perubahan stok, dengan jenis:

- `IN`: barang masuk.
- `OUT`: barang keluar.
- `ADJUSTMENT`: penyesuaian dari stock opname.

Movement juga menyimpan produk, gudang, kuantitas, referensi, catatan, pengguna, dan waktu pencatatan. Saldo adalah kondisi terkini; movement adalah jejak perubahannya.

### StockOpname

Menyimpan hasil hitung fisik:

- `system_quantity`: saldo menurut sistem saat opname dibuat.
- `physical_quantity`: jumlah yang dihitung secara fisik.
- `difference`: hasil `physical_quantity - system_quantity`.
- `status`: pending, approved, atau rejected.
- Informasi pemeriksa dan penyetuju.

Ketika disetujui, service menghitung selisih terhadap saldo sistem yang disimpan pada opname dan menerapkan adjustment.

### AuditLog

Mencatat aktivitas seperti perubahan saldo dan approval opname. Ini berbeda dari `StockMovement`:

- `StockMovement` adalah catatan bisnis pergerakan stok.
- `AuditLog` adalah jejak aktivitas/perubahan untuk membantu penelusuran.

## 5. Alur barang masuk

Alur contoh untuk `/inventory/stock-in/`:

1. `inventory/urls.py` menghubungkan URL ke view `stock_in`.
2. View membuat `StockInForm` dari data request.
3. Jika request POST dan form valid, view memanggil `record_stock_in()` dari `inventory/services.py`.
4. Service mengubah input kuantitas menjadi `Decimal` dan menolak nilai yang tidak valid atau tidak positif.
5. Service memeriksa produk dan gudang aktif.
6. Di dalam `transaction.atomic()`, service mengunci baris produk dan gudang, mencari/membuat saldo, lalu menambah kuantitas.
7. Service membuat `StockMovement` berjenis `IN` dan membuat log aktivitas.
8. View menampilkan pesan sukses dan mengarahkan pengguna ke riwayat movement.

Hal yang bisa ditekankan: satu transaksi mencakup perubahan saldo dan pembuatan catatan transaksi, sehingga kegagalan di tengah proses tidak seharusnya meninggalkan pembaruan setengah jalan.

## 6. Alur barang keluar

Alurnya mirip barang masuk, tetapi service:

1. Memastikan kuantitas lebih besar dari nol.
2. Memastikan produk dan gudang aktif.
3. Mengunci baris terkait di dalam transaksi database.
4. Memastikan saldo tersedia.
5. Menolak transaksi jika saldo kurang dari kuantitas yang diminta.
6. Mengurangi saldo, membuat movement `OUT`, dan membuat audit log.

### Mengapa kuantitas memakai `Decimal`?

Stok dapat dicatat dalam pecahan, contohnya 1.250 kg. `Decimal` menghindari masalah pembulatan yang umum terjadi jika angka desimal uang/stok dihitung sebagai floating point biner.

## 7. Transaksi database dan konkurensi

### `transaction.atomic()`

Mengelompokkan beberapa operasi database menjadi satu transaksi. Jika terjadi exception sebelum commit, perubahan dalam blok transaksi dibatalkan.

Contoh kebutuhan di inventory:

- Mengubah saldo.
- Membuat movement.
- Menulis audit log.

Ketiganya berkaitan. Jika saldo berubah tetapi movement gagal tersimpan, catatan bisnis menjadi tidak konsisten. Transaksi membantu menghindari kondisi tersebut.

### `select_for_update()`

Meminta database mengunci baris terpilih sampai transaksi selesai. Tujuannya agar transaksi lain tidak membaca dan mengubah saldo yang sama secara bersamaan tanpa koordinasi.

Jawaban yang baik tidak mengklaim bahwa satu pemanggilan ini sendirian menyelesaikan seluruh persoalan konkurensi. Perilakunya bergantung pada database dan transaksi; PostgreSQL mendukung row-level locking, sedangkan SQLite tidak memberikan perilaku row lock yang sama.

### Constraint database

Validasi di Python meningkatkan pesan kesalahan dan pengalaman pengguna. Constraint database memberi perlindungan tambahan jika data ditulis dari jalur lain atau terjadi kondisi bersamaan. Untuk saldo, proyek memiliki batas non-negatif dan keunikan pasangan produk-gudang.

## 8. Alur stock opname

1. Pengguna membuat opname dengan memilih produk, gudang, dan jumlah fisik.
2. Service mengambil saldo sistem saat itu, atau nol jika saldo belum ada.
3. Model menghitung selisih: jumlah fisik dikurangi jumlah sistem.
4. Catatan dibuat dengan status awal pending.
5. Saat disetujui, service mengambil ulang opname dan saldo dalam transaksi.
6. Jika ada selisih, saldo disesuaikan dan movement `ADJUSTMENT` dicatat.
7. Opname diberi status approved beserta pengguna dan waktu approval.
8. Aktivitas approval dicatat ke audit log.

### Contoh angka

Saldo sistem 10, jumlah fisik 7:

```text
difference = 7 - 10 = -3
saldo setelah adjustment = 10 + (-3) = 7
```

Jika jumlah fisik 12, selisihnya `+2` dan stok bertambah dua.

## 9. Form, view, dan template

### Form

`ProductForm` dan `WarehouseForm` adalah `ModelForm`. Keduanya menampilkan field model dan menambahkan validasi khusus, seperti pemeriksaan nilai unik tanpa membedakan kapitalisasi.

### View

View master produk dan gudang menjalankan pola CRUD sederhana:

- Menampilkan daftar dengan pencarian.
- Membuat data dari form.
- Memperbarui data yang sudah ada.
- Menampilkan pesan keberhasilan dan mengarahkan kembali ke daftar.

View inventory memakai service untuk operasi yang memiliki aturan perubahan stok.

### Template

`templates/base.html` berisi struktur bersama seperti navigasi, pesan, dan blok konten. Template halaman lain menggunakan layout ini agar elemen umum tidak perlu diduplikasi.

Konteks template biasanya dikirim oleh view, misalnya daftar produk, hasil pencarian, atau statistik dashboard.

## 10. Login, grup, dan permission

- Sebagian besar halaman memakai `login_required`, jadi pengguna harus login untuk mengaksesnya.
- `accounts/signals.py` membuat grup Administrators dan Warehouse Users setelah migrasi, serta mengatur permission model untuk grup.
- Saat menjelaskan proyek, bedakan antara **permission yang disiapkan** dengan **authorization yang benar-benar diperiksa pada setiap view**. Dekorator `login_required` sendiri hanya memastikan pengguna login, bukan memeriksa permission tertentu.
- Jangan mengatakan semua hak akses sudah dibatasi per peran jika implementasi view yang diperiksa hanya memakai login requirement.

### Jawaban interview yang jujur

> “Login sudah melindungi halaman. Proyek juga menyiapkan grup dan permission Django, tetapi pemeriksaan hak akses per aksi perlu ditinjau konsisten di view/service. Itu salah satu area yang bisa saya tingkatkan.”

## 11. Test dan cara menjalankannya

Test di `inventory/tests.py` mencakup:

- Barang masuk berhasil.
- Barang keluar berhasil.
- Barang keluar ditolak jika stok tidak cukup.
- Kuantitas nol atau negatif ditolak.
- Approval opname mengubah saldo.
- SKU dan kode gudang duplikat ditolak.
- Test tambahan untuk memastikan saldo tidak menjadi negatif dalam skenario pengeluaran berurutan.

Perintah yang relevan:

```powershell
python manage.py check
python manage.py test inventory
python manage.py test
```

Migrasi dan menjalankan aplikasi:

```powershell
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

`makemigrations` membuat file migration berdasarkan perubahan model. `migrate` menerapkan migration ke database.

### Catatan interpretasi hasil test

Test bernama concurrency dalam file ini melakukan dua operasi pengeluaran secara berurutan. Itu berguna menguji hasil saldo pada skenario tersebut, tetapi bukan simulasi dua thread/proses yang benar-benar berjalan serentak. Selain itu, hasil pengujian row locking perlu diuji pada database yang mendukung perilaku locking yang dipakai, seperti PostgreSQL.

## 12. Jika diminta mengubah tata letak folder

### Cara berpikir yang aman

Jangan mulai dengan memindahkan file secara acak. Mulai dari alasan perubahan dan dampak dependensinya.

1. Tanyakan atau pastikan tujuan perubahan: mengurangi file terlalu besar, memisahkan domain, atau merapikan template?
2. Catat import yang memakai modul/file tersebut.
3. Periksa pemanggil view, URL name, template path, konfigurasi app, test, dan migration.
4. Buat perubahan dalam lingkup kecil, satu domain dulu.
5. Perbarui import dan referensi URL/template.
6. Jalankan `python manage.py check` dan test yang relevan.
7. Pastikan perilaku URL dan nama URL yang sudah digunakan template tidak berubah tanpa alasan.

### Contoh: memecah `inventory/views.py`

Jika file view inventory membesar, salah satu pilihan adalah mengubahnya menjadi package:

```text
inventory/
├── views/
│   ├── __init__.py
│   ├── stock.py
│   └── opname.py
├── services.py
├── models.py
└── urls.py
```

Kemudian import di `inventory/urls.py` disesuaikan, misalnya fungsi stock diimpor dari `views.stock` dan fungsi opname dari `views.opname`.

Yang perlu dicek setelah perubahan:

- Semua import berhasil.
- Tidak ada nama view yang hilang dari URL configuration.
- URL name yang dipakai template tetap sama.
- Test tetap menemukan modul dan berjalan.
- `python manage.py check` tidak melaporkan masalah konfigurasi.

### Contoh: memindahkan template

Template dicari berdasarkan nama/path yang diberikan ke `render()`. Jika file dipindah, string path di view juga perlu diubah. Jika template menggunakan `{% extends %}` atau `{% include %}`, relasi antar-template juga perlu diperiksa.

### Contoh: memindahkan Django app

Memindahkan app lebih berisiko daripada merapikan file internal karena berpengaruh ke:

- Nilai app di `INSTALLED_APPS`.
- `AppConfig.name` dan `AppConfig.label`.
- Import antaraplikasi.
- Nama tabel dan histori migration.
- Referensi content type dan permission.
- URL include.

Karena itu, jangan mengubah label app atau jalur migration tanpa memahami konsekuensi database dan deployment. Untuk permintaan interview berupa refactor sederhana, jelaskan dulu batas perubahan dan strategi validasinya.

### Jawaban contoh

> “Saya mulai dari tujuan refactor dan memetakan semua referensi sebelum memindahkan file. Untuk perubahan internal seperti memecah view inventory, saya mempertahankan URL dan nama URL agar template serta link yang ada tidak rusak, memperbarui import, lalu menjalankan Django check dan test inventory.”

## 13. Pertanyaan interview dan contoh inti jawaban

### “Apa tanggung jawab `models.py`, `views.py`, dan `services.py`?”

> “Model mendefinisikan data dan relasi. View menangani request, validasi form, dan response. Service menampung aturan bisnis yang perlu dipakai terpisah dari HTTP flow, terutama perubahan saldo stok.”

### “Kenapa perubahan stok tidak langsung dilakukan di view?”

> “Agar aturan stok terpusat, lebih mudah diuji, dan dapat digunakan dari jalur lain tanpa menggandakan logika di setiap view.”

### “Bagaimana sistem mencegah barang keluar melebihi saldo?”

> “Service memeriksa saldo sebelum pengurangan, lalu menolak jika kuantitas yang diminta lebih besar. Database juga memiliki constraint agar saldo tidak negatif.”

### “Apa bedanya saldo dan movement?”

> “Saldo menunjukkan jumlah stok saat ini untuk pasangan produk dan gudang. Movement adalah riwayat transaksi yang menjelaskan perubahan saldo.”

### “Apa fungsi `select_related()`?”

> “Untuk mengambil relasi foreign key bersama query utama, sehingga saat template mengakses objek terkait, jumlah query database dapat dikurangi.”

### “Apa perbedaan GET dan POST?”

> “GET umumnya mengambil/menampilkan data tanpa mengubah state. POST digunakan untuk mengirim data atau melakukan perubahan. Form yang mengubah data sebaiknya memakai POST dan dilindungi CSRF.”

### “Apa itu migration?”

> “Migration adalah versi perubahan struktur database yang dibuat Django dari perubahan model dan diterapkan ke database dengan perintah migrate.”

### “Bagaimana kamu menguji perubahan?”

> “Saya mulai dengan test yang terkait langsung, lalu menjalankan Django check. Jika perubahan berdampak lintas aplikasi atau routing, saya jalankan test suite yang lebih luas.”

### “Apa yang kamu tingkatkan berikutnya?”

Pilih jawaban yang benar-benar dapat kamu jelaskan, misalnya:

- Menambahkan pemeriksaan permission sesuai peran pada aksi tertentu.
- Memastikan approval opname tidak dapat diproses berulang kali.
- Memastikan endpoint yang mengubah state hanya menerima metode HTTP yang sesuai.
- Menambah test yang benar-benar menjalankan transaksi secara paralel pada database yang mendukung row locking.
- Menambahkan pagination untuk daftar yang datanya dapat tumbuh besar.
- Memisahkan statistik dashboard agar satu implementasi dipakai konsisten.

Jelaskan sebagai rencana peningkatan, bukan mengklaim fitur tersebut sudah diterapkan.

## 14. Hal yang perlu dijawab secara jujur

Saat interview, lebih baik membedakan fitur yang ada dan ide pengembangan:

- Proyek memiliki grup serta permission Django yang dibuat melalui signal, tetapi view yang diperiksa banyak menggunakan `login_required`; itu bukan pemeriksaan permission berbasis peran.
- Test operasi stok sudah ada, tetapi test concurrency yang terlihat belum menjalankan dua proses/thread bersamaan.
- Stock opname memiliki status dan approval, namun jika membahas approval berulang, jelaskan bahwa transisi status/idempotensi perlu dipastikan dan dites.
- Konfigurasi README menyebut PostgreSQL sebagai konfigurasi utama serta SQLite untuk validasi lokal. Jangan menyimpulkan perilaku locking PostgreSQL terbukti hanya dari test SQLite.
- `accounts/models.py` berisi `AccountProfile` placeholder yang `managed = False`; jangan menjelaskannya sebagai model profil aktif yang menyimpan field profil.

## 15. Rencana belajar singkat

### Jika punya 60 menit

1. **10 menit:** pahami ringkasan proyek dan peta folder.
2. **15 menit:** telusuri `inventory/urls.py` → `inventory/views.py` → `inventory/services.py`.
3. **10 menit:** pahami `InventoryStock`, `StockMovement`, dan `StockOpname`.
4. **10 menit:** baca test inventory dan pahami skenario yang dijaga.
5. **10 menit:** latihan menjawab pertanyaan tentang transaction, service layer, dan perubahan folder.
6. **5 menit:** ucapkan ringkasan proyek 30 detik tanpa membaca.

### Checklist sebelum interview

- [ ] Bisa menjelaskan tujuan aplikasi dalam dua kalimat.
- [ ] Bisa menggambar alur request dari URL sampai database dan template.
- [ ] Bisa membedakan model, form, view, service, dan template.
- [ ] Bisa menjelaskan alur barang masuk, barang keluar, dan opname.
- [ ] Bisa menjelaskan `transaction.atomic()` dan `select_for_update()` secara sederhana.
- [ ] Bisa menyebut test yang tersedia dan batas cakupannya.
- [ ] Bisa menjelaskan urutan aman saat memindahkan file.
- [ ] Tidak mengklaim hal yang belum diterapkan atau belum diuji.

## 16. Ringkasan satu menit

> “WMS ini dibangun dengan Django dan dipisah menjadi app accounts, products, warehouses, dan inventory. Produk dan gudang adalah data master. Saldo disimpan per kombinasi produk-gudang, sementara setiap perubahan dicatat sebagai stock movement. View menerima request dan form, kemudian operasi stok memanggil service layer. Service memvalidasi kuantitas dan status entitas, menggunakan transaksi database, mengubah saldo, lalu mencatat movement dan audit. Jika perlu mengubah struktur folder, saya akan memetakan import, URL, template, test, serta migration yang terdampak; melakukan perubahan kecil; dan memverifikasi dengan Django check serta test terkait.”
