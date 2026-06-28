---
name: ziwei-pair-analysis
description: 紫微斗數雙人合盤比對模組 — 命宮對看、四化互飛、夫妻宮互照、福德宮舒適度。輸出結構化資料供 LLM 解讀。
version: 1.0.0
author: Qiyan Aina
tags: [ziwei-doushu, 紫微斗數, 合盤, 配對, pair-analysis, heming, match]
---

# 紫微斗數雙人合盤比對

## 概述

基於 ruijayfeng/ziwei（紫微知道）的合盤架構，實作 Python 版本的雙人命盤比對。**不做硬編碼評分，只產出結構化比對資料，交給 LLM 解讀。**

## 流程

```
py-iztro 排A盤 → py-iztro 排B盤 → PairAnalyzer → 結構化資料 → LLM 解盤
```

## 安裝

```bash
python3 -m venv /opt/pyiztro_venv
/opt/pyiztro_venv/bin/pip install py-iztro
```

## 使用

```python
from py_iztro import Astro
from ziwei_pair import PairAnalyzer
import json

astro = Astro()
data_a = json.loads(astro.by_solar('1976-4-4', 10, '男', language='zh-TW').model_dump_json(by_alias=True))
data_b = json.loads(astro.by_solar('1990-5-15', 6, '女', language='zh-TW').model_dump_json(by_alias=True))

result = PairAnalyzer(data_a, data_b).analyze()
print(result.to_prompt_context())  # 直接餵 LLM
```

## 比對項目

### 1. 命宮對看
雙方命宮主星強弱搭配、煞吉星分布、節奏相容度（開創型 vs 穩定型）

### 2. 四化互飛
A 的四化星落在 B 的哪宮，B 的四化星落在 A 的哪宮
- 祿=助益、權=主導、科=緩和、忌=課題

### 3. 夫妻宮互照
A 的夫妻宮 vs B 的命宮（A 的理想 vs B 的實際）

### 4. 福德宮情緒舒適度
雙方福德宮主星相容性

### 5. 特殊格局
命宮同星、廉貞忌入對方宮位

## LLM Prompt 範本

結構化資料產出後，LLM 依此格式解讀：

```markdown
## 雙人命盤合參解析
### 壹· 緣分深淺（定性：天作之合/歡喜冤家/相輔相成）
### 貳· 性情互動（相合之處/磨合難點）
### 參· 命理羈絆（四化互飛：誰旺誰/誰牽掛誰）
### 肆· 現實展望（未來挑戰/相處建議）
```

## 完整模組原始碼（ziwei_pair.py）

```python
from py_iztro import Astro
from typing import Any
import json

SHA_STARS = {'擎羊', '陀羅', '火星', '鈴星', '地空', '地劫',
             '天空', '旬空', '截路', '大耗', '天使', '天傷'}
LUCKY_STARS = {'文昌', '文曲', '左輔', '右弼', '天魁', '天鉞',
               '祿存', '天馬', '天官', '天福', '天才', '天壽',
               '三台', '八座', '恩光', '天貴', '台輔', '龍池',
               '鳳閣', '紅鸞', '天喜', '孤辰', '寡宿'}
FOUR_SIHUA = {'祿', '權', '科', '忌'}
BRANCH_NAMES = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']

def _get_branch(p: dict) -> int:
    return BRANCH_NAMES.index(p['earthlyBranch'])

def _major_stars(p: dict) -> list:
    return [s['name'] for s in p.get('majorStars', [])]

def _all_stars(p: dict) -> list:
    return p.get('majorStars', []) + p.get('minorStars', []) + p.get('adjectiveStars', [])

def _get_sihua(data: dict) -> list:
    r = []
    for p in data['palaces']:
        for s in p['majorStars'] + p['minorStars']:
            if s.get('mutagen') and s['mutagen'] in FOUR_SIHUA:
                r.append({'star': s['name'], 'mutagen': s['mutagen'],
                          'palace': p['name'], 'branch': _get_branch(p)})
    return r

def _palace_by_branch(palaces: list, b: int) -> dict:
    for p in palaces:
        if _get_branch(p) == b:
            return p
    return {}

class PairAnalyzer:
    def __init__(self, a: dict, b: dict):
        self.a, self.b = a, b
        self.r = {}  # result

    def analyze(self) -> dict:
        self._life_contrast()
        self._sihua_fly()
        self._spouse_mirror()
        self._fortune_comfort()
        self._patterns()
        return self.r

    def _p(self, data, name):
        for p in data['palaces']:
            if p['name'] == name:
                return p
        return {}

    def _life_contrast(self):
        am = _major_stars(self._p(self.a, '命宮'))
        bm = _major_stars(self._p(self.b, '命宮'))
        open_s = {'七殺', '破軍', '貪狼', '廉貞'}
        stable_s = {'紫微', '天府', '天相', '天梁', '武曲'}
        ao = sum(1 for s in am if s in open_s)
        bo = sum(1 for s in bm if s in open_s)
        ast = sum(1 for s in am if s in stable_s)
        bst = sum(1 for s in bm if s in stable_s)
        if ao > 0 and bo > 0:
            pace = '雙方開創型，節奏相近'
        elif (ao > 0 and bst > 0) or (bo > 0 and ast > 0):
            pace = '一動一靜，互補或摩擦取決於分工'
        elif ast > 0 and bst > 0:
            pace = '雙方穩定型，生活協調'
        else:
            pace = '需觀察'
        self.r['life_contrast'] = {'a_major': am, 'b_major': bm, 'pace': pace}

    def _sihua_fly(self):
        def _map(sihua_list, target):
            r = []
            for s in sihua_list:
                tp = _palace_by_branch(target['palaces'], s['branch'])
                r.append({'star': s['star'], 'mutagen': s['mutagen'],
                          'from_palace': s['palace'], 'to_palace': tp.get('name', '?')})
            return r
        self.r['sihua'] = {'a_to_b': _map(_get_sihua(self.a), self.b),
                           'b_to_a': _map(_get_sihua(self.b), self.a)}

    def _spouse_mirror(self):
        asp = _major_stars(self._p(self.a, '夫妻'))
        bsp = _major_stars(self._p(self.b, '夫妻'))
        amg = _major_stars(self._p(self.a, '命宮'))
        bmg = _major_stars(self._p(self.b, '命宮'))
        def _ji(p):
            for s in p.get('majorStars', []):
                if s.get('mutagen') == '忌': return True
            return False
        self.r['spouse'] = {
            'a_spouse': asp, 'b_life': bmg,
            'match': '期待相近' if set(asp) & set(bmg) else '需觀察',
            'b_spouse': bsp, 'a_life': amg,
            'reverse_match': '期待相近' if set(bsp) & set(amg) else '需觀察',
        }

    def _fortune_comfort(self):
        af = _major_stars(self._p(self.a, '福德'))
        bf = _major_stars(self._p(self.b, '福德'))
        self.r['fortune'] = {'a': af or ['無'], 'b': bf or ['無']}

    def _patterns(self):
        r = []
        am = _major_stars(self._p(self.a, '命宮'))
        bm = _major_stars(self._p(self.b, '命宮'))
        common = set(am) & set(bm)
        if common:
            r.append(f"命宮同星：雙方命宮皆有{', '.join(common)}")
        asp = self._p(self.a, '夫妻')
        for s in asp.get('majorStars', []):
            if s.get('mutagen') == '忌':
                bc = _palace_by_branch(self.b['palaces'], _get_branch(asp))
                if bc:
                    r.append(f"廉貞忌入{bc['name']}：A的夫妻宮化忌對應B的{bc['name']}")
        self.r['patterns'] = r

def to_prompt(result: dict) -> str:
    lines = ['## 壹· 命宮對看']
    lc = result.get('life_contrast', {})
    lines.append(f'A命宮：{lc.get("a_major",[])}  B命宮：{lc.get("b_major",[])}')
    lines.append(f'節奏：{lc.get("pace","")}')
    lines.append('')
    lines.append('## 貳· 四化互飛')
    for label, key in [('A對B', 'a_to_b'), ('B對A', 'b_to_a')]:
        for s in result.get('sihua', {}).get(key, []):
            lines.append(f'{s["star"]}化{s["mutagen"]}（{s["from_palace"]}→{s["to_palace"]}）')
    lines.append('')
    sp = result.get('spouse', {})
    lines.append('## 參· 夫妻宮互照')
    lines.append(f'A的伴侶期待：{sp.get("a_spouse",[])} vs B的形象：{sp.get("b_life",[])} → {sp.get("match","")}')
    lines.append(f'B的伴侶期待：{sp.get("b_spouse",[])} vs A的形象：{sp.get("a_life",[])} → {sp.get("reverse_match","")}')
    lines.append('')
    ft = result.get('fortune', {})
    lines.append('## 肆· 福德宮')
    lines.append(f'A：{ft.get("a",[])}  B：{ft.get("b",[])}')
    if result.get('patterns'):
        lines.append('')
        lines.append('## 伍· 特殊格局')
        lines.extend(f'  {p}' for p in result['patterns'])
    return '\n'.join(lines)
```

## 整合

此模組可搭配 py-iztro-ziwei-doushu（排盤）+ ziwei-doushu-nihai（格局與古籍 RAG）：

```
py-iztro 排盤 → PairAnalyzer 比對 → to_prompt() → LLM 解盤
                                                          ↑
                                            ziwei-doushu-nihai 格局知識庫（RAG）
```
