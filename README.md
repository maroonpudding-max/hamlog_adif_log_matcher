![Result](command.png)

# DX Log Matcher for HAMLOG

Tool for automatically matching amateur radio QSO logs between **HAMLOG CSV** and **ADIF logs (LoTW / eQSL)**.

Designed for DXers who manage large HAMLOG databases and want to quickly verify confirmations.

---

## Overview

Amateur radio operators often keep logs in **HAMLOG** while confirmations arrive later via **LoTW** or **eQSL**.

Because uploads may occur hours, days, or even years later, manual matching can be extremely time-consuming.

This tool automatically compares log entries and detects matches using multiple criteria.

Background

HAMLOG originally used a simple QSL flag system where the third character was often just "Y".

After starting to manage confirmations from LoTW and eQSL, more detailed classification became necessary.
However, a large number of existing QSOs remained unprocessed, and manual verification was no longer practical.

This script was created to automate the matching process between HAMLOG logs and ADIF logs (LoTW / eQSL), allowing large QSO databases to be processed quickly and consistently.

---

## Features

* Match **HAMLOG CSV logs** with **ADIF logs**
* Detect QSO matches using:

  * CALLSIGN
  * BAND
  * MODE
  * Time tolerance (default ±60 minutes)
* Supports confirmation sources such as:

  * LoTW
  * eQSL
* Designed for **DX confirmation management**

---

## Requirements

* Python 3.x

No external libraries are required.

---

## Supported File Formats

Input files:

* HAMLOG export file (CSV)
* LoTW log file (ADIF)
* eQSL log file (ADIF)

---

## Usage

1. Place the following files in the same directory:

```
hamlog.csv
lotw.adi
eqsl.adi
dx_match_final_v8.py
```

2. Run the script:

```
python dx_match_final_v8.py
```

3. The script will analyze the logs and detect matching QSOs.

---

## Matching Rules

Matches are determined using the following fields:

* CALLSIGN
* BAND
* MODE
* QSO time within ±60 minutes tolerance

These rules help account for time differences and delayed log uploads.

---

## Output

The script generates result files such as:

```
changes_checked.txt
hamlog_checked.csv
```

These files show detected matches and verification results.

---

## Disclaimer

This software is provided **"as is"**, without warranty of any kind.

Use at your own risk.

---

## Author

Amateur radio operator developing tools for DX log verification.

---

Sample files are included in the repository for testing.

This tool has been tested on a real HAMLOG database containing over 86,000 QSO records, enabling fast verification of LoTW and eQSL confirmations.
