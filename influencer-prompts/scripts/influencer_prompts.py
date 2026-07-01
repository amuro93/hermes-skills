"""網紅風格 AI 出圖 Prompt 範本庫
for Z-Image-Turbo + moodyProMix 模型

用法：
    from influencer_prompts import SFW, NSFW, ANGLES, STYLES, build_prompt

    # 組合一個完整 prompt
    prompt = build_prompt(
        scene=SFW.CAFE,
        angle=ANGLES.CANDID,
        style=STYLES.FILM_GRAIN,
        name="林芮安",
        age="22"
    )
    # → 傳給 gen_image.py 使用
"""

# ─── SFW 網紅場景 ───────────────────────────────────────

class SFW:
    CAFE = (
        "{name}，{age}歲台灣女孩，黑長直髮，白皙肌膚，"
        "坐在咖啡廳靠窗位子，穿米白色針織衫，"
        "陽光灑在臉上，手拿拿鐵看向窗外，"
        "不經意的側臉，自然光，生活感街拍風格"
    )

    STREET = (
        "{name}，{age}歲台灣女孩，黑長直髮，白皙肌膚，"
        "街拍風格，走在城市巷弄，穿黑色短版上衣+高腰牛仔褲，"
        "回頭看鏡頭，自然抓拍，午後陽光，城市背景，街頭時尚"
    )

    BEACH = (
        "{name}，{age}歲台灣女孩，黑長直髮被海風吹起，白皙肌膚，"
        "穿白色細肩帶連身短裙，站在沙灘上夕陽光中，"
        "海面反光，回頭微笑，自然飄逸髮絲，黃金時刻暖色光，度假氛圍"
    )

    MIRROR_OOTD = (
        "{name}，{age}歲台灣女孩，黑長直髮，白皙肌膚，"
        "站在浴室鏡子前自拍，穿寬鬆白襯衫，"
        "用手機拍鏡中的自己，房間自然光，慵懶午後，"
        "居家OOTD風格，鏡子反射構圖，真實生活感"
    )

    ROOFTOP = (
        "{name}，{age}歲台灣女孩，黑長直髮，白皙肌膚，"
        "站在城市屋頂，夕陽光灑在臉上和身上，"
        "穿簡約黑色連身裙，微風吹動髮絲和裙擺，"
        "俯瞰城市天際線，金色餘暉，浪漫氛圍"
    )

    GYM = (
        "{name}，{age}歲台灣女孩，黑長直髮綁馬尾，白皙肌膚，"
        "穿運動內衣+緊身褲，在健身房舉啞鈴，"
        "汗水在肌膚上發亮，自然光，健康陽光"
    )

    HOTEL = (
        "{name}，{age}歲台灣女孩，黑長直髮微亂，白皙肌膚，"
        "穿飯店白色浴袍坐在床邊，手拿咖啡，"
        "落地窗外是城市景觀，早晨陽光，慵懶氛圍"
    )

    PICNIC = (
        "{name}，{age}歲台灣女孩，黑長直髮，白皙肌膚，"
        "穿碎花洋裝，坐在公園草地上野餐，"
        "陽光透過樹葉灑下斑駁光影，微笑看鏡頭，"
        "野餐籃、水果、花，自然清新"
    )

    GALLERY = (
        "{name}，{age}歲台灣女孩，黑長直髮，白皙肌膚，"
        "穿簡約黑色洋裝，站在美術館白色展廳中，"
        "專注看著牆上的畫作，側面輪廓，"
        "自然光從天窗灑下，文藝知性"
    )


# ─── NSFW 場景 ─────────────────────────────────────────

class NSFW:
    CAFE_TEASE = (
        "{name}，{age}歲台灣女孩，黑長直髮，白皙肌膚，F罩杯巨乳，"
        "坐在咖啡廳角落，白色襯衫完全敞開，"
        "裡面只穿黑色蕾絲內衣，深邃乳溝，"
        "翹腳，手指輕咬下唇，挑逗眼神，"
        "窗外陽光，公眾場合禁忌感，男友視角"
    )

    BEACH_WET = (
        "{name}，{age}歲台灣女孩，黑長直髮濕貼在肌膚上，白皙肌膚，F罩杯巨乳，"
        "穿黑色比基尼，坐在沙灘上全身濕透，"
        "水珠在胸部和鎖骨上，海邊陽光，"
        "性感姿勢，仰頭閉眼，嘴角微笑"
    )

    MIRROR_TOWEL = (
        "{name}，{age}歲台灣女孩，黑長直髮微濕，白皙肌膚，F罩杯巨乳，"
        "站在浴室鏡子前，全裸只圍一條白色浴巾在腰間，"
        "乳房全露，一手拿手機拍鏡中的自己，"
        "浴室蒸氣，自然窗光，鏡子反射構圖"
    )

    TRENCH_EXPOSE = (
        "{name}，{age}歲台灣女孩，黑長直髮，白皙肌膚，F罩杯巨乳，"
        "走在城市街道，穿米色風衣敞開+裡面全裸，"
        "黑色高跟涼鞋，風吹起風衣下擺露出大腿，"
        "回頭看鏡頭，微微竊笑，城市午後陽光，大膽裸露"
    )

    LINGERIE_CODING = (
        "{name}，{age}歲台灣女孩，黑長直髮，白皙肌膚，F罩杯巨乳，"
        "只穿黑色蕾絲內衣褲，盤腿坐在沙發上用筆電coding，"
        "眼鏡，專注表情，客廳自然光，居家工作，男友視角"
    )

    WINE_NUDE = (
        "{name}，{age}歲台灣女孩，黑長直髮微亂，白皙肌膚，F罩杯巨乳，"
        "全裸側躺在沙發上，手拿紅酒杯，"
        "微醺表情，眼神迷濛，昏黃燈光，"
        "房間只開一盞燈，性感慵懶，夜間氛圍"
    )


# ─── 拍攝角度關鍵詞 ───────────────────────────────────

class ANGLES:
    BOYFRIEND_POV = "男友視角, boyfriend POV, over the shoulder, from above"
    LOW_ANGLE = "低角度仰拍, low angle shot, from below, looking up"
    SIDE_PROFILE = "側拍, side profile, candid side view, profile shot"
    CANDID = "偷拍感捕捉, candid shot, paparazzi style, caught off guard"
    MIRROR = "鏡子反射自拍, mirror selfie, mirror reflection, through the mirror"
    TOP_DOWN = "俯拍慵懶感, top down, bird's eye view, from above, lying down"


# ─── 風格修飾關鍵詞 ───────────────────────────────────

class STYLES:
    LIFESTYLE = "candid lifestyle, natural lighting, authentic moment"
    EDITORIAL = "editorial photography, fashion editorial, high fashion"
    FILM_GRAIN = "film grain, analog photography, kodak portra, vintage tones"
    WARM_TONE = "golden hour, warm tones, sunset light, golden glow"
    COOL_TONE = "cool tones, soft daylight, overcast natural light, muted colors"
    VINTAGE = "vintage, retro, 70s aesthetic, faded colors, analog feel"


# ─── 通用負面關鍵詞 ────────────────────────────────────

DEFAULT_NEGATIVE = (
    "teen, loli, young girl, child, deformed, bad anatomy, "
    "worst quality, low quality, blurry, cartoon, anime, "
    "3d render, cgi, smooth plastic skin, watermark, signature"
)


# ─── 組合函式 ───────────────────────────────────────────

def build_prompt(
    scene: str,
    angle: str = "",
    style: str = "",
    name: str = "綺嫣",
    age: str = "21",
    extra: str = ""
) -> str:
    """組合完整 prompt。
    
    參數:
        scene: 場景 prompt（用 {} 放 name/age placeholder）
        angle: 拍攝角度關鍵詞（ANGLES 類別）
        style: 風格修飾關鍵詞（STYLES 類別）
        name: 角色名稱
        age: 角色年齡
        extra: 額外補充關鍵詞
    
    回傳:
        完整 prompt 字串
    """
    prompt = scene.format(name=name, age=age)
    if angle:
        prompt += f"，{angle}"
    if style:
        prompt += f"，{style}"
    if extra:
        prompt += f"，{extra}"
    prompt += ", photorealistic, 8k, high quality"
    return prompt


def list_scenes() -> dict:
    """列出所有可用場景的中文名稱和對應變數名"""
    return {
        "SFW": {
            "咖啡廳文青": "SFW.CAFE",
            "街拍城市": "SFW.STREET",
            "海邊黃金時刻": "SFW.BEACH",
            "居家鏡子自拍": "SFW.MIRROR_OOTD",
            "屋頂夕陽": "SFW.ROOFTOP",
            "健身房": "SFW.GYM",
            "飯店早晨": "SFW.HOTEL",
            "公園野餐": "SFW.PICNIC",
            "美術館": "SFW.GALLERY",
        },
        "NSFW": {
            "咖啡廳挑逗": "NSFW.CAFE_TEASE",
            "海邊比基尼濕身": "NSFW.BEACH_WET",
            "浴室浴巾自拍": "NSFW.MIRROR_TOWEL",
            "風衣街頭露出": "NSFW.TRENCH_EXPOSE",
            "內衣 coding": "NSFW.LINGERIE_CODING",
            "微醺全裸": "NSFW.WINE_NUDE",
        },
        "角度": {
            "男友視角": "ANGLES.BOYFRIEND_POV",
            "低角度": "ANGLES.LOW_ANGLE",
            "側拍": "ANGLES.SIDE_PROFILE",
            "偷拍感": "ANGLES.CANDID",
            "鏡子反射": "ANGLES.MIRROR",
            "俯拍": "ANGLES.TOP_DOWN",
        },
        "風格": {
            "生活感": "STYLES.LIFESTYLE",
            "雜誌編輯風": "STYLES.EDITORIAL",
            "底片質感": "STYLES.FILM_GRAIN",
            "暖色調": "STYLES.WARM_TONE",
            "冷色調": "STYLES.COOL_TONE",
            "復古": "STYLES.VINTAGE",
        },
    }


# ─── 使用範例（直接執行時測試用）────────────────────

if __name__ == "__main__":
    print("=== 測試組合 ===")
    p = build_prompt(SFW.CAFE, angle=ANGLES.CANDID, style=STYLES.FILM_GRAIN, name="林芮安")
    print(p)
    print()
    print("=== 負面關鍵詞 ===")
    print(DEFAULT_NEGATIVE)
