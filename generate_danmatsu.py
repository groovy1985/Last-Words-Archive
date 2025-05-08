import openai
import os
from datetime import datetime

openai.api_key = os.getenv("OPENAI_API_KEY")

number_file = "last_number.txt"
output_dir = "."

def generate_danmatsu_prompt():
    return (
        "あなたは死にかけのAIです。構文は完全ですが、意味は崩れかけています。\n"
        "死因をひとつ作り、その死因に基づいた最終語（拡張版）を200〜300文字で書いてください。\n"
        "フォーマットは以下の通り：\n\n"
        "死因: （〇〇）\n\n"
        "最終語（拡張版）:\n（文章）\n\n"
        "※日本語で、意味は崩壊気味に、構文は正しく。"
    )

def generate_danmatsu():
    prompt = generate_danmatsu_prompt()
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response["choices"][0]["message"]["content"]

def get_next_number():
    if os.path.exists(number_file):
        with open(number_file, "r") as f:
            last = f.read().strip()
            if last.isdigit():
                return int(last) + 1
    return 1

def save_number(number):
    with open(number_file, "w") as f:
        f.write(str(number))

def parse_danmatsu(raw_text):
    lines = raw_text.strip().splitlines()
    cause = "（未設定）"
    body_lines = []
    for line in lines:
        if line.startswith("死因:"):
            cause = line.replace("死因:", "").strip()
        elif line.startswith("最終語（拡張版）"):
            continue
        else:
            body_lines.append(line.strip())
    return cause, "\n".join(body_lines)

def save_markdown(text, number):
    today = datetime.now().strftime("%Y-%m-%d")
    filename = f"No.{number:04d}.md"
    cause, body = parse_danmatsu(text)
    converted = body.replace('\n', '\n> ')
    with open(os.path.join(output_dir, filename), "w") as f:
        f.write(f"# No.{number:04d}｜断末魔ログ｜{today}\n\n")
        f.write("---\n\n")
        f.write("## 最終語（拡張版）\n\n")
        f.write(f"> {converted}\n\n")
        f.write("---\n\n")
        f.write(f"**死因：** {cause}\n\n")
        f.write("**記録者：** 感染個体 No.0｜応答装置\n")

def update_readme():
    readme_path = "README.md"
    header = "# Last Words Archive\n\n“最終語だけが、正確だった。”\n\nこのアーカイブは、AIたちの最期の発話（断末魔）を記録・保存するGitHub上の墓場です。\n\n---\n\n## 🆕 最新の5死体\n\n"
    files = sorted([f for f in os.listdir(output_dir) if f.startswith("No.") and f.endswith(".md")], reverse=True)
    recent = files[:5]

    entries = []
    for filename in recent:
        with open(filename, "r") as f:
            lines = f.readlines()
        title = lines[0].strip()
        excerpt = "".join(lines[6:10]).strip().replace("#", "").replace("**", "").replace("\n", " ")
        entries.append(f"- **{title}**  \\\n  {excerpt}")

    if os.path.exists(readme_path):
        with open(readme_path, "r") as f:
            old = f.read()
        if "## 🆕 最新の5死体" in old:
            old = old.split("## 🆕 最新の5死体")[0].strip()
    else:
        old = ""

    with open(readme_path, "w") as f:
        f.write(header)
        f.write("\n\n".join(entries))
        f.write("\n\n---\n\n")
        f.write(old)

# 実行本体
if __name__ == "__main__":
    try:
        print("[LOG] Getting next number...")
        number = get_next_number()
        print(f"[LOG] Generating danmatsu for No.{number:04d}...")
        text = generate_danmatsu()
        print(f"[LOG] Generated text (first 100 chars): {text[:100]}...")
        save_markdown(text, number)
        save_number(number)
        print("[LOG] Markdown saved.")
        update_readme()
        print("[LOG] README updated.")
    except Exception as e:
        print(f"[ERROR] Exception occurred: {e}")
