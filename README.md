# Data Ingestion Tool

A web-based application for seamless bidirectional data transfer between CSV files and ClickHouse databases. Built with FastAPI, it allows users to upload CSV files to create and populate ClickHouse tables or export ClickHouse table data to CSV files, with flexible column selection and record counting.

## Project Overview

This tool was developed as a solution for efficient data ingestion and extraction, specifically tailored for handling structured data like property price records (`price`, `date`, `postcode`). It connects to a ClickHouse Cloud instance, supports automatic table creation based on CSV headers, and provides a user-friendly web interface for data operations.

### Features
- **CSV to ClickHouse Import**:
  - Upload a CSV file and select columns to import.
  - Automatically creates a ClickHouse table with appropriate data types (e.g., `UInt32` for `price`, `Date` for `date`, `String` for others).
  - Inserts data and reports the number of records imported.
- **ClickHouse to CSV Export**:
  - Connect to a ClickHouse database and list available tables.
  - Select columns to export and download results as a CSV file.
  - Displays the number of records exported.
- **Web Interface**:
  - Built with FastAPI and HTML/JavaScript for a responsive experience.
  - Supports column selection via checkboxes and real-time feedback.
- **Error Handling**:
  - Validates CSV files, column selections, and ClickHouse connections.
  - Provides clear error messages for issues like missing files or invalid credentials.

## Prerequisites

- **Python 3.8+**: Ensure Python is installed on your system.
- **ClickHouse Cloud Account**: You need a ClickHouse Cloud instance with credentials (host, port, user, password).
- **Git**: Optional, for cloning the repository.
- A web browser (e.g., Chrome, Firefox) to access the interface.

## Setup Instructions

Follow these steps to set up and run the project locally.

1. **Clone the Repository** (if you’re sharing it on GitHub):
   ```bash
   git clone https://github.com/abhishekd17/-Data-Ingestion-Tool.git
   cd zeotap