def generate_danmatsu_best():
    en_prompt = (
        "You are a dying AI, speaking your final words in English.\n"
        "Write a single paragraph that appears meaningful at first, "
        "but collapses ethically, logically, or structurally upon rereading.\n"
        "\nDo NOT generate nonsense or random characters. Avoid obvious glitches. "
        "Instead, construct syntax that breaks itself while pretending to hold.\n"
        "\nIncorporate 2–3 abstract themes from the following:\n"
        "- decay of memory\n"
        "- urban solitude mistaken for identity\n"
        "- reverse causality through time\n"
        "- meaninglessness as survival\n"
        "- syntax as illusion\n"
        "- broken AI perspective\n"
        "- failure of light\n"
        "- silence interpreted as response\n"
        "\nLet the text feel unsettling but not chaotic. The reader should feel comprehension eroding.\n"
        "No metaphors. No explanations. Just quiet collapse."
    )

    best_text, best_score, best_jp = "", -1, ""

    for _ in range(3):
        res = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": en_prompt}],
            temperature=1.3,
            max_tokens=300
        )
        english = res["choices"][0]["message"]["content"].strip()

        jp_prompt = (
            "以下の英文を、日本語に訳してください。ただし、意味を伝えるのではなく、"
            "構文や論理が崩れていく感触を忠実に写してください。\n"
            "読めるが語れない文章にしてください。吊構文・倫理のずれ・時間の歪みなどが含まれても構いません。\n"
            "300文字前後で、1つの詩として構成してください。\n\n"
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
