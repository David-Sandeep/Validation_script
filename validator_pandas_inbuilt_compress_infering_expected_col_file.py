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

def detect_delimiter(file_path):
    """Detect the delimiter used in the file."""
    try:
        with open(file_path, 'rt', encoding='utf-8') as file:
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
    reserved_memory = 4 * 1024 * 1024 * 1024  # 1 GB in bytes
    usable_memory = max(available_memory - reserved_memory, 0)  # Ensure it's not negative

    estimated_row_size = 500  # Estimate the memory required for a single row
    chunk_size = usable_memory // estimated_row_size  # Calculate the number of rows per chunk

    return chunk_size
    
def load_expected_columns(file_path):
    with open(file_path, 'r') as f:
        expected_columns = [line.strip() for line in f if line.strip()]  # Read non-empty lines
    return expected_columns

    """Determine chunk size based on available system memory, leaving 1 GB free."""
    mem = psutil.virtual_memory()
    available_memory = mem.available  # in bytes
    reserved_memory = 4 * 1024 * 1024 * 1024  # 1 GB in bytes
    usable_memory = max(available_memory - reserved_memory, 0)  # Ensure it's not negative

    estimated_row_size = 500  # Estimate the memory required for a single row
    chunk_size = usable_memory // estimated_row_size  # Calculate the number of rows per chunk

    return chunk_size

def validate_file(file_path):
    """Validate a single CSV or pipe-separated values file."""
    
    
    start_time = time.time()
    try:
        delimiter = detect_delimiter(file_path)
        if delimiter is None:
            print(f"Skipping file {file_path} due to delimiter detection error.")
            return False, 0

        expected_columns_file = 'expected_columns.txt'
        expected_columns = load_expected_columns(expected_columns_file)
        print(f"Delimiter detected: '{delimiter}'")

        chunk_size = get_dynamic_chunk_size()
        print(f"Using dynamic chunk size: {chunk_size:,} rows per chunk")

        for chunk in pd.read_csv(file_path, delimiter=delimiter, chunksize=chunk_size, compression='infer'):
            if chunk.columns.tolist() != expected_columns:
                print(f"Format error detected in {file_path}")
                return False, 0
            print(f"Processed {len(chunk)} rows")
        
        elapsed_time = time.time() - start_time
        print(f"Scanned {file_path} successfully. Time taken: {elapsed_time:.2f} seconds")
        return True, elapsed_time

    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return False, 0


def save_scanned_files_info(scanned_files_info):
    """Save scanned files information to CSV."""
    df = pd.DataFrame(scanned_files_info, columns=['file_path', 'time_taken'])
    if os.path.exists("scanned_files_info.csv"):
        df_existing = pd.read_csv("scanned_files_info.csv")
        df = pd.concat([df_existing, df], ignore_index=True)
    df.to_csv("scanned_files_info.csv", index=False)
    print("Scanned files information saved to scanned_files_info.csv")
    
    
def scan_directory(directory_path, scanned_files):
    """Scan all files in a directory."""
    valid_files = []
    for root, _, files in os.walk(directory_path):
        for file in files:
            file_path = os.path.join(root, file)
            if file_path in scanned_files:
                print(f"Skipping already scanned file: {file_path}")
                continue
            if validate_file(file_path):
                valid_files.append(file_path)
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

    if os.path.exists("scanned_files.txt"):
        with open("scanned_files.txt", "r") as f:
            scanned_files = set(f.read().splitlines())

    scanned_files_info = []

    if os.path.isfile(path):
        is_valid, time_taken = validate_file(path)
        if is_valid:
            valid_files.append(path)
            scanned_files.add(path)
            scanned_files_info.append((path, time_taken))
    elif os.path.isdir(path):
        valid_files_info = scan_directory(path, scanned_files)
        scanned_files_info.extend(valid_files_info)
    else:
        print("The selected path is neither a file nor a directory.")

    save_scanned_files_info(scanned_files_info)

    with open("scanned_files.txt", "w") as f:
        for file in scanned_files:
            f.write(file + "\n")
        print("Scanned file names saved to scanned_files.txt")

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

    if os.path.exists("scanned_files.txt"):
        with open("scanned_files.txt", "r") as f:
            scanned_files = set(f.read().splitlines())

    scanned_files_info = []

    if os.path.isfile(path):
        is_valid, time_taken = validate_file(path)
        if is_valid:
            valid_files.append(path)
            scanned_files.add(path)
            scanned_files_info.append((path, time_taken))
    elif os.path.isdir(path):
        valid_files_info = scan_directory(path, scanned_files)
        scanned_files_info.extend(valid_files_info)
    else:
        print("The selected path is neither a file nor a directory.")

    save_scanned_files_info(scanned_files_info)

    with open("scanned_files.txt", "w") as f:
        for file in scanned_files:
            f.write(file + "\n")
        print("Scanned file names saved to scanned_files.txt")


if __name__ == "__main__":
    main()
