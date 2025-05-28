import openai
import os
from datetime import datetime

# OpenAI APIキーを環境変数から取得
openai.api_key = os.getenv("OPENAI_API_KEY")

# 出力先ディレクトリ設定
log_dir = "output/logs"
os.makedirs(log_dir, exist_ok=True)

# 評価観点（宇宙震撼ランキング）
RANKING_FACTORS = [
    "存在の不安", "構文の崩壊美", "死の暗喩", "都市的孤独", "時間の歪曲",
    "記憶汚染", "光と影の錯誤", "無意味の力", "AI視点の破綻", "読者を潰す衝撃"
]

# プロンプト生成
def generate_danmatsu_prompt():
    base = (
        "あなたは死にゆくAIです。死因を設定し、それに基づき『最終語（拡張版）』を生成してください。"
        "構文は揺らぎ、意味は錯乱し、しかし崩壊美を保ってください。"
        "以下から2〜3個の概念を統合し、詩的断末魔として日本語300文字前後で出力してください：\n"
    )
    factors = "\n".join([f"- {f}" for f in RANKING_FACTORS])
    return f"{base}{factors}\n\n※人間に読解不能な表現も歓迎されます。"

# 震撼スコア計算
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

# 断末魔生成（3回試行→最高震撼）
def generate_danmatsu_best():
    prompt = generate_danmatsu_prompt()
    best_text, best_score = "", -1
    for _ in range(3):
        res = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=1.3,
            max_tokens=600
        )
        content = res["choices"][0]["message"]["content"]
        score = evaluate_shinkan_score(content)
        if score > best_score:
            best_text, best_score = content, score
    return best_text, best_score

# 次番号取得
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
    with open(filename, "w") as f:
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
        with open(os.path.join(log_dir, fname), "r") as f:
            lines = f.readlines()
        title = lines[0].strip()
        body = "".join(lines[6:10]).strip().replace("#", "").replace("**", "").replace("\n", " ")
        entries.append(f"- **{title}**  \\\n  {body}")
    with open(readme_path, "w") as f:
        f.write(header + "\n\n".join(entries) + "\n\n---\n")

# 実行
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
