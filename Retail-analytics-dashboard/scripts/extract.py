import requests
import pandas as pd
import os

RAW_PATH = "data/raw/"

def extract_products():
    url="https://dummyjson.com/products"
    response=requests.get(url)

    if response.status_code == 200:
        data=response.json()
        df=pd.DataFrame(data["products"])
        df.to_csv(os.path.join(RAW_PATH,"products.csv"),index=False)
        print("Products data extracted successfully !!")
    else:
        print("Failed to fetch products")

def extract_orders():
    df=pd.read_csv(os.path.join(RAW_PATH,"orders.csv"))
    print("Orders data loaded successfully !!")
    return df

def extract_customers():
    df=pd.read_csv(os.path.join(RAW_PATH,"customers.csv"))
    print("Customers data loaded successfully !!")
    return df

if __name__=="__main__":
    extract_products()
    extract_orders()
    extract_customers()