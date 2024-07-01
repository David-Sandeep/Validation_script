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
    

def check_delimiter_consistency(file_path, compression, delimiter):
    """Check if each line in the file contains the detected delimiter."""
    print("="*60)
    print(f"Checking delimiter consistency in file: {file_path} with compression: {compression}")
    try:
        line_count = 0
        if compression == 'gzip':
            import gzip
            with gzip.open(file_path, 'rt') as f:
                for line in f:
                    line_count += 1
                    if delimiter not in line:
                        raise ValueError(f"Delimiter mismatch detected in file: {file_path} on line {line_count}")
                    if line_count % 10000 == 0:
                        print("="*60)
                        print(f"Checked {line_count} lines so far...the current line is:\n {line}")
        else:
            with open(file_path, 'rt') as f:
                for line in f:
                    line_count += 1
                    if delimiter not in line:
                        raise ValueError(f"Delimiter mismatch detected in file: {file_path} on line {line_count}")
                    if line_count % 10000 == 0:
                        print("="*60)
                        print(f"Checked {line_count} lines so far...the current line is:\n {line}")
        print("="*60)
        print(f"Delimiter consistency check passed for file: {file_path}")
        return True
    except Exception as e:
        print("="*60)
        print(f"Error checking delimiter consistency in {file_path}: {e}")
        return False

    
    


def count_rows(file_path, compression, delimiter):
    """Count the total number of rows in the file efficiently."""
    print("="*60)
    print(f"Counting rows in file: {file_path} with compression: {compression}")
    if compression == 'gzip':
        import gzip
        with gzip.open(file_path, 'rt') as f:
            row_count = sum(1 for _ in f) - 2  # Exclude header and last rows
    else:
        with open(file_path, 'rt') as f:
            row_count = sum(1 for _ in f) - 2  # Exclude header and last rows
    print("="*60)
    print(f"Total rows (excludi§§ng header and last rows): {row_count}")
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
                
        if not check_delimiter_consistency(file_path, compression, delimiter):
            return False
        
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
