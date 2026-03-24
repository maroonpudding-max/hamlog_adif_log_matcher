# DX Log Matcher

Python tool for matching amateur radio QSO logs between HAMLOG CSV and ADIF formats.

## Features

- Match HAMLOG CSV and ADIF logs
- Flexible time tolerance (±60 minutes)
- CALL / BAND / MODE matching
- Designed for amateur radio QSO log verification

## Usage

Place the following files in the same directory:

dx_match_final_v8.py
hamlog.csv
lotw.adi
eqsl.adi

Run:

python dx_match_final_v8.py

## Output

changes_checked.txt
hamlog_checked.csv

## Performance

Tested with approximately 85,000 QSO records.
Processing time: under 30 seconds.

## Disclaimer

This software is provided "as is", without warranty.
Use at your own risk.