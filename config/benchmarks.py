# config/benchmarks.py

# Daftar tabel wajib hasil ekstraksi ZIP
EXPECTED_RAW_TABLES = [
    "products_catalog",
    "customers",
    "online_orders",
    "offline_pos_orders",
    "inventory_stock",
    "returns_warranty",
]

# Skema kolom standar untuk dataset transaksi omnichannel gabungan
UNIFIED_TRANSACTION_SCHEMA = [
    "order_id",
    "channel",
    "customer_ref",
    "sku_id",
    "transaction_timestamp",
    "quantity",
    "unit_price",
    "discount_rate",
    "total_amount",
    "serial_number",
    "location_ref",
    "payment_method",
]

# Batasan nilai valid untuk audit aturan bisnis ritel elektronik
BUSINESS_RULES = {
    "min_quantity": 1,
    "max_discount_rate": 1.0,  # Diskon tidak boleh melebihi 100%
    "min_price": 1000,
    "allowed_channels": ["ONLINE", "OFFLINE"],
    "valid_payment_statuses": ["PAID", "COMPLETED", "SETTLED"],
}
