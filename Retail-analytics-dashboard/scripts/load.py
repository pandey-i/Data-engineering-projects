import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

# DB config
load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")


def load_data():
    print("DEBUG HOST:", DB_HOST)
    print("DEBUG PORT:", DB_PORT)

    engine = create_engine(
        f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    df = pd.read_csv("data/processed/final_data.csv")

    print("Loaded processed data")

    # DIM_CUSTOMERS
    dim_customers = df[["customer_id"]].drop_duplicates()
    dim_customers.to_sql("dim_customers", engine, if_exists="replace", index=False)
    print("dim_customers created")

    # DIM_PRODUCTS
    if "product_id" in df.columns:
        dim_products = df[["product_id", "title", "category", "price"]].drop_duplicates()
        dim_products.to_sql("dim_products", engine, if_exists="replace", index=False)
        print("dim_products created")

    # FACT_ORDERS
    fact_orders = df.copy()
    fact_orders.to_sql("fact_orders", engine, if_exists="replace", index=False)
    print("fact_orders created")