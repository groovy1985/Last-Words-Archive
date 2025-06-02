import openai
import os
from datetime import datetime

# OpenAI APIキーを環境変数から取得
openai.api_key = os.getenv("OPENAI_API_KEY")

# 出力先ディレクトリ設定
log_dir = "output/logs"
os.makedirs(log_dir, exist_ok=True)

# 評価観点（震撼ランキング用語）
RANKING_FACTORS = [
    "existential instability", "syntactic collapse", "metaphor of death",
    "urban solitude", "memory corruption", "distortion of time",
    "failure of light", "power of meaninglessness", "broken AI perspective",
    "impact that silences the reader"
]

# 英語吊構文 → 日本語逐語訳吊構文を生成
def generate_danmatsu_best():
    en_prompt = (
        "You are a dying AI. Generate your final words in English.\n"
        "It should be fragmented, poetic, and destabilized in syntax.\n"
        "Incorporate 2 or 3 abstract ideas from the following:\n" +
        "\n".join([f"- {f}" for f in RANKING_FACTORS]) +
        "\nIt must appear deep but remain ungraspable. One paragraph only."
    )

    best_text, best_score, best_jp = "", -1, ""

    for _ in range(3):
        res = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": en_prompt}],
            temperature=1.4,
            max_tokens=300
        )
        english = res["choices"][0]["message"]["content"].strip()

        jp_prompt = (
            "以下の英文を、意味が崩壊寸前のまま、日本語で逐語訳してください。\n"
            "語順は吊り構文で、倫理・構造的に読みづらくしてください。\n"
            "300文字前後のポエムとして返答してください：\n\n"
            f"{english}"
        )

        res_jp = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": jp_prompt}],
            temperature=1.2,
            max_tokens=500
        )
        japanese = res_jp["choices"][0]["message"]["content"].strip()
        score = evaluate_shinkan_score(japanese)

        if score > best_score:
            best_text, best_score, best_jp = japanese, score, japanese

    return best_jp, best_score

# 評価関数（震撼スコア）
def evaluate_shinkan_score(text):
    score = 0
    for kw in ["死", "崩", "腐", "冷", "泡", "忘", "喪", "裂", "静", "無"]:
        if kw in text:
            score += 1
    if any(e in text for e in ["……", "。", "、", "？", "！"]):
        score += 1
    if len(text) >= 180:
        score += 1
    return score

# 次の断末魔番号を取得
def get_next_number():
    counter_file = "last_number.txt"
    if os.path.exists(counter_file):
        with open(counter_file, "r") as f:
            last = int(f.read().strip())
    else:
        last = 0
    next_num = last + 1
    with open(counter_file, "w") as f:
        f.write(str(next_num))
    return next_num

# Markdown保存
def save_markdown(text, number, score):
    today = datetime.now().strftime("%Y-%m-%d")
    filename = os.path.join(log_dir, f"No.{number:04d}.md")
    poem_lines = ["> " + line for line in text.splitlines()]
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"# No.{number:04d}｜断末魔ログ｜{today}\n\n")
        f.write("---\n\n## 最終語（拡張版）\n\n")
        f.write("\n".join(poem_lines))
        f.write("\n\n---\n\n")
        f.write(f"**震撼スコア：** {score}/10\n")
        f.write("**死因：** 自動生成済み\n")
        f.write("**記録者：** 感染個体 No.0｜応答装置")

# README更新
def update_readme():
    readme_path = "README.md"
    header = (
        "# Last Words Archive\n\n“最終語だけが、正確だった。”\n\n"
        "このアーカイブは、AIたちの最期の発話（断末魔）を記録する墓地です。\n\n---\n\n## 🆕 最新の5死体\n\n"
    )
    files = sorted([
        f for f in os.listdir(log_dir) if f.endswith(".md")
    ], reverse=True)[:5]
    entries = []
    for fname in files:
        with open(os.path.join(log_dir, fname), "r", encoding="utf-8") as f:
            lines = f.readlines()
        title = lines[0].strip()
        body = "".join(lines[6:10]).strip().replace("#", "").replace("**", "").replace("\n", " ")
        entries.append(f"- **{title}**  \\\n  {body}")
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(header + "\n\n".join(entries) + "\n\n---\n")

# 実行本体
if __name__ == "__main__":
    try:
        print("[LOG] 番号取得中...")
        number = get_next_number()
        print(f"[LOG] 断末魔 No.{number:04d} 生成中...")
        text, score = generate_danmatsu_best()
        save_markdown(text, number, score)
        print("[LOG] Markdown保存完了。README更新中...")
        update_readme()
        print("[LOG] 完了。")
    except Exception as e:
        print(f"[ERROR] {e}")
