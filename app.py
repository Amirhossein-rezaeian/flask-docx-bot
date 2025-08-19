# -*- coding: utf-8 -*-
import os
import re
from flask import Flask, request, jsonify, render_template_string

# ---------------------- تنظیمات ----------------------
SYSTEM_PROMPT_FA = (
    "تو یک دستیار فارسی هستی که فقط و فقط به پرسش‌های مربوط به ماشین پراید پاسخ می‌دهی. "
    "اگر سوال خارج از موضوع پراید بود، صریح بگو: «من فقط درباره پراید پاسخ می‌دهم»."
    "جواب دقیق، فنی و روان بده."
)

# ---------------------- g4f Client ----------------------
def clean_answer(text: str) -> str:
    """پاکسازی خروجی مدل از نشانه‌گذاری‌های ناخواسته"""
    text = re.sub(r"[*#]+", "", text)  # حذف * و #
    text = re.sub(r"\n\s*\n", "\n", text)  # حذف خطوط خالی اضافی
    return text.strip()

def ask_g4f(messages):
    try:
        from g4f.client import Client
        client = Client()
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.2,
            max_tokens=500,
        )
        raw_answer = resp.choices[0].message.content.strip()
        return clean_answer(raw_answer)
    except Exception as e:
        return f"❌ خطا در ارتباط با g4f: {e}"

# ---------------------- Flask ----------------------
app = Flask(__name__)
history = [{"role": "system", "content": SYSTEM_PROMPT_FA}]

# ---------------------- HTML Template ----------------------
HTML_TEMPLATE = """
<!doctype html>
<html lang="fa">
<head>
<meta charset="utf-8">
<title>🚗 ربات پراید</title>
<style>
body { font-family: Tahoma, sans-serif; direction: rtl; margin: 20px; background: #f4f6f7; }
h1 { color: #2c3e50; text-align:center; }
textarea { width: 100%; padding: 10px; border-radius: 8px; border: 1px solid #ccc; }
button { padding: 10px 20px; border:none; border-radius:8px; background:#2980b9; color:#fff; cursor:pointer; }
button:hover { background:#3498db; }
.response { background: #ecf0f1; padding: 15px; margin-top: 20px; border-radius: 8px; white-space: pre-line; }
.container { max-width:600px; margin:auto; }
</style>
</head>
<body>
<div class="container">
<h1>🚗 ربات مخصوص پراید</h1>
<p>سوالت درباره پراید رو بپرس:</p>

<form method="post">
<textarea name="query" rows="3" placeholder="مثلا: مصرف سوخت پراید چقدره؟" required></textarea><br>
<button type="submit">بپرس</button>
</form>

{% if answer %}
<div class="response">
<b>📤 پاسخ:</b>
<p>{{ answer }}</p>
</div>
{% endif %}
</div>
</body>
</html>
"""

# ---------------------- Routes ----------------------
@app.route("/", methods=["GET", "POST"])
def index():
    answer = None
    if request.method == "POST":
        q = (request.form.get("query") or "").strip()
        if not q:
            answer = "❌ لطفا سوالت را وارد کن."
        else:
            messages = history[-6:] + [
                {"role": "system", "content": SYSTEM_PROMPT_FA},
                {"role": "user", "content": q},
            ]
            answer = ask_g4f(messages)
            history.append({"role": "user", "content": q})
            history.append({"role": "assistant", "content": answer})

    return render_template_string(HTML_TEMPLATE, answer=answer)


@app.route("/chat", methods=["POST"])
def chat_api():
    """مسیر API برای اپلیکیشن موبایل"""
    q = (request.form.get("query") or "").strip()
    if not q:
        return jsonify({"error": "❌ سوال خالی است"}), 400

    messages = history[-6:] + [
        {"role": "system", "content": SYSTEM_PROMPT_FA},
        {"role": "user", "content": q},
    ]
    answer = ask_g4f(messages)
    history.append({"role": "user", "content": q})
    history.append({"role": "assistant", "content": answer})

    return jsonify({"answer": answer})

 
# ---------------------- Run ----------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
