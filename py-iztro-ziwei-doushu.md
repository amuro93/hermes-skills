---
name: py-iztro-ziwei-doushu
description: 紫微斗數排盤引擎 py-iztro — 安裝、使用、四化查詢、流年運限。適用於本地 LLM、Telegram bot、資料分析等 Python 環境。
version: 1.0.0
author: Qiyan Aina
tags: [ziwei-doushu, 紫微斗數, astrology, python, py-iztro, chinese-astrology, fortune-telling]
---

# py-iztro 紫微斗數排盤引擎

`py-iztro` 是 iztro（JS）的 Python port，使用 pythonmonkey 在 Python 中執行 JS 核心，輸出乾淨的 Pydantic 結構化資料。支援陽曆/農曆排盤、12 宮星盤、主星/輔星/雜耀/四化/亮度、大限/流年/流月/流日/流時運限、三方四正等。

## 安裝

```bash
# 建立虛擬環境（建議）
python3 -m venv /path/to/pyiztro_venv
/path/to/pyiztro_venv/bin/pip install py-iztro

# 或使用 uv
uv pip install py-iztro
```

> ⚠️ `pythonmonkey` 需要建置 C 擴展，第一次安裝可能較慢（約 15-30 秒）。

## 基本用法

### 1. 陽曆排盤（最常用）

```python
from py_iztro import Astro

astro = Astro()

chart = astro.by_solar(
    solar_date_str='1990-5-15',   # YYYY-M-D（無前導零）
    time_index=6,                  # 時辰索引（0~12）
    gender='男',                    # 或 '女'
    fix_leap=True,                 # 是否調整閏月（預設 True）
    language='zh-TW'               # 繁體中文輸出
)

# 轉成 JSON
import json
data = json.loads(chart.model_dump_json(by_alias=True))
```

### 2. 時辰索引對照表

0=早子時(00:00~00:59), 1=丑時(01:00~02:59), 2=寅時(03:00~04:59),
3=卯時(05:00~06:59), 4=辰時(07:00~08:59), 5=巳時(09:00~10:59),
6=午時(11:00~12:59), 7=未時(13:00~14:59), 8=申時(15:00~16:59),
9=酉時(17:00~18:59), 10=戌時(19:00~20:59), 11=亥時(21:00~22:59),
12=晚子時(23:00~23:59)

**換算 function：**
```python
def hour_to_time_index(h: int) -> int:
    return {0: 0, 23: 12}.get(h, (h + 1) // 2)
```

## 資料結構

### chart 頂層
gender, solarDate, lunarDate, chineseDate(八字), time(時辰), timeRange,
sign(星座), zodiac(生肖), earthlyBranchOfSoulPalace(命宮地支),
earthlyBranchOfBodyPalace(身宮地支), soul(命主), body(身主),
fiveElementsClass(五行局), palaces(12宮陣列)

### palace 宮位
index(0=寅,1=卯...), name(宮名), isBodyPalace(身宮), heavenlyStem(宫干),
earthlyBranch(宫支), majorStars(主星), minorStars(輔星,含文昌/文曲),
adjectiveStars(雜耀), decadal(大限), ages(年齡)

### star 星耀
name(星名), type(major/soft/tianma等), brightness(廟旺得利平不陷),
mutagen(四化:祿權科忌)

> 文昌/文曲歸類為輔星(minorStars)，查四化需同時檢查 majorStars + minorStars

## 四化查詢

```python
for p in data['palaces']:
    for s in p['majorStars'] + p['minorStars']:
        if s.get('mutagen'):
            print(f'{p["name"]} {s["name"]} 化{s["mutagen"]}')
```

## 流年運限

```python
horo = chart.horoscope('2026-06-29')
hdata = json.loads(horo.model_dump_json(by_alias=True))
# keys: lunarDate, solarDate, decadal, age, yearly, monthly, daily, hourly
```

## 農曆排盤

```python
chart = astro.by_lunar('1990-4-21', 6, '女', is_leap=False, language='zh-TW')
```

## 驗證（1976-04-04 19:05 戌時 男）

```python
from py_iztro import Astro
import json
astro = Astro()
chart = astro.by_solar('1976-4-4', 10, '男', language='zh-TW')
data = json.loads(chart.model_dump_json(by_alias=True))

# 命宮：貪狼(旺)+左輔+擎羊
# 四化：廉貞忌.天同祿.天機權.文昌科
# 命主破軍/身主文昌/金四局
```

## 踩坑記錄

1. solar_date_str 格式 `YYYY-M-D`，**無前導零**
2. 文昌/文曲四化藏在 minorStars mutagen，要一起查
3. 亮度：廟>旺>得>利>平>不>陷
4. 建議獨立 venv 避免系統衝突
