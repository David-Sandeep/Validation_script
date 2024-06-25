#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 11 11:04:54 2024

@author: davidsandeep
"""
import os
import pandas as pd
import psutil
import time
from tkinter import Tk
from tkinter.filedialog import askdirectory, askopenfilename
import duckdb

def detect_delimiter(file_path):
    """Detect the delimiter used in the file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            line = file.readline()
            if ',' in line and '|' in line:
                raise ValueError("File contains both commas and pipes.")
            elif ',' in line:
                return ','
            elif '|' in line:
                return '|'
            else:
                raise ValueError("File does not contain a recognized delimiter.")
    except Exception as e:
        print(f"Error detecting delimiter in {file_path}: {e}")
        return None

def get_dynamic_chunk_size():
    """Determine chunk size based on available system memory, leaving 1 GB free."""
    mem = psutil.virtual_memory()
    available_memory = mem.available  # in bytes
    reserved_memory = 1 * 1024 * 1024 * 1024  # 1 GB in bytes
    usable_memory = max(available_memory - reserved_memory, 0)  # Ensure it's not negative

    estimated_row_size = 500  # Estimate the memory required for a single row
    chunk_size = usable_memory // estimated_row_size  # Calculate the number of rows per chunk

    return chunk_size

def append_to_scanned_files_info(file_path, time_taken, validation_method):
    """Append validation information to scanned_files_info.csv."""
    if not os.path.exists("scanned_files_info.csv"):
        with open("scanned_files_info.csv", "w") as f:
            f.write("file_path,time_taken,validation_method\n")
    
    with open("scanned_files_info.csv", "a") as f:
        f.write(f"{file_path},{time_taken:.2f},{validation_method}\n")

def validate_file_pandas(file_path):
    """Validate a single CSV or pipe-separated values file using pandas."""
    start_time = time.time()
    try:
        delimiter = detect_delimiter(file_path)
        if delimiter is None:
            print(f"Skipping file {file_path} due to delimiter detection error.")
            return False, 0

        first_chunk = pd.read_csv(file_path, delimiter=delimiter, chunksize=1)
        header = next(first_chunk).columns
        print(f"Header detected in {file_path}: {header}")
        print(f"Delimiter detected: '{delimiter}'")

        chunk_size = get_dynamic_chunk_size()
        print(f"Using dynamic chunk size: {chunk_size:,} rows per chunk")  # Format chunk size with commas

        for chunk in pd.read_csv(file_path, delimiter=delimiter, chunksize=chunk_size):
            if chunk.columns.tolist() != header.tolist():
                print(f"Format error detected in {file_path}")
                return False, 0
            print(f"Processed {len(chunk):,} rows")

        elapsed_time = time.time() - start_time
        print(f"Scanned {file_path} successfully with pandas. Time taken: {elapsed_time:.2f} seconds")

        append_to_scanned_files_info(file_path, elapsed_time, "pandas")
        return True, elapsed_time

    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return False, 0

def validate_file_duckdb(file_path):
    """Validate a single CSV or pipe-separated values file using DuckDB without SQL."""
    start_time = time.time()
    try:
        delimiter = detect_delimiter(file_path)
        if delimiter is None:
            print(f"Skipping file {file_path} due to delimiter detection error.")
            return False, 0

        # Read the file using DuckDB
        conn = duckdb.connect(database=':memory:')
        df = conn.execute(f"SELECT * FROM read_csv_auto('{file_path}', delim='{delimiter}')").fetchdf()

        # Get the header
        header = df.columns.tolist()
        print(f"Header detected in {file_path}: {header}")

        chunk_size = get_dynamic_chunk_size()
        print(f"Using dynamic chunk size: {chunk_size:,} rows per chunk")  # Format chunk size with commas

        offset = 0
        while offset < len(df):
            chunk = df.iloc[offset:offset + chunk_size]
            if chunk.columns.tolist() != header:
                print(f"Format error detected in {file_path}")
                return False, 0
            offset += chunk_size
            print(f"Processed {len(chunk):,} rows")

        elapsed_time = time.time() - start_time
        print(f"Scanned {file_path} successfully with DuckDB. Time taken: {elapsed_time:.2f} seconds")

        append_to_scanned_files_info(file_path, elapsed_time, "duckdb")
        return True, elapsed_time

    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return False, 0

def scan_directory(directory_path, scanned_files):
    """Scan all files in a directory."""
    valid_files = []
    for root, _, files in os.walk(directory_path):
        for file in files:
            file_path = os.path.join(root, file)
            if file_path in scanned_files:
                print(f"Skipping already scanned file: {file_path}")
                continue
            valid_pandas, _ = validate_file_pandas(file_path)
            valid_duckdb, _ = validate_file_duckdb(file_path)
            if valid_pandas and valid_duckdb:
                valid_files.append((file_path))
                scanned_files.add(file_path)
    return valid_files

def main():
    Tk().withdraw()
    print("Do you want to select a file or a directory?")
    print("1. File")
    print("2. Directory")
    choice = input("Enter 1 for file or 2 for directory: ").strip()

    if choice == '1':
        path = askopenfilename(title="Select a file")
    elif choice == '2':
        path = askdirectory(title="Select a directory")
    else:
        print("Invalid choice. Please run the script again and choose 1 or 2.")
        return

    if not path:
        print("No file or directory selected.")
        return

    scanned_files = set()
    valid_files = []
    is_exists=False

    if os.path.exists("scanned_files.txt"):
        with open("scanned_files.txt", "r") as f:
            scanned_files = set(f.read().splitlines())

    if os.path.isfile(path):
        if path  in scanned_files:
            print(f"Skipping already scanned file: {path}")
            is_exists=True
        else:
            valid_pandas, _ = validate_file_pandas(path)
            valid_duckdb, _ = validate_file_duckdb(path)
            if valid_pandas and valid_duckdb:
                valid_files.append(path)
    elif os.path.isdir(path):
        valid_files = scan_directory(path, scanned_files)
    else:
        print("The selected path is neither a file nor a directory.")
    
    
    if not is_exists:
        # Write validated files to scanned_files.txt
        if not os.path.exists("scanned_files.txt"):
            with open("scanned_files.txt", "w") as f:
                for file in valid_files:
                    f.write(file + "\n")
        with open("scanned_files.txt", "a") as f:
            for file in valid_files:
                f.write(file + "\n")
    
        print(f"Scanned files list saved to scanned_files.txt")

if __name__ == "__main__":
    main()
