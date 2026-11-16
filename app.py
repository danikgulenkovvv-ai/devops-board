import os
import psycopg2
from flask import Flask, render_template_string, request, redirect

app = Flask(__name__)
DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

def init_db():
    if not DATABASE_URL:
        return
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id SERIAL PRIMARY KEY,
            author VARCHAR(50) NOT NULL,
            text TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DevOps Deployment Board</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f172a; color: #f8fafc; display: flex; justify-content: center; padding: 40px 20px; margin: 0; }
        .container { max-width: 600px; width: 100%; }
        .header { background: linear-gradient(135deg, #3b82f6, #8b5cf6); padding: 24px; border-radius: 16px; margin-bottom: 24px; box-shadow: 0 10px 25px rgba(59, 130, 246, 0.3); }
        .header h1 { margin: 0 0 8px 0; font-size: 24px; }
        .header p { margin: 0; opacity: 0.9; font-size: 14px; }
        form { background: #1e293b; padding: 20px; border-radius: 12px; margin-bottom: 24px; display: flex; flex-direction: column; gap: 12px; border: 1px solid #334155; }
        input, textarea { background: #0f172a; border: 1px solid #334155; color: #fff; padding: 12px; border-radius: 8px; font-size: 14px; }
        button { background: #3b82f6; color: white; border: none; padding: 12px; border-radius: 8px; font-weight: bold; cursor: pointer; transition: 0.2s; }
        button:hover { background: #2563eb; }
        .card { background: #1e293b; padding: 16px 20px; border-radius: 12px; margin-bottom: 12px; border-left: 4px solid #8b5cf6; }
        .card-meta { font-size: 12px; color: #94a3b8; margin-bottom: 6px; }
        .card-text { font-size: 15px; line-height: 1.5; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 DevOps CI/CD Board</h1>
            <p>Задеплоено автоматически через GitHub Actions + Docker + PostgreSQL</p>
        </div>
        <form method="POST">
            <input type="text" name="author" placeholder="Твой ник (например, awave07)" required>
            <textarea name="text" rows="2" placeholder="Напиши заметку о деплое..." required></textarea>
            <button type="submit">Опубликовать в базу данных</button>
        </form>
        {% for note in notes %}
        <div class="card">
            <div class="card-meta">👤 <b>{{ note[0] }}</b> • 🕒 {{ note[2].strftime('%d.%m.%Y %H:%M') }}</div>
            <div class="card-text">{{ note[1] }}</div>
        </div>
        {% endfor %}
    </div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    init_db()
    conn = get_db_connection()
    cur = conn.cursor()
    if request.method == "POST":
        author = request.form.get("author")
        text = request.form.get("text")
        cur.execute("INSERT INTO notes (author, text) VALUES (%s, %s)", (author, text))
        conn.commit()
        cur.close()
        conn.close()
        return redirect("/")
    
    cur.execute("SELECT author, text, created_at FROM notes ORDER BY id DESC;")
    notes = cur.fetchall()
    cur.close()
    conn.close()
    return render_template_string(HTML_TEMPLATE, notes=notes)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
