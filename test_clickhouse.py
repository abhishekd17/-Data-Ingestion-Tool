import requests

# Your ClickHouse Cloud connection details
host = "v2yxl8xjud.us-east1.gcp.clickhouse.cloud"
port = "8443"
user = "default"
password = "c4Cx6.6.AFWhi"

url = f"https://{host}:{port}/"
headers = {"X-ClickHouse-User": user, "X-ClickHouse-Key": password}

# Create table (use POST for modifying queries)
query = """
CREATE TABLE uk_price_paid (
    price UInt32,
    date Date,
    postcode String
) ENGINE = MergeTree
ORDER BY date
"""
response = requests.post(url, params={"query": query}, headers=headers, verify=True)
print("Create Table:", response.text if response.status_code != 200 else "Success")

# Insert data (use POST for modifying queries)
query = "INSERT INTO uk_price_paid VALUES (1000, '2025-01-01', 'RK2 2RK')"
response = requests.post(url, params={"query": query}, headers=headers, verify=True)
print("Insert Data:", response.text if response.status_code != 200 else "Success")

# Check data (use GET for reading queries)
query = "SELECT * FROM uk_price_paid"
response = requests.get(url, params={"query": query}, headers=headers, verify=True)
print("Data:", response.text)