import csv
import re
from datetime import datetime, timedelta
from bisect import bisect_left

TIME_WINDOW = 3600   # ±60分


# -----------------------------
# コールサイン正規化
# -----------------------------
def normalize_call(call):

    call = call.upper().strip()

    if "/" not in call:
        return call

    parts = call.split("/")

    for p in parts:
        if re.match(r"^[A-Z]{1,3}[0-9][A-Z0-9]{1,4}$", p):
            return p

    return max(parts, key=len)


# -----------------------------
# MODE正規化
# -----------------------------
def normalize_mode(mode):

    m = mode.upper()

    if m in ["FT8","FT4","JT65","JT9","MFSK","DIGITAL","DATA"]:
        return "DIGI"

    if m in ["SSB","PHONE","USB","LSB"]:
        return "PHONE"

    if m in ["CW"]:
        return "CW"

    return m


# -----------------------------
# 周波数→バンド
# -----------------------------
def freq_to_band(freq):

    m = re.search(r"[0-9]+\.?[0-9]*", str(freq))
    if not m:
        return "?"

    f = float(m.group())

    if f > 10000:
        f = f / 1000

    if 1.8 <= f < 2: return "160M"
    if 3.5 <= f < 4: return "80M"
    if 7 <= f < 8: return "40M"
    if 10 <= f < 11: return "30M"
    if 14 <= f < 15: return "20M"
    if 18 <= f < 19: return "17M"
    if 21 <= f < 22: return "15M"
    if 24 <= f < 25: return "12M"
    if 28 <= f < 30: return "10M"
    if 50 <= f < 54: return "6M"
    if 144 <= f < 148: return "2M"
    if 430 <= f < 450: return "70CM"

    return "?"


# -----------------------------
# HAMLOG時間
# -----------------------------
def parse_hamlog(date, time):

    y, m, d = date.split("/")
    y = int(y)

    if y < 50:
        y += 2000
    else:
        y += 1900

    date = f"{y}{int(m):02d}{int(d):02d}"

    clean_time = time.strip().upper()

    tz = None

    if clean_time.endswith("Z"):
        tz = "UTC"
        clean_time = clean_time[:-1]

    elif clean_time.endswith("J"):
        tz = "JST"
        clean_time = clean_time[:-1]

    clean_time = clean_time[:5].replace(":", "")

    dt = datetime.strptime(date + clean_time, "%Y%m%d%H%M")

    if tz == "JST":
        dt -= timedelta(hours=9)

    return dt


# -----------------------------
# ADIF読み込み
# -----------------------------
def parse_adif(file):

    with open(file, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()

    records = re.split(r"<eor>", text, flags=re.IGNORECASE)

    qsos = []

    for r in records:

        q = {}

        fields = re.findall(r"<(.*?):(\d+).*?>([^<]*)", r)

        for name, length, value in fields:
            q[name.upper()] = value.strip()

        if "CALL" in q:
            qsos.append(q)

    return qsos


# -----------------------------
# ADIF時間
# -----------------------------
def adif_time(date, time):

    try:
        return datetime.strptime(date + time[:4], "%Y%m%d%H%M")
    except:
        return None


# -----------------------------
# インデックス作成
# -----------------------------
def build_index(qsos):

    index = {}

    for q in qsos:

        call = normalize_call(q.get("CALL", ""))

        band = q.get("BAND", "").upper()

        if not band:
            band = freq_to_band(q.get("FREQ", ""))

        mode = normalize_mode(q.get("MODE", ""))

        dt = adif_time(q.get("QSO_DATE", ""), q.get("TIME_ON", ""))

        if not dt:
            continue

        key = (call, band)

        index.setdefault(key, []).append((dt, mode))

    return index


# -----------------------------
# マッチ判定
# -----------------------------
def match(dt, call, band, mode, index):

    key = (call, band)

    if key not in index:
        return False

    for t, m in index[key]:

        diff = abs((dt - t).total_seconds())

        if diff <= TIME_WINDOW:

            if m == mode:
                return True

            # MODE違いでも許容
            return True

    return False


# -----------------------------
# 日付ずれ補正
# -----------------------------
def match_shift(dt, call, band, mode, index):

    if match(dt, call, band, mode, index):
        return True

    if dt.hour >= 21:
        if match(dt + timedelta(days=1), call, band, mode, index):
            return True

    if dt.hour <= 3:
        if match(dt - timedelta(days=1), call, band, mode, index):
            return True

    return False


# -----------------------------
# QSL更新
# -----------------------------
def update_third(third, lotw, eqsl):

    if third == "R":
        return "R"

    if third == "":
        if lotw and eqsl: return "R"
        if lotw: return "L"
        if eqsl: return "E"
        return ""

    if third == "P":
        if lotw and eqsl: return "Y"
        if lotw: return "K"
        if eqsl: return "F"
        return "P"

    if third == "E":
        if lotw: return "R"
        return "E"

    if third == "L":
        if eqsl: return "R"
        return "L"

    if third == "F":
        if lotw: return "R"
        return "F"

    if third == "K":
        if eqsl: return "R"
        return "K"

    if third == "Y":
        if not lotw and not eqsl: return "P"
        if lotw and eqsl: return "Y"
        if lotw: return "K"
        if eqsl: return "F"

    return third


# =============================
# メイン
# =============================

print("LoTW読み込み")
lotw = parse_adif("lotw.adi")

print("eQSL読み込み")
eqsl = parse_adif("eqsl.adi")

lotw_index = build_index(lotw)
eqsl_index = build_index(eqsl)

rows = []

with open("hamlog.csv", encoding="cp932", errors="ignore") as f:
    reader = csv.reader(f)
    for r in reader:
        rows.append(r)

changes = []

lotw_hits = 0
eqsl_hits = 0

for r in rows:

    if len(r) < 10:
        continue

    call = normalize_call(r[0])

    dt = parse_hamlog(r[1], r[2])

    band = freq_to_band(r[5]).upper()

    mode = normalize_mode(r[6])

    old_code = r[9].upper()
    old_code = (old_code + "   ")[:3]

    third = old_code[2]

    if third == " ":
        third = ""

    lotw_flag = match_shift(dt, call, band, mode, lotw_index)
    eqsl_flag = match_shift(dt, call, band, mode, eqsl_index)

    if lotw_flag:
        lotw_hits += 1

    if eqsl_flag:
        eqsl_hits += 1

    new_third = update_third(third, lotw_flag, eqsl_flag)

    if new_third != third:

        new_code = old_code[:2] + new_third

        changes.append((call, str(dt), old_code, new_code))

        r[9] = new_code


with open("hamlog_checked.csv", "w", newline="", encoding="cp932") as f:

    writer = csv.writer(f)
    writer.writerows(rows)


with open("changes_checked.txt", "w") as f:

    for c in changes:
        f.write(f"{c[0]} {c[1]} {c[2]} -> {c[3]}\n")


print("更新件数:", len(changes))
print("LoTWマッチ:", lotw_hits)
print("eQSLマッチ:", eqsl_hits)
