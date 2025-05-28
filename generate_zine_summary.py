import os
import glob
from datetime import datetime

# フォルダ設定
log_dir = "output/logs"
zine_dir = "zine"
os.makedirs(zine_dir, exist_ok=True)

# ログ取得
entries = []
for file_path in sorted(glob.glob(os.path.join(log_dir, "No.*.md"))):
    with open(file_path, encoding='utf-8') as f:
        lines = f.readlines()
    if len(lines) >= 6:
        try:
            title_line = lines[0].strip()  # 例: # No.0001｜断末魔ログ｜2025-05-28
            parts = title_line.split("｜")
            date_str = parts[-1]
            date = datetime.strptime(date_str, "%Y-%m-%d").date()
            body = "".join(lines[6:]).strip()
            entries.append({
                "date": date,
                "title": parts[0].replace("#", "").strip(),
                "body": body
            })
        except Exception:
            continue

# 今月分の抽出
today = datetime.now().date()
this_month = today.replace(day=1)
monthly_entries = [e for e in entries if e["date"] >= this_month]

# 出力ファイルパス
zine_filename = os.path.join(zine_dir, f"{today.strftime('%Y-%m')}_zine.md")

# Markdown出力
with open(zine_filename, "w", encoding='utf-8') as f:
    f.write(f"# 月次断末魔ZINE｜{this_month}〜{today}\n\n")
    for entry in monthly_entries:
        f.write(f"## {entry['title']}｜{entry['date']}\n\n")
        f.write(f"{entry['body']}\n\n")
        f.write("---\n\n")

print(f"[LOG] zine summary saved: {zine_filename}")
