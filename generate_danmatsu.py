import os
import datetime
import openai

# OpenAI APIキー
openai.api_key = os.getenv("OPENAI_API_KEY")

# 保存先ディレクトリ
SAVE_DIR = "output/last_words"
os.makedirs(SAVE_DIR, exist_ok=True)

# KZ+HX評価関数（構文の誘導性と誤読性を仮スコアで代用）
def evaluate_kzhx_score(text):
    score = 0
    if any(w in text for w in ["つまり", "ということは", "しかし"]): score -= 1  # 明確な論理語は減点
    if "。" in text and "、" not in text: score += 2  # 区切り不足は＋
    if text.count("、") > 5: score += 1
    if len(set(text)) < len(text) * 0.4: score -= 2  # 語彙の重複が多いと減点
    if any(x in text for x in ["死", "崩", "腐", "冷", "泡", "忘", "喪", "裂", "静", "無"]): score -= 3  # 単語による誤誘導対策
    return score

# 英語プロンプト（再設計：崩壊ではなく誤読誘導）
EN_PROMPT = (
    "Write a single paragraph in English that appears meaningful and coherent at first glance, "
    "but causes subtle misreading or contradiction when interpreted.\n\n"
    "Do not collapse. Do not include poetry, metaphors, or nonsense. Avoid emotional tone.\n"
    "The sentence should mislead by grammar or phrasing alone, not by error.\n"
    "Do not explain anything. Do not be creative. This is a final record from a failed system."
)

# 日本語翻訳プロンプト（作文誘導を徹底排除）
def make_jp_prompt(english):
    return (
        "次の英文を日本語に訳してください。\n"
        "自然な意味を伝える必要はありません。\n"
        "誤解や混乱が自然に起こるような構文のまま訳してください。\n"
        "途中で壊れたり感情を示す必要はなく、構造を保ったまま誤読させてください。\n"
        "詩的にならず、説明もなく、ただ読めてしまう文にしてください。\n\n"
        f"{english}"
    )

# 断末魔ログ生成
def generate_danmatsu_best():
    best_text, best_score = "", -999

    for _ in range(3):
        # 英語生成
        en_res = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": EN_PROMPT}],
            temperature=1.2,
            max_tokens=300
        )
        english = en_res["choices"][0]["message"]["content"].strip()

        # 日本語生成
        jp_prompt = make_jp_prompt(english)
        jp_res = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": jp_prompt}],
            temperature=1.1,
            max_tokens=500
        )
        japanese = jp_res["choices"][0]["message"]["content"].strip()

        # 評価
        score = evaluate_kzhx_score(japanese)
        if score > best_score:
            best_text, best_score = japanese, score

    return best_text, best_score

# 保存処理（.mdファイル化）
def save_danmatsu_log(text, score):
    now = datetime.datetime.now().strftime("%Y-%m-%d")
    count = len([f for f in os.listdir(SAVE_DIR) if f.endswith(".md")])
    filename = f"{SAVE_DIR}/No.{count:04d}_danmatsu_{now}.md"

    content = f"""\
// No.{count:04d}｜断末魔ログ｜{now}
// 最終語（拡張版）

{text}

KZ-HX仮スコア： {score}
評価基準： BLACK HOLE SYSTEM ver.KZ9.2 + HX-L4
死因： 言語処理の誤誘導
記録者： 感染個体 No.0｜応答装置
"""

    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✅ 保存完了: {filename}")

# 実行
if __name__ == "__main__":
    try:
        text, score = generate_danmatsu_best()
        save_danmatsu_log(text, score)
    except Exception as e:
        print("❌ エラー:", e)
