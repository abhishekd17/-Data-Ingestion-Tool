import requests

host = "v2yxl8xjud.us-east1.gcp.clickhouse.cloud"
port = "8443"
user = "default"
password = "c4Cx6.6.AFWhi"

url = f"https://{host}:{port}/"
headers = {"X-ClickHouse-User": user, "X-ClickHouse-Key": password}

query = "CREATE DATABASE IF NOT EXISTS mydb"
response = requests.post(url, params={"query": query}, headers=headers, verify=True)
print("Create Database:", response.text if response.status_code != 200 else "Success")

query = """
CREATE TABLE IF NOT EXISTS mydb.uk_price_paid (
    price UInt32,
    date Date,
    postcode String
) ENGINE = MergeTree
ORDER BY date
"""
response = requests.post(url, params={"query": query}, headers=headers, verify=True)
print("Create Table:", response.text if response.status_code != 200 else "Success")

query = "INSERT INTO mydb.uk_price_paid VALUES (100000, '2020-01-01', 'AB1 2CD'), (200000, '2020-02-01', 'XY2 3ZW')"
response = requests.post(url, params={"query": query}, headers=headers, verify=True)
print("Insert Data:", response.text if response.status_code != 200 else "Success")