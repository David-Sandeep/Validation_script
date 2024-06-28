Delimiter Detection:

Added detect_delimiter function to identify if the file uses commas (,) or pipes (|) as delimiters, supporting both uncompressed and gzip-compressed files.


Row Counting:

Enhanced count_rows function to count rows efficiently, excluding the last row, for both uncompressed and gzip-compressed files.


Last Row Retrieval:

Improved get_last_row function to fetch the last row efficiently, supporting both uncompressed and gzip-compressed files.


Loading Expected Columns:

Added load_expected_columns function to read the expected columns from a specified file (expected_columns.txt).



File Validation:

Enhanced validate_file function to:
Determine file compression based on file extension.
Detect delimiter.
Load expected columns.
Compare actual columns from the first row with expected columns.
Compare total row count with the count in the last row’s third value.

Saving Valid Files:

Enhanced save_valid_files function to save the list of valid files to valid_scanned_files.txt, only if there are any valid files.











 Case 1:
value= all records count. untitled4_validator_ all records count.py

Eg: last row’s value =10        total rows=11.  -1


Case 2: untitled7_validator_all records count excluding header_1.py
Value = all records count excluding header. 
 
Eg: last row’s value= 9  total rows=11.         -2
