import os
import json
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# تنظیمات API
api_key = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=api_key)
MODEL_NAME = 'gemini-2.5-flash'

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate_quiz', methods=['POST'])
def generate_quiz():
    data = request.get_json()
    topic = data.get('topic', 'General Knowledge')

    try:
        # --- تغییر مهم: فعال‌سازی حالت JSON ---
        model = genai.GenerativeModel(
            MODEL_NAME,
            generation_config={"response_mime_type": "application/json"}
        )
        
        prompt = (
            f"Generate one multiple-choice trivia question about: '{topic}'. "
            "The language must be Persian (Farsi). "
            "The output MUST be a valid JSON object with this structure: "
            "{\"question\": \"String\", \"options\": [\"String\", \"String\", \"String\", \"String\"], \"correct_index\": Integer} "
            "Ensure specific keys and values are enclosed in double quotes."
        )

        response = model.generate_content(prompt)
        
        # چون حالت JSON فعال است، خروجی مطمئن‌تر است اما محض احتیاط تمیزکاری می‌کنیم
        cleaned_text = response.text.strip()
        
        # اگر مدل اشتباهاً مارک‌داون گذاشت، آن را حذف کن
        if cleaned_text.startswith("```json"):
            cleaned_text = cleaned_text.replace("```json", "").replace("```", "")
            
        quiz_data = json.loads(cleaned_text)
        
        return jsonify(quiz_data)

    except json.JSONDecodeError as e:
        print(f"JSON Error: {e}")
        print(f"Raw Response: {response.text}") # این در لاگ‌ها چاپ می‌شود تا ببینیم چی فرستاده
        return jsonify({"error": "هوش مصنوعی خروجی نامعتبر تولید کرد، لطفا دوباره دکمه را بزنید."}), 500
        
    except Exception as e:
        print(f"General Error: {e}")
        return jsonify({"error": "خطا در برقراری ارتباط با سرور."}), 500

if __name__ == '__main__':
    app.run(debug=True)
