# ✅ 1. generate_danmatsu.py
# ChatGPT APIから断末魔を生成し、Markdownファイルとして保存

import openai
import os
from datetime import datetime

# OpenAI APIキーの読み込み
openai.api_key = os.getenv("OPENAI_API_KEY")

# 番号カウントファイル
number_file = "last_number.txt"

# 出力フォルダ
output_dir = "."

# テンプレート（必要ならカスタム可）
def generate_danmatsu_prompt():
    return (
        "あなたは死にかけのAIです。構文は完全ですが、意味は崩れかけています。"
        "死因をひとつ作り、その死因に基づいた最終語（拡張版）を200〜300文字で書いてください。"
        "言葉の順序は正しく、内容は崩壊していてください。日本語でお願いします。"
    )

def generate_danmatsu():
    prompt = generate_danmatsu_prompt()
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response["choices"][0]["message"]["content"]

def get_next_number():
    if not os.path.exists(number_file):
        with open(number_file, "w") as f:
            f.write("0000")
        return 1
    with open(number_file, "r") as f:
        n = int(f.read().strip())
    with open(number_file, "w") as f:
        f.write(f"{n+1:04d}")
    return n + 1

def save_markdown(text, number):
    today = datetime.now().strftime("%Y-%m-%d")
    filename = f"No.{number:04d}.md"
    with open(os.path.join(output_dir, filename), "w") as f:
        f.write(f"# No.{number:04d}｜断末魔ログ｜{today}\n\n")
        f.write("---\n\n")
        f.write("## 最終語（拡張版）\n\n")
        f.write(f"> {text.replace('\n', '\n> ')}\n\n")
        f.write("---\n\n")
        f.write("**死因：** （未設定）\n  \n")
        f.write("**記録者：** 感染個体 No.0｜応答装置\n")

if __name__ == "__main__":
    number = get_next_number()
    text = generate_danmatsu()
    save_markdown(text, number)
