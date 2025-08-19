# -*- coding: utf-8 -*-
import os
from flask import Flask, request, render_template_string

# ---------------------- تنظیمات ----------------------
SYSTEM_PROMPT_FA = (
    "تو یک دستیار فارسی هستی که فقط و فقط به پرسش‌های مربوط به ماشین پراید پاسخ می‌دهی. "
    "اگر سوال خارج از موضوع پراید بود، صریح بگو: «من فقط درباره پراید پاسخ می‌دهم»."
    "جواب دقیق، فنی و روان بده."
)

# ---------------------- ابزارها ----------------------
def ask_g4f(messages):
    from g4f.client import Client
    client = Client()
    resp = client.chat.completions.create(
        model="gpt-4o-mini",   # یا gpt-3.5-turbo اگر مشکلی بود
        messages=messages,
        temperature=0.2,
        max_tokens=500,
    )
    return resp.choices[0].message.content.strip()

# ---------------------- Flask ----------------------
app = Flask(__name__)
history = [{"role": "system", "content": SYSTEM_PROMPT_FA}]

# ---------------------- رابط وب ----------------------
HTML_TEMPLATE = """
<!doctype html>
<html lang="fa">
<head>
<meta charset="utf-8">
<title>🤖 ربات پراید</title>
<style>
body { font-family: Tahoma, sans-serif; direction: rtl; margin: 30px; background-color: #f9f9f9; }
h1 { color: #2c3e50; }
textarea { width: 100%; padding: 10px; margin: 10px 0; box-sizing: border-box; }
input[type=submit] { padding: 10px 20px; }
div.response { background: #ecf0f1; padding: 15px; margin-top: 20px; border-radius: 8px; white-space: pre-wrap; }
</style>
</head>
<body>
<h1>🚗 ربات مخصوص ماشین پراید</h1>
<p>هر سوالی درباره پراید داری بپرس، من جواب می‌دم.</p>

<form method="post">
<textarea name="query" rows="3" placeholder="سوالت درباره پراید رو اینجا بنویس..." required></textarea>
<br>
<input type="submit" value="بپرس">
</form>

{% if answer %}
<div class="response">
<h3>📤 پاسخ:</h3>
<p>{{ answer }}</p>
</div>
{% endif %}
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    answer = None
    if request.method == "POST":
        q = (request.form.get("query") or "").strip()

        # اضافه کردن متن فایل data.txt در صورت وجود
        context = ""
        if os.path.exists("data.txt"):
            with open("data.txt", encoding="utf-8") as f:
                context = f.read()
            q = f"{q}\n\nاطلاعات فنی موجود:\n{context}"

        messages = history[-6:] + [
            {"role": "system", "content": SYSTEM_PROMPT_FA},
            {"role": "user", "content": q},
        ]

        try:
            model_answer = ask_g4f(messages)
        except Exception as e:
            model_answer = f"❌ خطا از g4f: {e}"

        answer = model_answer
        history.append({"role": "user", "content": q})
        history.append({"role": "assistant", "content": answer})

    return render_template_string(HTML_TEMPLATE, answer=answer)

# ---------------------- اجرا ----------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
