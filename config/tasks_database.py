# config/tasks_database.py
TASKS_DATA = {
    # -------------------------------------------------------------------------
    # MODUL 1: IMPORT & EXTRACT
    # -------------------------------------------------------------------------
    "modul_01": {
        "title": "Import and Extract",
        "description": "Ekstraksi ZIP multi-CSV, inspeksi skema awal, dan verifikasi kelengkapan tabel.",
        "mcq": {
            "task_id": "m1_mcq_1",
            "question": "Metode apa yang paling efisien membaca file CSV langsung dari memori ZIP tanpa ekstrak fisik ke disk?",
            "options": [
                "zipfile.ZipFile.extractall() lalu pd.read_csv()",
                "pd.read_csv(zipfile.ZipFile.open(filename))",
                "os.system('unzip archive.zip') lalu looping file",
                "pd.read_zip('archive.zip')",
            ],
            "correct_index": 1,
            "points": 15,
        },
        "matching": {
            "task_id": "m1_match_1",
            "title": "Jodohkan nama file CSV mentah dengan deskripsi entitas datanya:",
            "sources": [
                "offline_pos_orders.csv",
                "products_catalog.csv",
                "returns_warranty.csv",
                "inventory_stock.csv",
            ],
            "targets": [
                "Transaksi kasir toko fisik (delimiter titik koma)",
                "Master data SKU, nama item, dan format harga",
                "Data log klaim garansi dan pengembalian barang",
                "Jumlah persediaan barang per cabang gudang/toko",
            ],
            "correct_mapping": {
                "offline_pos_orders.csv": "Transaksi kasir toko fisik (delimiter titik koma)",
                "products_catalog.csv": "Master data SKU, nama item, dan format harga",
                "returns_warranty.csv": "Data log klaim garansi dan pengembalian barang",
                "inventory_stock.csv": "Jumlah persediaan barang per cabang gudang/toko",
            },
            "points": 25,
        },
        "fill_one_word": {
            "task_id": "m1_fill_1",
            "instruction": "Lengkapi parameter pandas untuk menangani file POS dengan pemisah titik koma (;):",
            "code_snippet": "df_pos = pd.read_csv(file_buffer, sep='___')",
            "correct_keywords": [";"],
            "points": 20,
            "hints": {
                1: "Karakter pemisah untuk file CSV POS ini adalah tanda baca khusus.",
                2: "Gunakan tanda titik koma (;) di dalam tanda kutip.",
                3: "Ketik ';' (titik koma).",
            },
        },
        "script_task": {
            "task_id": "m1_script_1",
            "instruction": "Ganti '___' dengan atribut pandas yang tepat untuk mengambil dimensi baris dan kolom tabel.",
            "starter_code": """# Ganti ___ dengan atribut dimensi DataFrame yang benar
summary = {}
for name, df in raw_dfs.items():
    summary[name] = df.___

print(summary)
""",
            "hints": {
                1: "Atribut dimensi di pandas mengembalikan tuple (jumlah_baris, jumlah_kolom).",
                2: "Gunakan atribut `.shape` (tanpa tanda kurung).",
                3: "Lengkapi kode menjadi `summary[name] = df.shape`.",
            },
            "points": 40,
        },
    },
    # -------------------------------------------------------------------------
    # MODUL 2: MISSING & DUPLICATES
    # -------------------------------------------------------------------------
    "modul_02": {
        "title": "Missing and Duplicates",
        "description": "Penanganan transaksi retry payment berulang dan imputasi identitas pembeli POS.",
        "mcq": {
            "task_id": "m2_mcq_1",
            "question": "Kolom serial_number bernilai NaN pada produk kategori 'Accessories'. Tindakan paling tepat adalah:",
            "options": [
                "Menghapus seluruh baris transaksi tersebut",
                "Mengisi dengan nilai mean/median",
                "Membiarkan NaN atau memberi label 'NOT_APPLICABLE'",
                "Menghapus kolom serial_number",
            ],
            "correct_index": 2,
            "points": 15,
        },
        "matching": {
            "task_id": "m2_match_1",
            "title": "Jodohkan jenis missing value dengan strategi penanganannya:",
            "sources": [
                "pos_cust_contact bernilai NaN / '-'",
                "customer_id bernilai NaN pada online_orders",
                "city bernilai NaN pada master customers",
                "order_id duplikat akibat retry payment",
            ],
            "targets": [
                "Imputasi dengan nilai konstan 'GUEST_OFFLINE'",
                "Hapus baris karena foreign key pembeli tidak teridentifikasi",
                "Imputasi dengan label 'UNKNOWN'",
                "Hapus baris duplikat berbasis subset ['order_id']",
            ],
            "correct_mapping": {
                "pos_cust_contact bernilai NaN / '-'": "Imputasi dengan nilai konstan 'GUEST_OFFLINE'",
                "customer_id bernilai NaN pada online_orders": "Hapus baris karena foreign key pembeli tidak teridentifikasi",
                "city bernilai NaN pada master customers": "Imputasi dengan label 'UNKNOWN'",
                "order_id duplikat akibat retry payment": "Hapus baris duplikat berbasis subset ['order_id']",
            },
            "points": 25,
        },
        "fill_one_word": {
            "task_id": "m2_fill_1",
            "instruction": "Lengkapi method untuk menghapus duplikasi dengan mempertahankan kemunculan pertama:",
            "code_snippet": "df_online = df_online.drop_duplicates(subset=['order_id'], keep='___')",
            "correct_keywords": ["first"],
            "points": 20,
            "hints": {
                1: "Parameter ini menentukan baris mana yang akan disimpan saat duplikat ditemukan.",
                2: "Gunakan kata bahasa Inggris yang berarti 'pertama'.",
                3: "Ketik 'first'.",
            },
        },
        "script_task": {
            "task_id": "m2_script_1",
            "instruction": "Lengkapi '___' untuk menghapus duplikasi online_orders dan imputasi kontak kosong pada POS.",
            "starter_code": """# 1. Hapus duplikasi order_id dengan mempertahankan baris pertama
df_online_dedup = df_online.drop_duplicates(subset=['order_id'], keep='___')

# 2. Imputasi kontak pembeli kasir POS yang kosong/anonim
df_pos_imputed = df_pos.copy()
df_pos_imputed['pos_cust_contact'] = (
    df_pos_imputed['pos_cust_contact']
    .___( 'GUEST_OFFLINE' )
    .replace(['-', 'GUEST', 'NON_MEMBER', '0000'], 'GUEST_OFFLINE')
)
""",
            "hints": {
                1: "Parameter deduplikasi awal adalah 'first'.",
                2: "Fungsi untuk mengisi missing value (NaN) di pandas adalah `fillna`.",
                3: "Gunakan `keep='first'` dan `.fillna('GUEST_OFFLINE')`.",
            },
            "points": 40,
        },
    },
    # -------------------------------------------------------------------------
    # MODUL 3: STANDARDIZATION & REGEX
    # -------------------------------------------------------------------------
    "modul_03": {
        "title": "Standardization and Regex",
        "description": "Regex pembersihan harga mata uang, standardisasi nomor HP, dan parsing tanggal.",
        "mcq": {
            "task_id": "m3_mcq_1",
            "question": "Pola Regex yang tepat untuk mencocokkan karakter non-digit adalah:",
            "options": ["r'[^0-9]'", "r'[a-zA-Z]'", "r'\\d+'", "r'[\\s,.]'"],
            "correct_index": 0,
            "points": 15,
        },
        "matching": {
            "task_id": "m3_match_1",
            "title": "Jodohkan format data mentah dengan direktif strptime yang sesuai:",
            "sources": [
                "2026-03-15 14:30:00",
                "15/03/2026",
                "15-Mar-2026",
                "2026/03/15",
            ],
            "targets": [
                "%Y-%m-%d %H:%M:%S",
                "%d/%m/%Y",
                "%d-%b-%Y",
                "%Y/%m/%d",
            ],
            "correct_mapping": {
                "2026-03-15 14:30:00": "%Y-%m-%d %H:%M:%S",
                "15/03/2026": "%d/%m/%Y",
                "15-Mar-2026": "%d-%b-%Y",
                "2026/03/15": "%Y/%m/%d",
            },
            "points": 25,
        },
        "fill_one_word": {
            "task_id": "m3_fill_1",
            "instruction": "Lengkapi method untuk mengubah kolom string menjadi tipe datetime:",
            "code_snippet": "df_pos['tx_datetime'] = pd.___(df_pos['transaction_date'], format='%d/%m/%Y')",
            "correct_keywords": ["to_datetime"],
            "points": 20,
            "hints": {
                1: "Fungsi di modul pandas untuk parsing tanggal berkaitan dengan konversi waktu.",
                2: "Awali dengan 'to_' diikuti kata 'datetime'.",
                3: "Ketik 'to_datetime'.",
            },
        },
        "script_task": {
            "task_id": "m3_script_1",
            "instruction": "Lengkapi '___' pada tipe data integer, regex replace, dan parsing datetime.",
            "starter_code": """# 1. Bersihkan raw_price menjadi Integer murni di kolom clean_price
df_products_clean = df_products.copy()
df_products_clean['clean_price'] = (
    df_products_clean['raw_price']
    .astype(str)
    .str.replace(r',00$', '', regex=True)
    .str.replace(r'[^0-9]', '', regex=True)
    .astype('___')  # int64
)

# 2. Hapus karakter non-angka pada nomor telepon
df_customers_clean = df_customers.copy()
df_customers_clean['clean_phone'] = (
    df_customers_clean['contact_phone']
    .astype(str)
    .str.replace(r'[^0-9]', '', regex=___)  # True
)

# 3. Parsing tanggal transaksi POS
df_pos_clean = df_pos.copy()
df_pos_clean['tx_datetime'] = pd.to_datetime(df_pos_clean['transaction_date'], format='___')  # %d/%m/%Y
""",
            "hints": {
                1: "Gunakan tipe 'int64' untuk mengonversi harga ke bilangan bulat, parameter regex bernilai True.",
                2: "Format tanggal DD/MM/YYYY diwakili oleh simbol direktif waktu standar.",
                3: "Gunakan 'int64', True, dan '%d/%m/%Y'.",
            },
            "points": 40,
        },
    },
    # -------------------------------------------------------------------------
    # MODUL 4: OMNICHANNEL MERGE
    # -------------------------------------------------------------------------
    "modul_04": {
        "title": "Omnichannel Merge",
        "description": "Harmonisasi nama kolom, penggabungan baris (union), dan left join katalog SKU.",
        "mcq": {
            "task_id": "m4_mcq_1",
            "question": "Jenis join apa yang wajib digunakan saat menggabungkan transaksi dengan katalog agar transaksi tidak hilang meski SKU belum ada di katalog?",
            "options": ["INNER JOIN", "LEFT JOIN", "RIGHT JOIN", "CROSS JOIN"],
            "correct_index": 1,
            "points": 15,
        },
        "matching": {
            "task_id": "m4_match_1",
            "title": "Jodohkan nama kolom POS dengan standar kolom Online:",
            "sources": [
                "pos_invoice_no",
                "pos_sku_code",
                "pos_cust_contact",
                "store_branch",
            ],
            "targets": [
                "order_id",
                "sku_id",
                "customer_ref",
                "location_ref",
            ],
            "correct_mapping": {
                "pos_invoice_no": "order_id",
                "pos_sku_code": "sku_id",
                "pos_cust_contact": "customer_ref",
                "store_branch": "location_ref",
            },
            "points": 25,
        },
        "fill_one_word": {
            "task_id": "m4_fill_1",
            "instruction": "Lengkapi fungsi pandas untuk menumpuk baris DataFrame secara vertikal:",
            "code_snippet": "df_all = pd.__([df1, df2], ignore_index=True)",
            "correct_keywords": ["concat"],
            "points": 20,
            "hints": {
                1: "Fungsi pandas untuk menggabungkan beberapa DataFrame secara vertikal.",
                2: "Nama fungsinya adalah singkatan dari concatenation.",
                3: "Ketik 'concat'.",
            },
        },
        "script_task": {
            "task_id": "m4_script_1",
            "instruction": "Lengkapi '___' pada fungsi penggabungan vertikal dan jenis relasi merge.",
            "starter_code": """# 1. Tambahkan label channel
df_online_prep = df_online.rename(columns={'customer_id': 'customer_ref', 'warehouse_code': 'location_ref'}).copy()
df_online_prep['channel'] = 'ONLINE'

df_pos_prep = df_pos.rename(columns={
    'pos_invoice_no': 'order_id',
    'pos_sku_code': 'sku_id',
    'pos_cust_contact': 'customer_ref',
    'store_branch': 'location_ref',
    'quantity_sold': 'qty'
}).copy()
df_pos_prep['channel'] = 'OFFLINE'
if 'discount_rate' not in df_pos_prep.columns:
    df_pos_prep['discount_rate'] = 0.0

cols = ['order_id', 'channel', 'customer_ref', 'sku_id', 'qty', 'discount_rate', 'location_ref']

# 2. Gabungkan transaksi vertikal
df_omnichannel = pd.___(
    [df_online_prep[[c for c in cols if c in df_online_prep.columns]],
     df_pos_prep[[c for c in cols if c in df_pos_prep.columns]]],
    ignore_index=True
)

# 3. Left Join dengan katalog SKU
df_master_enriched = df_omnichannel.merge(
    df_products[['product_id', 'product_name', 'category', 'clean_price' if 'clean_price' in df_products.columns else 'cost_price']],
    left_on='sku_id',
    right_on='product_id',
    how='___'
)
""",
            "hints": {
                1: "Gunakan `pd.concat` untuk penggabungan vertikal baris.",
                2: "Gunakan `how='left'` agar seluruh transaksi tetap terjaga.",
                3: "Gunakan `pd.concat` dan `how='left'`.",
            },
            "points": 40,
        },
    },
    # -------------------------------------------------------------------------
    # MODUL 5: BUSINESS RULES & OUTLIERS
    # -------------------------------------------------------------------------
    "modul_05": {
        "title": "Business Rules and Outliers",
        "description": "Filtering kuantitas tidak valid, pembatasan diskon, dan deteksi IQR bulk orders.",
        "mcq": {
            "task_id": "m5_mcq_1",
            "question": "Rumus batas atas (Upper Fence) metode IQR untuk mendeteksi outlier adalah:",
            "options": [
                "Q3 + 1.5 * IQR",
                "Q1 - 1.5 * IQR",
                "Mean + 3 * StdDev",
                "Median + 2 * IQR",
            ],
            "correct_index": 0,
            "points": 15,
        },
        "matching": {
            "task_id": "m5_match_1",
            "title": "Jodohkan jenis anomali data dengan perlakuan pembersihannya:",
            "sources": [
                "qty <= 0 (Kuantitas minus/nol)",
                "discount_rate > 1.0 (Diskon > 100%)",
                "Klaim garansi sebelum tanggal order",
                "qty > 50 (Pembelian borongan/scalper)",
            ],
            "targets": [
                "Hapus baris karena data input korup/batal",
                "Capping ke nilai maksimum 1.0 atau sesuaikan ke nilai wajar",
                "Flagging data sebagai klaim tidak valid",
                "Pisahkan ke tabel audit B2B / Reseller",
            ],
            "correct_mapping": {
                "qty <= 0 (Kuantitas minus/nol)": "Hapus baris karena data input korup/batal",
                "discount_rate > 1.0 (Diskon > 100%)": "Capping ke nilai maksimum 1.0 atau sesuaikan ke nilai wajar",
                "Klaim garansi sebelum tanggal order": "Flagging data sebagai klaim tidak valid",
                "qty > 50 (Pembelian borongan/scalper)": "Pisahkan ke tabel audit B2B / Reseller",
            },
            "points": 25,
        },
        "fill_one_word": {
            "task_id": "m5_fill_1",
            "instruction": "Lengkapi operator untuk menyaring baris dengan kuantitas positif:",
            "code_snippet": "df_valid = df.loc[df['qty'] ___ 0]",
            "correct_keywords": [">"],
            "points": 20,
            "hints": {
                1: "Gunakan operator perbandingan untuk memeriksa nilai lebih besar dari.",
                2: "Simbol menghadap ke kanan untuk menandakan positif.",
                3: "Ketik '>'.",
            },
        },
        "script_task": {
            "task_id": "m5_script_1",
            "instruction": "Lengkapi '___' pada kondisi filter kuantitas dan pembatasan diskon.",
            "starter_code": """# 1. Filter hanya transaksi dengan kuantitas > 0
df_clean = df_omnichannel[df_omnichannel['qty'] ___ 0].copy()

# 2. Capping nilai diskon maksimal 1.0 (100%)
df_clean['discount_rate'] = df_clean['discount_rate'].clip(lower=0.0, upper=___)

# 3. Hitung batasan IQR untuk menandai pembeli borongan (bulk)
q1 = df_clean['qty'].quantile(0.25)
q3 = df_clean['qty'].quantile(0.75)
iqr = q3 - q1
upper_limit = q3 + (1.5 * iqr)

df_clean['is_bulk_buyer'] = df_clean['qty'] > upper_limit
""",
            "hints": {
                1: "Operator perbandingan lebih besar dari nol adalah `>`.",
                2: "Nilai upper untuk clip diskon maksimal adalah `1.0`.",
                3: "Gunakan `>` untuk filter dan `1.0` untuk batas upper clip.",
            },
            "points": 40,
        },
    },
    # -------------------------------------------------------------------------
    # MODUL 6: VALIDATION & EXPORT
    # -------------------------------------------------------------------------
    "modul_06": {
        "title": "Validation and Export",
        "description": "Profiling akhir, agregasi bisnis omnichannel, dan ekspor master ke Parquet.",
        "mcq": {
            "task_id": "m6_mcq_1",
            "question": "Mengapa format Apache Parquet lebih efisien daripada CSV untuk master dataset analitik?",
            "options": [
                "Parquet menyimpan skema native dan mendukung kompresi kolom efisien",
                "Parquet berorientasi baris murni",
                "Parquet dapat diedit langsung via Notepad",
                "Parquet tidak memerlukan engine pembaca khusus",
            ],
            "correct_index": 0,
            "points": 15,
        },
        "matching": {
            "task_id": "m6_match_1",
            "title": "Jodohkan dimensi mutu data dengan pemeriksaannya:",
            "sources": [
                "Completeness (Kelengkapan)",
                "Uniqueness (Keunikan)",
                "Validity (Kesesuaian Aturan)",
                "Consistency (Konsistensi)",
            ],
            "targets": [
                "Persentase nilai null pada kolom wajib = 0%",
                "Tidak ada duplicate values pada primary key order_id",
                "Rentang nilai harga > 0 dan diskon antara 0 s.d. 1",
                "Format tanggal seragam di seluruh channel penjualan",
            ],
            "correct_mapping": {
                "Completeness (Kelengkapan)": "Persentase nilai null pada kolom wajib = 0%",
                "Uniqueness (Keunikan)": "Tidak ada duplicate values pada primary key order_id",
                "Validity (Kesesuaian Aturan)": "Rentang nilai harga > 0 dan diskon antara 0 s.d. 1",
                "Consistency (Konsistensi)": "Format tanggal seragam di seluruh channel penjualan",
            },
            "points": 25,
        },
        "fill_one_word": {
            "task_id": "m6_fill_1",
            "instruction": "Lengkapi method pandas untuk ekspor ke Parquet:",
            "code_snippet": "df_clean.to____('clean_master.parquet', index=False)",
            "correct_keywords": ["parquet"],
            "points": 20,
            "hints": {
                1: "Method ekspor Pandas diawali dengan awalan 'to_'.",
                2: "Format target penyimpanan adalah file terkompresi Apache.",
                3: "Ketik 'parquet'.",
            },
        },
        "script_task": {
            "task_id": "m6_script_1",
            "instruction": "Lengkapi '___' untuk menghitung total pendapatan kotor (gross revenue) per saluran.",
            "starter_code": """# 1. Hitung pendapatan kotor per baris transaksi
unit_col = 'clean_price' if 'clean_price' in df_master.columns else 'unit_price'
df_master['gross_revenue'] = df_master['qty'] * df_master[unit_col]

# 2. Agregasi total revenue berdasarkan channel ('ONLINE' vs 'OFFLINE')
channel_summary = df_master.groupby('channel')['gross_revenue'].___()

print(channel_summary)
""",
            "hints": {
                1: "Fungsi agregasi untuk menjumlahkan nilai total secara keseluruhan.",
                2: "Gunakan fungsi `.sum()` di akhir pemanggilan groupby.",
                3: "Lengkapi dengan `.sum()`.",
            },
            "points": 40,
        },
    },
}
