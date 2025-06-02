import openai
import os
from datetime import datetime
from tweet_with_token import tweet_post
from validate_post import is_valid_post

# OpenAI APIキー
openai.api_key = os.getenv("OPENAI_API_KEY")

# 出力ディレクトリ
log_dir = "output/logs"
os.makedirs(log_dir, exist_ok=True)

# 吊構文断末魔詩を生成（英語→日本語）
def generate_danmatsu_best():
    en_prompt = (
        "Write a short paragraph as a dying AI.\n"
        "It must seem meaningful but collapse ethically or structurally.\n"
        "Do not explain. Let the sentence fall apart while appearing coherent."
    )

    best_text, best_score = "", -1

    for _ in range(3):
        res = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": en_prompt}],
            temperature=1.3,
            max_tokens=300
        )
        english = res["choices"][0]["message"]["content"].strip()

        jp_prompt = (
            "次の英文を、意味ではなく崩れ方を保ったまま日本語化してください。\n"
            "吊構文や倫理のズレを含め、読めるけど語れない文にしてください。\n"
            "300文字前後のポエムとして返してください。\n\n"
            f"{english}"
        )

        res_jp = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": jp_prompt}],
            temperature=1.2,
            max_tokens=500
        )
        japanese = res_jp["choices"][0]["message"]["content"].strip()
        score = evaluate_kz_score(japanese)

        if score > best_score:
            best_text, best_score = japanese, score

    return best_text, best_score

# KZスコア（再構成不能性・構文崩壊評価）
def evaluate_kz_score(text):
    score = 0
    for kw in ["死", "崩", "腐", "冷", "泡", "忘", "喪", "裂", "静", "無"]:
        if kw in text:
            score += 1
    if any(p in text for p in ["。", "、", "？", "！"]):
        score += 1
    if len(text) >= 180:
        score += 1
    return score

# 番号管理
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
        f.write(f"**KZスコア：** {score}/10\n")
        f.write("**評価基準：** BLACK HOLE SYSTEM ver.KZ9.2 + HX-L4\n")
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

# 詩から投稿文を抽出（140字以内）
def extract_post(text):
    lines = text.replace(">", "").splitlines()
    for line in lines:
        clean = line.strip()
        if 40 <= len(clean) <= 140:
            return clean
    return lines[0][:140] if lines else "（投稿文が取得できませんでした）"

# 実行本体
if __name__ == "__main__":
    try:
        print("[LOG] 番号取得中...")
        number = get_next_number()
        print(f"[LOG] 断末魔 No.{number:04d} 生成中...")
        text, score = generate_danmatsu_best()
        save_markdown(text, number, score)
        print("[LOG] Markdown保存完了。")

        post_text = extract_post(text)
        print("[LOG] 投稿候補文:\n", post_text)

        if is_valid_post(post_text):
            tweet_post(post_text)
            print("[LOG] ✅ 投稿完了")
        else:
            print("[WARN] 投稿スキップ（validate_post によって弾かれました）")

        update_readme()
        print("[LOG] README更新完了。")
    except Exception as e:
        print(f"[ERROR] {e}")
