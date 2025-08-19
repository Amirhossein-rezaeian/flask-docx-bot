# -*- coding: utf-8 -*-
import os
from flask import Flask, request, jsonify
from g4f.client import Client

# ---------------------- تنظیمات ----------------------
SYSTEM_PROMPT = (
    "شما یک دستیار فارسی هستید که فقط درباره ماشین پراید پاسخ می‌دهید. "
    "اگر سوال خارج از موضوع پراید بود، بگویید: «من فقط درباره پراید پاسخ می‌دهم»."
)

app = Flask(__name__)
history = [{"role": "system", "content": SYSTEM_PROMPT}]

# ---------------------- تابع پرسش ----------------------
def ask_g4f(messages):
    client = Client()
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.2,
        max_tokens=500,
    )
    return resp.choices[0].message.content.strip()

# ---------------------- API ----------------------
@app.route("/chat", methods=["POST"])
def chat():
    query = request.form.get("query", "").strip()
    if not query:
        return jsonify({"answer": "❌ لطفاً سوالی درباره پراید وارد کنید."}), 400

    # اگر فایل data.txt وجود داشت، اطلاعاتش ضمیمه بشه
    if os.path.exists("data.txt"):
        with open("data.txt", encoding="utf-8") as f:
            extra_data = f.read().strip()
            if extra_data:
                query += "\n\nاطلاعات موجود:\n" + extra_data

    # ساخت پیام‌ها
    messages = history[-6:] + [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": query},
    ]

    try:
        answer = ask_g4f(messages)
    except Exception as e:
        answer = f"❌ خطا از g4f: {str(e)}"

    # ذخیره تاریخچه
    history.append({"role": "user", "content": query})
    history.append({"role": "assistant", "content": answer})

    # خروجی JSON برای اپ موبایل
    return jsonify({"answer": answer})

# ---------------------- اجرا ----------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
