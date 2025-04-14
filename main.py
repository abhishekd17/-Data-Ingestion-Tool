from fastapi import FastAPI, Form, UploadFile, File
from fastapi.responses import HTMLResponse
import httpx
import csv
import io
import os

app = FastAPI()

# Serve the HTML page
@app.get("/", response_class=HTMLResponse)
async def read_root():
    print("Serving index.html")
    try:
        with open("index.html") as f:
            return f.read()
    except FileNotFoundError:
        print("Error: index.html not found")
        return "Error: index.html not found"

# Connect to ClickHouse and get tables
@app.post("/connect_clickhouse")
def connect_clickhouse(host: str = Form(...), port: str = Form(...), user: str = Form(...), password: str = Form(...)):
    print(f"Connecting to {host}:{port}")
    url = f"https://{host}:{port}/"
    headers = {"X-ClickHouse-User": user, "X-ClickHouse-Key": password}
    query = "SELECT name FROM system.tables WHERE database = 'mydb'"
    try:
        response = httpx.get(url, params={"query": query}, headers=headers, verify=True)
        response.raise_for_status()
        tables = [row.strip() for row in response.text.split("\n") if row]
        print(f"Tables: {tables}")
        return {"tables": tables}
    except httpx.HTTPError as e:
        print(f"Connect error: {str(e)}")
        return {"error": f"Failed to connect: {str(e)}"}

# Get columns of a table
@app.post("/get_columns_clickhouse")
def get_columns_clickhouse(host: str = Form(...), port: str = Form(...), user: str = Form(...), password: str = Form(...), table_name: str = Form(...)):
    print(f"Fetching columns for {table_name}")
    url = f"https://{host}:{port}/"
    headers = {"X-ClickHouse-User": user, "X-ClickHouse-Key": password}
    query = f"DESCRIBE TABLE mydb.{table_name}"
    try:
        response = httpx.get(url, params={"query": query}, headers=headers, verify=True)
        response.raise_for_status()
        columns = [row.split('\t')[0] for row in response.text.split("\n") if row and '\t' in row]
        print(f"Columns: {columns}")
        return {"columns": columns}
    except httpx.HTTPError as e:
        print(f"Columns error: {str(e)}")
        return {"error": f"Failed to fetch columns: {str(e)}"}

# Ingest from ClickHouse to CSV
@app.post("/ingest_clickhouse_to_flatfile")
def ingest_clickhouse_to_flatfile(host: str = Form(...), port: str = Form(...), user: str = Form(...), password: str = Form(...), table_name: str = Form(...), selected_columns: str = Form(...)):
    print(f"Exporting from {table_name}")
    columns = selected_columns.split(',')
    print(f"Columns: {columns}")
    url = f"https://{host}:{port}/"
    headers = {"X-ClickHouse-User": user, "X-ClickHouse-Key": password}
    query = f"SELECT {','.join(columns)} FROM mydb.{table_name} FORMAT CSVWithNames"
    try:
        print("Sending export query")
        response = httpx.get(url, params={"query": query}, headers=headers, verify=True, stream=True)
        response.raise_for_status()
        print("Writing output.csv")
        with open("output.csv", "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print("Counting records")
        with open("output.csv", "r") as f:
            record_count = sum(1 for line in f) - 1
        print(f"Exported {record_count} records")
        return {"record_count": record_count}
    except httpx.HTTPError as e:
        print(f"Export error: {str(e)}")
        return {"error": f"Failed to export: {str(e)}"}

# Upload CSV and get columns
@app.post("/upload_flatfile")
async def upload_flatfile(file: UploadFile = File(...)):
    print("Uploading CSV")
    try:
        content = await file.read()
        if not content:
            print("Empty file")
            return {"error": "Uploaded file is empty"}
        print("Saving temp.csv")
        with open("temp.csv", "wb") as f:
            f.write(content)
        print("Reading headers")
        with open("temp.csv", "r") as f:
            reader = csv.reader(f)
            headers = next(reader, [])
            if not headers:
                print("Empty CSV")
                return {"error": "CSV file is empty or invalid"}
        print(f"Headers: {headers}")
        return {"columns": headers}
    except Exception as e:
        print(f"Upload error: {str(e)}")
        return {"error": f"Failed to process CSV: {str(e)}"}

# Ingest from CSV to ClickHouse
@app.post("/ingest_flatfile_to_clickhouse")
def ingest_flatfile_to_clickhouse(host: str = Form(...), port: str = Form(...), user: str = Form(...), password: str = Form(...), selected_columns: str = Form(...), target_table: str = Form(...)):
    print("Starting ingestion")
    try:
        columns = selected_columns.split(',')
        print(f"Selected columns: {columns}")
        url = f"https://{host}:{port}/"
        headers = {"X-ClickHouse-User": user, "X-ClickHouse-Key": password}
        print("Checking temp.csv")
        if not os.path.exists("temp.csv"):
            print("temp.csv missing")
            return {"error": "No CSV file uploaded. Please upload a file first."}
        print("Reading temp.csv")
        with open("temp.csv", "r") as f:
            reader = csv.reader(f)
            csv_headers = next(reader, [])
            print(f"CSV headers: {csv_headers}")
            if not csv_headers:
                print("Empty CSV")
                return {"error": "CSV file is empty or invalid"}
        print("Validating columns")
        indices = []
        for col in columns:
            if col not in csv_headers:
                print(f"Column {col} not found")
                return {"error": f"Column {col} not found in CSV"}
            indices.append(csv_headers.index(col))
        print(f"Selected indices: {indices}")
        print("Creating schema")
        schema = []
        for col in columns:
            if col == "price":
                schema.append(f"{col} UInt32")
            elif col == "date":
                schema.append(f"{col} Date")
            else:
                schema.append(f"{col} String")
        query = f"CREATE TABLE IF NOT EXISTS mydb.{target_table} ({', '.join(schema)}) ENGINE = MergeTree ORDER BY tuple()"
        print(f"Table query: {query}")
        print("Sending create query")
        response = httpx.post(url, params={"query": query}, headers=headers, verify=True)
        print(f"Create status: {response.status_code}")
        if response.status_code != 200:
            print(f"Create failed: {response.text}")
            return {"error": f"Failed to create table: {response.text}"}
        print("Table created")
        print("Preparing data")
        output = io.StringIO()
        writer = csv.writer(output, lineterminator='\n')
        writer.writerow(columns)
        count = 0
        with open("temp.csv", "r") as f:
            reader = csv.reader(f)
            next(reader)  # Skip header
            for row in reader:
                print(f"Processing row: {row}, length: {len(row)}")
                if not row or len(row) < max(indices) + 1:
                    print(f"Skipping invalid row: {row}")
                    continue
                selected = []
                for i in indices:
                    selected.append(row[i])
                print(f"Selected values: {selected}")
                writer.writerow(selected)
                count += 1
        print(f"Records to insert: {count}")
        if count == 0:
            print("No valid rows")
            return {"error": "No valid rows to insert"}
        data = output.getvalue()
        print(f"Data to insert:\n{data}")
        print("Sending insert query")
        query = f"INSERT INTO mydb.{target_table} FORMAT CSVWithNames"
        response = httpx.post(url, data=data.encode('utf-8'), headers=headers, params={"query": query}, verify=True)
        print(f"Insert status: {response.status_code}")
        if response.status_code != 200:
            print(f"Insert failed: {response.text}")
            return {"error": f"Failed to insert data: {response.text}"}
        print("Insert successful")
        return {"record_count": count}
    except Exception as e:
        print(f"Error: {str(e)}")
        return {"error": f"Processing error: {str(e)}"}
    finally:
        if os.path.exists("temp.csv"):
            print("Deleting temp.csv")
            os.remove("temp.csv")