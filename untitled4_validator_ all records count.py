#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 11 11:04:54 2024

@author: davidsandeep
"""

import os
import pandas as pd
import time
from tkinter import Tk
from tkinter.filedialog import askdirectory, askopenfilename

def detect_delimiter(file_path, compression):
    """Detect the delimiter used in the file."""
    print("="*60)
    print(f"Detecting delimiter in file: {file_path} with compression: {compression}")
    try:
        if compression == 'gzip':
            import gzip
            with gzip.open(file_path, 'rt') as file:
                line = file.readline()
        else:
            with open(file_path, 'rt') as file:
                line = file.readline()
        
        if ',' in line and '|' in line:
            raise ValueError("File contains both commas and pipes.")
        elif ',' in line:
            delimiter = ','
        elif '|' in line:
            delimiter = '|'
        else:
            raise ValueError("File does not contain a recognized delimiter.")
        
        print("="*60)
        print(f"Delimiter detected: {delimiter}")
        return delimiter
    except Exception as e:
        print("="*60)
        print(f"Error detecting delimiter in {file_path}: {e}")
        return None

def count_rows(file_path, compression, delimiter):
    """Count the total number of rows in the file efficiently."""
    print("="*60)
    print(f"Counting rows in file: {file_path} with compression: {compression}")
    if compression == 'gzip':
        import gzip
        with gzip.open(file_path, 'rt') as f:
            row_count = sum(1 for _ in f) - 1  # Exclude last row count
    else:
        with open(file_path, 'rt') as f:
            row_count = sum(1 for _ in f) - 1  # Exclude last row count
    print("="*60)
    print(f"Total rows (excluding last row): {row_count}")
    return row_count

def get_last_row(file_path, compression, delimiter):
    """Get the last row of the file efficiently."""
    print("="*60)
    print(f"Getting last row in file: {file_path} with compression: {compression}")
    if compression == 'gzip':
        import gzip
        with gzip.open(file_path, 'rt') as f:
            last_line = None
            for last_line in f:
                pass
            last_row = last_line.strip().split(delimiter)
    else:
        with open(file_path, 'rt') as f:
            last_line = None
            for last_line in f:
                pass
            last_row = last_line.strip().split(delimiter)
    print("="*60)
    print(f"Last row: {last_row}")
    return last_row

def load_expected_columns(file_path):
    """Load the expected columns from a file."""
    print("="*60)
    print(f"Loading expected columns from file: {file_path}")
    with open(file_path, 'r') as f:
        expected_columns = [line.strip() for line in f if line.strip()]  # Read non-empty lines
    print("="*60)
    print(f"Expected columns: {expected_columns}")
    return expected_columns

def validate_file(file_path):
    """Validate a single CSV or gzip-compressed values file."""
    start_time = time.time()
    print("="*60)
    print(f"Validating file: {file_path}")
    try:
        # Determine the compression type based on the file extension
        compression = 'gzip' if file_path.endswith('.gz') else None

        delimiter = detect_delimiter(file_path, compression)
        if not delimiter:
            print("="*60)
            print(f"Skipping file {file_path} due to delimiter detection error.")
            return False

        expected_columns_file = 'expected_columns.txt'
        expected_columns = load_expected_columns(expected_columns_file)

        # Read the first row to get the actual columns
        first_row = pd.read_csv(file_path, nrows=1, compression=compression, delimiter=delimiter)
        actual_columns = first_row.columns.tolist()
        print("="*60)
        print(f"Actual columns: {actual_columns}")

        total_rows = count_rows(file_path, compression, delimiter)
        last_row = get_last_row(file_path, compression, delimiter)

        if actual_columns != expected_columns or not last_row or total_rows != int(last_row[2]):
            print("="*60)
            print(f"Format error detected in {file_path}")
            return False

        elapsed_time = time.time() - start_time
        print("="*60)
        print(f"Scanned {file_path} successfully. Time taken: {elapsed_time:.2f} seconds")
        return True

    except Exception as e:
        print("="*60)
        print(f"Error reading {file_path}: {e}")
        return False

def scan_directory(directory_path):
    """Scan all files in a directory."""
    print("="*60)
    print(f"Scanning directory: {directory_path}")
    valid_files = []
    for root, _, files in os.walk(directory_path):
        for file in files:
            file_path = os.path.join(root, file)
            print("="*60)
            print(f"Processing file: {file_path}")
            print("="*60)
            if validate_file(file_path):
                valid_files.append(file_path)
    print("="*60)
    print(f"Valid files: {valid_files}")
    return valid_files

def save_valid_files(valid_files):
    """Save valid scanned files to a text file, only if there are any valid files."""
    if valid_files:
        print("="*60)
        print("Saving valid scanned files to valid_scanned_files.txt")
        with open("valid_scanned_files.txt", "w") as f:
            for file in valid_files:
                f.write(file + "\n")
        print("="*60)
        print("Valid scanned file names saved to valid_scanned_files.txt")
    else:
        print("="*60)
        print("No valid files to save.")

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
        print("="*60)
        print("Invalid choice. Please run the script again and choose 1 or 2.")
        return

    if not path:
        print("="*60)
        print("No file or directory selected.")
        return

    valid_files = []

    if os.path.isfile(path):
        print("="*60)
        print(f"Selected path is a file: {path}")
        if validate_file(path):
            valid_files.append(path)
    elif os.path.isdir(path):
        print("="*60)
        print(f"Selected path is a directory: {path}")
        valid_files = scan_directory(path)
    else:
        print("="*60)
        print("The selected path is neither a file nor a directory.")

    save_valid_files(valid_files)

if __name__ == "__main__":
    main()
