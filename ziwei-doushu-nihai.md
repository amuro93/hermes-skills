---
name: ziwei-doushu-nihai
description: 倪海夏體系紫微斗數格局識別 + 古籍知識庫 — 44 格局、14主星合盤斷語、骨髓賦/全集/全書原文。搭配 py-iztro 使用。
version: 1.0.0
author: Qiyan Aina
tags: [ziwei-doushu, 紫微斗數, nihai, pattern-recognition, 格局, 倪海夏, heming]
---

# 倪海夏紫微斗數格局識別引擎

基於 Renhuai123/ziwei-doushu。

## 安裝

```bash
python3 -m venv /opt/pyiztro_venv
/opt/pyiztro_venv/bin/pip install py-iztro
git clone https://github.com/Renhuai123/ziwei-doushu.git /opt/ziwei-doushu
```

## 排盤 -> 格局識別

```python
from py_iztro import Astro
import json

astro = Astro()
chart = astro.by_solar('1976-4-4', 10, '男', language='zh-TW')
data = json.loads(chart.model_dump_json(by_alias=True))

SHA = ['擎羊','陀羅','火星','鈴星','地空','地劫','天空','旬空','截路','大耗','天使','天傷']
LUCKY = ['文昌','文曲','左輔','右弼','天魁','天鉞','祿存','天馬',
         '天官','天福','天才','天壽','三台','八座','恩光',
         '天貴','台輔','龍池','鳳閣','紅鸞','天喜','孤辰','寡宿']

def build_palace_map(data):
    branch_names = ['子','丑','寅','卯','辰','巳','午','未','申','酉','戌','亥']
    palaces = {}
    for p in data['palaces']:
        stars = {'major': [], 'sha': [], 'lucky': [], 'minor': []}
        for s in p['majorStars'] + p['minorStars'] + p['adjectiveStars']:
            n = s['name']
            if s.get('type') == 'major' or n in [ms['name'] for ms in p['majorStars']]:
                if n not in stars['major']: stars['major'].append(n)
            elif n in SHA: stars['sha'].append(n)
            elif n in LUCKY: stars['lucky'].append(n)
            else: stars['minor'].append(n)
        palaces[p['name']] = {'branch': branch_names.index(p['earthlyBranch']), 'stars': stars}
    return palaces
```

## 44 格局

### 大貴格局 (excellent)
君臣慶會、紫府同宮、府相朝垣、陽梁昌祿、三奇加會

### 吉格 (good)
火貪/鈴貪格、武貪格、殺破狼、機月同梁、廉貞天相格、武曲七殺、天同天梁格、日月同宮、日月夾命、巨日同宮、石中隱玉、明珠出海、紫微入命、輔弼夾命、昌曲夾命、魁鉞夾命、雙祿朝垣、化祿入財、化權入官、輔弼同會、魁鉞同會、科權雙會、機月同梁三星會

### 凶格 (caution)
羊陀夾忌、火鈴夾命、空劫夾命、廉殺羊、巨火羊、鈴昌陀武、馬頭帶箭

## 格局識別 Python 實作

```python
def detect_patterns(palaces):
    patterns = []
    ming = palaces.get('命宮', {})
    if not ming: return patterns
    san_fang_all = set()
    for pn in ['命宮','財帛','官祿','遷移']:
        p = palaces.get(pn)
        if p:
            for cat in ['major','lucky','sha']:
                san_fang_all.update(p['stars'][cat])
    def has(n): return n in san_fang_all
    def in_ming(n): return n in ming['stars']['major'] or n in ming['stars']['lucky']

    if in_ming('紫微') and has('左輔') and has('右弼'):
        patterns.append({'name':'君臣慶會','level':'excellent','desc':'紫微入命左右同會，大富大貴'})
    if in_ming('紫微') and in_ming('天府'):
        patterns.append({'name':'紫府同宮','level':'excellent','desc':'帝相並臨，尊貴之命'})
    if has('太陽') and has('天梁') and has('文昌') and has('祿存'):
        patterns.append({'name':'陽梁昌祿','level':'excellent','desc':'科舉之星，清貴顯達'})
    if all(has(s) for s in ['七殺','破軍','貪狼']):
        patterns.append({'name':'殺破狼','level':'good','desc':'開創闖蕩，一生變動多'})
    if all(has(s) for s in ['天機','太陰','天同','天梁']):
        patterns.append({'name':'機月同梁','level':'excellent','desc':'文質彬彬，適公職學術'})
    if has('武曲') and has('貪狼'):
        patterns.append({'name':'武貪格','level':'good','desc':'中年後大富大貴(武貪不發少年人)'})
    if has('貪狼') and (has('火星') or has('鈴星')):
        hn = '火貪格' if has('火星') else '鈴貪格'
        patterns.append({'name':hn,'level':'good','desc':f'貪狼+{"火星" if has("火星") else "鈴星"}，爆發財運'})
    return patterns
```

## 14 主星夫妻宮斷語

來源：`/opt/ziwei-doushu/lib/ziwei/heming-knowledge.ts`

紫微: 配偶高傲能幹宜晚婚 | 天機: 婚姻多變宜年齡差大 | 武曲: 寡宿必晚婚
廉貞: 感情激烈起伏大 | 貪狼: 桃花重宜遲婚35後 | 天同: 溫和享樂宜男35/女30
巨門: 口舌之星溝通關鍵 | 七殺: 配偶剛強宜晚婚 | 破軍: 婚姻多變宜冷靜
太陽: 男助妻/女旺夫 | 天府: 配偶賢能宜28後 | 太陰: 溫柔感性
天相: 配偶溫柔斯文 | 天梁: 配偶年長5歲+

## 古籍 RAG

`/opt/ziwei-doushu/lib/classics/data/`:
- gusuifu.ts 骨髓賦 ~1500字 (核心，段落有唯一ID如gsf-1-1)
- quanji.ts 紫微斗數全集
- quanshu.ts 紫微斗數全書

## 整合流程

py-iztro (排盤) -> patterns.py (格局) -> heming (斷語) -> classics (RAG) -> LLM (解盤)

## 踩坑

1. hour用0-11地支索引(戌=10)，iztro用0-12(早子0/晚子12)，戌都是10
2. 倪海夏體系不支援飛星四化
3. patterns.ts是TypeScript，Python需自行轉換
4. 格局成敗關鍵在breaking煞星條件
