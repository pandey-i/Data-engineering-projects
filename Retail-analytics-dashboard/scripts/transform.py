import pandas as pd
import numpy as np
import os

RAW_PATH = "data/raw/"
PROCESSED_PATH = "data/processed/"


def transform_data():
    # Load datasets
    products = pd.read_csv(os.path.join(RAW_PATH, "products.csv"))
    orders = pd.read_csv(os.path.join(RAW_PATH, "orders.csv"))
    customers = pd.read_csv(os.path.join(RAW_PATH, "customers.csv"))

    print("Data loaded")

    # --- CLEANING ---
    products.drop_duplicates(inplace=True)
    orders.drop_duplicates(inplace=True)
    customers.drop_duplicates(inplace=True)

    # Fix missing values properly
    products = products.ffill()
    orders = orders.ffill()
    customers = customers.ffill()

    # --- FIX PRODUCT ID ---
    # Rename products id → product_id
    products.rename(columns={"id": "product_id"}, inplace=True)

    # Add product_id to orders (simulation)
    if "product_id" not in orders.columns:
        orders["product_id"] = np.random.choice(products["product_id"], size=len(orders))

    # --- MERGE ---
    merged = orders.merge(customers, on="customer_id", how="left")
    merged = merged.merge(products, on="product_id", how="left")

    # --- FEATURE ENGINEERING ---
    merged["quantity"] = np.random.randint(1, 5, size=len(merged))
    merged["total_revenue"] = merged["price"] * merged["quantity"]

    # Customer order count
    merged["order_count"] = merged.groupby("customer_id")["customer_id"].transform("count")

    # Customer segmentation
    merged["customer_type"] = merged["order_count"].apply(lambda x: "High" if x > 5 else "Low")

    # Save processed data
    output_path = os.path.join(PROCESSED_PATH, "final_data.csv")
    merged.to_csv(output_path, index=False)

    print("Transformation complete → saved to processed folder")


if __name__ == "__main__":
    transform_data()