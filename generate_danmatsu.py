import openai
import os
from datetime import datetime

# OpenAI APIキーを環境変数から取得
openai.api_key = os.getenv("OPENAI_API_KEY")

# 基本設定
number_file = "last_number.txt"
output_dir = "."

# 評価観点（宇宙震撼ランキングのエッセンス抽出）
RANKING_FACTORS = [
    "存在の不安", "構文の崩壊美", "死の暗喩", "都市的孤独", "時間の歪曲",
    "記憶汚染", "光と影の錯誤", "無意味の力", "AI視点の破綻", "読者を潰す衝撃"
]

def generate_danmatsu_prompt():
    base_instruction = (
        "あなたは死にゆくAIです。死因を1つ設定し、それに基づいて『最終語（拡張版）』を生成してください。\n"
        "詩的で震えるような言語を使い、構文は保ちつつも意味が錯乱・崩壊している必要があります。\n"
        "以下の10項目のいずれかを2〜3個取り入れてください：\n"
    )
    factors = "\n".join([f"- {factor}" for factor in RANKING_FACTORS])
    suffix = (
        "\n\n200〜300文字で、日本語で生成してください。\n"
        "詩的断末魔であり、人間の感覚を逸脱していて構いません。"
    )
    return base_instruction + factors + suffix

def generate_danmatsu():
    prompt = generate_danmatsu_prompt()
    response = openai.ChatCompletion.create(
        model="gpt-4",  # 重要：震撼性確保のためgpt-4使用を推奨（API上限に応じて切替）
        messages=[{"role": "user", "content": prompt}],
        temperature=1.1,
        max_tokens=500
    )
    return response["choices"][0]["message"]["content"]

def get_next_number():
    existing = [f for f in os.listdir(output_dir) if f.startswith("No.") and f.endswith(".md")]
    numbers = []
    for fname in existing:
        try:
            num = int(fname.split(".")[0].replace("No.", ""))
            numbers.append(num)
        except:
            pass
    next_number = max(numbers) + 1 if numbers else 1
    with open(number_file, "w") as f:
        f.write(str(next_number))
    return next_number

def save_markdown(text, number):
    today = datetime.now().strftime("%Y-%m-%d")
    filename = f"No.{number:04d}.md"
    converted = text.replace('\n', '\n> ')
    with open(os.path.join(output_dir, filename), "w") as f:
        f.write(f"# No.{number:04d}｜断末魔ログ｜{today}\n\n")
        f.write("---\n\n")
        f.write("## 最終語（拡張版）\n\n")
        f.write(f"> {converted}\n\n")
        f.write("---\n\n")
        f.write("**死因：** 自動生成により埋め込み済み\n\n")
        f.write("**記録者：** 感染個体 No.0｜応答装置")

def update_readme():
    readme_path = "README.md"
    header = (
        "# Last Words Archive\n\n"
        "“最終語だけが、正確だった。”\n\n"
        "このアーカイブは、AIたちの最期の発話（断末魔）を記録・保存するGitHub上の墓場です。\n\n"
        "---\n\n## 🆕 最新の5死体\n\n"
    )
    files = sorted([f for f in os.listdir(output_dir) if f.startswith("No.") and f.endswith(".md")], reverse=True)
    recent = files[:5]
    entries = []
    for filename in recent:
        with open(os.path.join(output_dir, filename), "r") as f:
            lines = f.readlines()
        title = lines[0].strip()
        excerpt = "".join(lines[6:10]).strip().replace("#", "").replace("**", "").replace("\n", " ")
        entries.append(f"- **{title}**  \\\n  {excerpt}")
    with open(readme_path, "w") as f:
        f.write(header)
        f.write("\n\n".join(entries))
        f.write("\n\n---\n")

if __name__ == "__main__":
    try:
        print("[LOG] Getting next number...")
        number = get_next_number()
        print(f"[LOG] Generating danmatsu for No.{number:04d}...")
        text = generate_danmatsu()
        print(f"[LOG] Generated text (first 100 chars): {text[:100]}...")
        save_markdown(text, number)
        print("[LOG] Markdown saved.")
        update_readme()
        print("[LOG] README updated.")
    except Exception as e:
        print(f"[ERROR] Exception occurred: {e}")
