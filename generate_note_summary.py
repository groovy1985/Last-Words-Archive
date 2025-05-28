import os
import glob
from datetime import datetime, timedelta

# フォルダ設定
log_dir = "output/logs"
note_dir = "note"
os.makedirs(note_dir, exist_ok=True)

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
            excerpt = "".join(lines[6:10]).strip()
            entries.append({
                "date": date,
                "title": parts[0].replace("#", "").strip(),
                "excerpt": excerpt
            })
        except Exception:
            continue

# 日付判定
today = datetime.now().date()
week_ago = today - timedelta(days=7)
weekly_entries = [e for e in entries if e["date"] > week_ago]

# Markdown出力
note_filename = os.path.join(note_dir, f"{today.isoformat()}_note.md")
with open(note_filename, "w", encoding='utf-8') as f:
    f.write(f"# 週次断末魔まとめ｜{week_ago} 〜 {today}\n\n")
    for entry in weekly_entries:
        f.write(f"## {entry['title']}｜{entry['date']}\n\n")
        f.write(f"{entry['excerpt']}\n\n")
        f.write("---\n\n")

print(f"[LOG] note summary saved: {note_filename}")
