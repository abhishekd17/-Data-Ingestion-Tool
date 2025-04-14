import requests

host = "v2yxl8xjud.us-east1.gcp.clickhouse.cloud"
port = "8443"
user = "default"
password = "c4Cx6.6.AFWhi"

url = f"https://{host}:{port}/"
headers = {"X-ClickHouse-User": user, "X-ClickHouse-Key": password}

query = "SHOW DATABASES"
response = requests.get(url, params={"query": query}, headers=headers, verify=True)
print("Databases:", response.text)

query = "SELECT name FROM system.tables WHERE database = 'mydb'"
response = requests.get(url, params={"query": query}, headers=headers, verify=True)
print("Tables in mydb:", response.text)

query = "DESCRIBE TABLE mydb.uk_price_paid"
response = requests.get(url, params={"query": query}, headers=headers, verify=True)
print("Describe uk_price_paid:", response.text)