# generate_raw_data.py
import datetime
import io
import os
import random
import zipfile
import numpy as np
import pandas as pd

# 1. Set Seed & Direktori
np.random.seed(42)
random.seed(42)
os.makedirs("data/raw", exist_ok=True)

START_DATE = datetime.datetime(2026, 1, 1, 8, 0, 0)
END_DATE = datetime.datetime(2026, 6, 30, 22, 0, 0)
TOTAL_SECONDS = int((END_DATE - START_DATE).total_seconds())


def random_date_iso():
    sec = random.randint(0, TOTAL_SECONDS)
    return (START_DATE + datetime.timedelta(seconds=sec)).strftime(
        "%Y-%m-%d %H:%M:%S"
    )


def random_date_dmy():
    sec = random.randint(0, TOTAL_SECONDS)
    return (START_DATE + datetime.timedelta(seconds=sec)).strftime("%d/%m/%Y")


# -------------------------------------------------------------------------
# 2. Generator Tabel 1: products_catalog.csv
# -------------------------------------------------------------------------
categories = {
    "Smartphone": [
        ("Samsung Galaxy S24", 13999000, True),
        ("iPhone 15 Pro", 18499000, True),
        ("Xiaomi 14", 11999000, True),
        ("Oppo Reno 11", 5999000, True),
        ("Vivo V30", 5499000, True),
        ("Infinix Note 40", 2499000, True),
    ],
    "Laptop": [
        ("Asus ROG Zephyrus", 28999000, True),
        ("MacBook Air M3", 17999000, True),
        ("Lenovo Legion 5", 19499000, True),
        ("Acer Swift Go 14", 11499000, True),
        ("HP Pavilion 15", 9999000, True),
    ],
    "Audio": [
        ("Sony WH-1000XM5", 4999000, False),
        ("AirPods Pro Gen 2", 3799000, False),
        ("JBL Flip 6 Speaker", 1699000, False),
        ("Bose QuietComfort", 5299000, False),
    ],
    "Home Appliance": [
        ("Polytron Kulkas 2 Pintu", 3499000, False),
        ("LG Mesin Cuci Front Load", 6199000, False),
        ("Sharp Smart TV 43 Inch", 3899000, False),
        ("Philips Air Fryer XL", 1499000, False),
        ("Miyako Rice Cooker", 329000, False),
    ],
    "Accessories": [
        ("Anker Powerbank 20000mAh", 450000, False),
        ("Baseus USB-C Fast Cable", 79000, False),
        ("Sandisk Flashdisk 128GB", 145000, False),
        ("Logitech Wireless Mouse", 229000, False),
    ],
}

products_data = []
sku_counter = 101

for cat, items in categories.items():
    for name, base_price, req_imei in items:
        # Generate multiple variant SKU
        for var in ["Standard", "Pro", "Max"] if cat != "Accessories" else [""]:
            p_name = f"{name} {var}".strip()
            sku = f"SKU-EL-{sku_counter}"
            sku_counter += 1

            # Variasi harga kotor (dirty formatting)
            price_variant = int(
                base_price * (1.15 if var == "Pro" else 1.3 if var == "Max" else 1.0)
            )
            cost_price = int(price_variant * 0.75)

            # Pola string kotor
            style = random.choice(["rp_dot", "rp_space", "idr_comma", "clean", "rp_cents"])
            if style == "rp_dot":
                raw_price = f"Rp. {price_variant:,.0f}".replace(",", ".")
            elif style == "rp_space":
                raw_price = f"Rp {price_variant}"
            elif style == "idr_comma":
                raw_price = f"IDR {price_variant:,}"
            elif style == "rp_cents":
                raw_price = f"Rp {price_variant:,.0f},00".replace(",", ".")
            else:
                raw_price = str(price_variant)

            # Spasi kotor pada nama produk
            if random.random() < 0.2:
                p_name = f"  {p_name}   "

            products_data.append(
                {
                    "product_id": sku,
                    "product_name": p_name,
                    "category": cat,
                    "raw_price": raw_price,
                    "cost_price": cost_price,
                    "requires_serial_number": req_imei,
                }
            )

df_products = pd.DataFrame(products_data)

# -------------------------------------------------------------------------
# 3. Generator Tabel 2: customers.csv
# -------------------------------------------------------------------------
first_names = ["Budi", "Siti", "Ahmad", "Dewi", "Eko", "Rina", "Reza", "Putri", "Hendra", "Maya", "Dian", "Agus", "Fajar", "Linda"]
last_names = ["Santoso", "Wijaya", "Kusuma", "Pratama", "Saputra", "Utami", "Nugroho", "Wahyudi", "Siregar", "Lestari", "Hidayat"]
cities = ["Jakarta Selatan", "Jakarta Barat", "Surabaya", "Bandung", "Medan", "Semarang", "Tangerang", "Bekasi", "Depok", "Yogyakarta"]

customers_data = []
for i in range(1, 801):
    c_id = f"CUST-{i:04d}"
    fname = random.choice(first_names)
    lname = random.choice(last_names)
    full_name = f"{fname} {lname}"

    # Variasi format nomor HP kotor
    base_num = f"8{random.randint(11, 99)}{random.randint(1000000, 9999999)}"
    style = random.choice(["plus62", "zero", "dash", "spaces", "invalid"])
    if style == "plus62":
        phone = f"+62{base_num}"
    elif style == "zero":
        phone = f"0{base_num}"
    elif style == "dash":
        phone = f"0{base_num[:3]}-{base_num[3:7]}-{base_num[7:]}"
    elif style == "spaces":
        phone = f"62 {base_num[:3]} {base_num[3:7]} {base_num[7:]}"
    else:
        phone = "INVALID_CONTACT" if random.random() < 0.05 else f"0{base_num}"

    # Variasi email kotor
    email_name = f"{fname.lower()}.{lname.lower()}{random.randint(1, 999)}"
    domain = random.choice(["gmail.com", "yahoo.com", "outlook.com", "icloud.com"])
    email = f"{email_name}@{domain}"
    if random.random() < 0.15:
        email = email.upper()
    elif random.random() < 0.1:
        email = f" {email}  "
    elif random.random() < 0.05:
        email = np.nan

    city = random.choice(cities) if random.random() > 0.08 else np.nan

    customers_data.append(
        {
            "customer_id": c_id,
            "customer_name": full_name,
            "contact_phone": phone,
            "email_address": email,
            "city": city,
            "registered_date": random_date_iso().split(" ")[0],
        }
    )

df_customers = pd.DataFrame(customers_data)

# -------------------------------------------------------------------------
# 4. Generator Tabel 3: online_orders.csv
# -------------------------------------------------------------------------
online_orders = []
sku_list = df_products["product_id"].tolist()
sku_imei_map = dict(zip(df_products["product_id"], df_products["requires_serial_number"]))
sku_cost_map = dict(zip(df_products["product_id"], df_products["cost_price"]))

for i in range(1, 3001):
    o_id = f"ONL-2026-{i:05d}"
    cust = random.choice(customers_data)["customer_id"]
    sku = random.choice(sku_list)
    timestamp = random_date_iso()

    # Outlier quantity: normal 1-3, anomali 0 / negatif / bulk
    r_qty = random.random()
    if r_qty < 0.02:
        qty = -1
    elif r_qty < 0.04:
        qty = 0
    elif r_qty < 0.07:
        qty = random.randint(50, 100)  # Reseller / scalper
    else:
        qty = random.choices([1, 2, 3], weights=[0.8, 0.15, 0.05])[0]

    # Outlier diskon: normal 0-25%, anomali 120% / 150%
    r_disc = random.random()
    if r_disc < 0.02:
        discount = random.choice([1.2, 1.5])  # Anomali diskon > 100%
    elif r_disc < 0.4:
        discount = random.choice([0.05, 0.10, 0.15, 0.20])
    else:
        discount = 0.0

    # Harga jual & status pembayaran
    unit_price = int(sku_cost_map[sku] * 1.35)
    status = random.choices(["PAID", "PENDING", "CANCELLED", "FAILED"], weights=[0.85, 0.05, 0.06, 0.04])[0]
    warehouse = random.choice(["WH-JKT-UTARA", "WH-SBY-RUNGKUT", "WH-BDG-SOETTA"])

    # Serial number / IMEI
    if sku_imei_map[sku]:
        serial_no = f"SN-ONL-{random.randint(100000000, 999999999)}" if random.random() > 0.1 else np.nan
    else:
        serial_no = np.nan

    online_orders.append(
        {
            "order_id": o_id,
            "customer_id": cust,
            "sku_id": sku,
            "order_timestamp": timestamp,
            "qty": qty,
            "unit_price": unit_price,
            "discount_rate": discount,
            "payment_status": status,
            "warehouse_code": warehouse,
            "serial_number": serial_no,
        }
    )

# Suntikkan transaksi duplikat akibat retry payment loop (~4% baris duplikat)
num_dupes = 120
dupe_rows = random.sample(online_orders, num_dupes)
online_orders.extend(dupe_rows)
random.shuffle(online_orders)
df_online = pd.DataFrame(online_orders)

# -------------------------------------------------------------------------
# 5. Generator Tabel 4: offline_pos_orders.csv
# -------------------------------------------------------------------------
pos_orders = []
branches = ["STORE-JKT-CP", "STORE-JKT-GI", "STORE-SBY-TP", "STORE-BDG-PVJ", "STORE-MDN-SUN"]
cashiers = ["CASHIER-01", "CASHIER-02", "CASHIER-03", "CASHIER-04"]

for i in range(1, 2501):
    pos_id = f"POS-TX-{i:05d}"
    sku = random.choice(sku_list)
    tx_date = random_date_dmy()
    store = random.choice(branches)
    cashier = random.choice(cashiers)

    # Identitas di POS: 45% Guest / Tanpa kontak
    if random.random() < 0.45:
        cust_phone = random.choice([np.nan, "GUEST", "NON_MEMBER", "-", "0000"])
    else:
        cust_phone = f"08{random.randint(11, 99)}{random.randint(1000000, 9999999)}"

    qty = random.choices([1, 2, 3, 4], weights=[0.82, 0.12, 0.04, 0.02])[0]
    unit_price = int(sku_cost_map[sku] * 1.35)
    total_val = unit_price * qty
    raw_subtotal = f"Rp {total_val:,.0f}".replace(",", ".")

    # Serial number di POS
    if sku_imei_map[sku]:
        serial_no = f"SN-POS-{random.randint(100000000, 999999999)}" if random.random() > 0.05 else np.nan
    else:
        serial_no = np.nan

    payment_method = random.choice(["CASH", "EDC_BCA", "EDC_MANDIRI", "QRIS"])

    pos_orders.append(
        {
            "pos_invoice_no": pos_id,
            "pos_sku_code": sku,
            "pos_cust_contact": cust_phone,
            "transaction_date": tx_date,
            "store_branch": store,
            "cashier_id": cashier,
            "quantity_sold": qty,
            "raw_subtotal": raw_subtotal,
            "pos_serial_number": serial_no,
            "payment_type": payment_method,
        }
    )

df_pos = pd.DataFrame(pos_orders)

# -------------------------------------------------------------------------
# 6. Generator Tabel 5: inventory_stock.csv
# -------------------------------------------------------------------------
locations = ["WH-JKT-UTARA", "WH-SBY-RUNGKUT", "WH-BDG-SOETTA"] + branches
inventory_data = []

for loc in locations:
    for sku in sku_list:
        stock_good = random.randint(5, 150)
        stock_reserved = random.randint(0, min(15, stock_good))
        damaged = random.randint(0, 4) if random.random() < 0.3 else 0
        last_restock = random_date_iso().split(" ")[0]

        inventory_data.append(
            {
                "facility_id": loc,
                "sku_id": sku,
                "available_stock": stock_good - stock_reserved,
                "reserved_stock": stock_reserved,
                "damaged_stock": damaged,
                "last_restock_date": last_restock,
            }
        )

df_inventory = pd.DataFrame(inventory_data)

# -------------------------------------------------------------------------
# 7. Generator Tabel 6: returns_warranty.csv
# -------------------------------------------------------------------------
returns_data = []
eligible_online = df_online[df_online["payment_status"] == "PAID"].to_dict("records")
sampled_orders = random.sample(eligible_online, 350)

for i, order in enumerate(sampled_orders, 1):
    ret_id = f"RET-2026-{i:04d}"
    ref_order = order["order_id"]
    order_dt = datetime.datetime.strptime(order["order_timestamp"], "%Y-%m-%d %H:%M:%S")

    # Anomali: 6% klaim retur terjadi sebelum tanggal order dibuat
    if random.random() < 0.06:
        claim_dt = order_dt - datetime.timedelta(days=random.randint(1, 15))
    else:
        claim_dt = order_dt + datetime.timedelta(days=random.randint(1, 45))

    reason = random.choice(["DEFECTIVE_HARDWARE", "WRONG_COLOR", "BUYER_REMORSE", "DAMAGED_IN_SHIPPING"])
    status = random.choice(["APPROVED", "REJECTED", "INVESTIGATING"])

    returns_data.append(
        {
            "return_id": ret_id,
            "ref_order_id": ref_order,
            "claim_timestamp": claim_dt.strftime("%Y-%m-%d %H:%M:%S"),
            "return_reason": reason,
            "claim_status": status,
        }
    )

df_returns = pd.DataFrame(returns_data)

# -------------------------------------------------------------------------
# 8. Kompresi ke dalam data/raw/electronics_omnichannel.zip
# -------------------------------------------------------------------------
zip_path = "data/raw/electronics_omnichannel.zip"
with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zip_file:
    zip_file.writestr("products_catalog.csv", df_products.to_csv(index=False))
    zip_file.writestr("customers.csv", df_customers.to_csv(index=False))
    zip_file.writestr("online_orders.csv", df_online.to_csv(index=False))
    # POS orders menggunakan delimiter titik koma (;) untuk menguji deteksi delimiter
    zip_file.writestr("offline_pos_orders.csv", df_pos.to_csv(index=False, sep=";"))
    zip_file.writestr("inventory_stock.csv", df_inventory.to_csv(index=False))
    zip_file.writestr("returns_warranty.csv", df_returns.to_csv(index=False))

print(f"Berhasil! Dataset 6 bulan telah dibuat di: {zip_path}")
print(f"Total tabel di dalam ZIP: 6 file CSV")
