import os
import json
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# تنظیمات
# از متغیر محیطی استفاده میکنیم، اما برای تست لوکال میتونی اینجا کلید بذاری
api_key = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=api_key)
MODEL_NAME = 'gemini-2.5-flash'

@app.route('/')
def home():
    # این دستور فایل index.html را از پوشه templates لود میکند
    return render_template('index.html')

@app.route('/generate_quiz', methods=['POST'])
def generate_quiz():
    data = request.get_json()
    topic = data.get('topic', 'General Knowledge')

    try:
        model = genai.GenerativeModel(MODEL_NAME)
        
        # پرامپت خیلی دقیق برای گرفتن خروجی جیسون
        prompt = (
            f"Generate one multiple-choice trivia question about: '{topic}'. "
            "The language must be Persian (Farsi). "
            "Return ONLY a valid JSON object with this structure: "
            "{'question': '...', 'options': ['A', 'B', 'C', 'D'], 'correct_index': 0} "
            "correct_index is the number of the correct option (0, 1, 2, or 3). "
            "Do not use Markdown formatting."
        )

        response = model.generate_content(prompt)
        
        # تمیزکاری متن خروجی
        cleaned_text = response.text.replace('```json', '').replace('```', '').strip()
        quiz_data = json.loads(cleaned_text)
        
        return jsonify(quiz_data)

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "خطا در تولید سوال. لطفا دوباره تلاش کنید."}), 500

if __name__ == '__main__':
    app.run(debug=True)
