import os
import sqlite3
from datetime import timedelta
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'super_secret_kurs_ishi_kaliti_2026_final'

# Foydalanuvchi sessiyasini 30 kun eslab qolish uchun
@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(days=30)

# Ma'lumotlar bazasiga ulanish funksiyasi
def get_db_connection():
    conn = sqlite3.connect('yangi_baza.db')
    conn.row_factory = sqlite3.Row
    return conn

# Jadvallar va hamma 30 ta savolni yaratish
def ozi_avtomat_baza_yaratish():
    db = get_db_connection()
    cursor = db.cursor()
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS foydalanuvchilar (
        id INTEGER PRIMARY KEY AUTOINCREMENT, ism TEXT, tel TEXT UNIQUE, parol TEXT
    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS fanlar (
        id INTEGER PRIMARY KEY AUTOINCREMENT, nomi TEXT
    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS savollar (
        id INTEGER PRIMARY KEY AUTOINCREMENT, fan_id INTEGER, savol_matni TEXT,
        variant_a TEXT, variant_b TEXT, variant_c TEXT, variant_d TEXT, togri_javob TEXT
    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS natijalar (
        id INTEGER PRIMARY KEY AUTOINCREMENT, user_tel TEXT, user_ism TEXT, fan_nomi TEXT, ball REAL, sana TEXT DEFAULT CURRENT_TIMESTAMP
    )''')
    db.commit()
    
    # Agar fanlar jadvali bo'sh bo'lsa, ma'lumot kiritamiz
    cursor.execute("SELECT COUNT(*) FROM fanlar")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO fanlar (nomi) VALUES ('Matematika'), ('Dasturlash (Python)'), ('Ingliz tili')")
        db.commit()
        
        hamma_savollar = [
            # Matematika (10 ta savol)
            (1, '5 * 5 + 5 nechaga teng?', '25', '30', '35', '20', 'B'),
            (1, '12 ning kvadrati qancha?', '144', '122', '134', '154', 'A'),
            (1, 'Tub sonni toping.', '4', '6', '9', '7', 'D'),
            (1, 'Uchburchak ichki burchaklari yig`indisi?', '90', '180', '360', '270', 'B'),
            (1, 'log2(8) nechaga teng?', '2', '3', '4', '5', 'B'),
            (1, '0.5 qaysi kasrga teng?', '1/2', '1/4', '1/3', '2/5', 'A'),
            (1, 'Doiraning yuzi formulasi qaysi?', '2pr', 'pr^2', 'ab', 'a^2', 'B'),
            (1, '100 ning 10% i qancha bo`ladi?', '5', '10', '20', '50', 'B'),
            (1, 'Kvadratning tomoni 4 bo`lsa, uning perimetri qancha?', '8', '12', '16', '20', 'C'),
            (1, 'Eng kichik juft son qaysi?', '0', '2', '4', '1', 'B'),
            
            # Dasturlash Python (10 ta savol)
            (2, 'Konsolga chiqarish buyrug`i qaysi?', 'input()', 'print()', 'output()', 'echo', 'B'),
            (2, 'Ro`yxat qavsi qaysi?', '()', '{}', '[]', '<>', 'C'),
            (2, 'Python dasturlash tili qachon yaratilgan?', '1991', '2000', '1985', '1995', 'A'),
            (2, 'O`zgaruvchi turini aniqlash funksiyasi qaysi?', 'type()', 'len()', 'int()', 'str()', 'A'),
            (2, 'Satrlarni birlashtirish belgisi qaysi?', '*', '-', '/', '+', 'D'),
            (2, 'Izoh qoldirish (comment) belgisi qaysi?', '//', '/*', '#', ';', 'C'),
            (2, 'Lug`at (dictionary) yaratish qavsi qaysi?', '()', '{}', '[]', '<>', 'B'),
            (2, 'Kodni sindirish/to`xtatish kalit so`zi qaysi?', 'continue', 'pass', 'break', 'exit', 'C'),
            (2, 'Python fayllari qaysi kengaytmada saqlanadi?', '.py', '.txt', '.html', '.exe', 'A'),
            (2, 'Qaysi ma`lumot turi faqat True yoki False qiymat oladi?', 'int', 'string', 'list', 'boolean', 'D'),

            # Ingliz tili (10 ta savol)
            (3, 'I ___ a student.', 'am', 'is', 'are', 'be', 'A'),
            (3, 'She ___ to school every day.', 'go', 'goes', 'going', 'gone', 'B'),
            (3, 'Find the past simple form of "go".', 'goed', 'gone', 'went', 'goes', 'C'),
            (3, 'Which one is a noun?', 'beautiful', 'run', 'apple', 'quickly', 'C'),
            (3, 'What is the opposite of "hot"?', 'warm', 'cold', 'ice', 'cool', 'B'),
            (3, 'They ___ football yesterday.', 'played', 'play', 'playing', 'plays', 'A'),
            (3, 'He is the ___ boy in the class.', 'tall', 'taller', 'tallest', 'more tall', 'C'),
            (3, 'Look! It ___ raining.', 'is', 'am', 'are', 'be', 'A'),
            (3, 'We have been here ___ 2 hours.', 'for', 'since', 'at', 'in', 'A'),
            (3, 'Choose the correct spelling.', 'Beautiful', 'Beautifull', 'Butiful', 'Bautifull', 'A')
        ]
        
        cursor.executemany("""
            INSERT INTO savollar (fan_id, savol_matni, variant_a, variant_b, variant_c, variant_d, togri_javob)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, hamma_savollar)
        db.commit()
    db.close()

# Tizimga kirish (Asosiy sahifa)
@app.route('/', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        tel = request.form['tel']
        parol = request.form['parol']
        
        db = get_db_connection()
        user = db.execute("SELECT * FROM foydalanuvchilar WHERE tel = ?", (tel,)).fetchone()
        db.close()
        
        if user and check_password_hash(user['parol'], parol):
            session['user_id'] = user['id']
            session['user_ism'] = user['ism']
            session['user_tel'] = user['tel']
            return redirect(url_for('dashboard'))
        else:
            flash("Telefon raqam yoki parol xato!", "danger")
            
    return render_template('login.html')

# Ro'yxatdan o'tish sahifasi
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        ism = request.form['ism']
        tel = request.form['tel']
        parol = request.form['parol']
        
        hashlangan_parol = generate_password_hash(parol)
        
        db = get_db_connection()
        try:
            db.execute("INSERT INTO foydalanuvchilar (ism, tel, parol) VALUES (?, ?, ?)", (ism, tel, hashlangan_parol))
            db.commit()
            flash("Muvaffaqiyatli ro'yxatdan o'tdingiz. Tizimga kiring!", "success")
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash("Bu telefon raqami allaqachon ro'yxatdan o'tgan!", "danger")
        finally:
            db.close()
            
    return render_template('register.html')

# Boshqaruv paneli (Fanlar va Natijalar ko'rinadigan joy)
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    db = get_db_connection()
    fanlar = db.execute("SELECT * FROM fanlar").fetchall()
    natijalar = db.execute("SELECT * FROM natijalar WHERE user_tel = ? ORDER BY sana DESC", (session['user_tel'],)).fetchall()
    db.close()
    
    return render_template('dashboard.html', fanlar=fanlar, natijalar=natijalar)

# Test topshirish jarayoni
@app.route('/test/<int:fan_id>', methods=['GET', 'POST'])
def test(fan_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    db = get_db_connection()
    fan = db.execute("SELECT * FROM fanlar WHERE id = ?", (fan_id,)).fetchone()
    savollar = db.execute("SELECT * FROM savollar WHERE fan_id = ?", (fan_id,)).fetchall()
    
    if request.method == 'POST':
        togri_javoblar_soni = 0
        jami_savollar = len(savollar)
        
        for savol in savollar:
            tanlangan_javob = request.form.get(f"savol_{savol['id']}")
            if tanlangan_javob == savol['togri_javob']:
                togri_javoblar_soni += 1
                
        ball = (togri_javoblar_soni / jami_savollar) * 100 if jami_savollar > 0 else 0
        ball = round(ball, 1)
        
        # Natijani bazaga yozish
        db.execute("""
            INSERT INTO natijalar (user_tel, user_ism, fan_nomi, ball) 
            VALUES (?, ?, ?, ?)
        """, (session['user_tel'], session['user_ism'], fan['nomi'], ball))
        db.commit()
        db.close()
        
        flash(f"Test yakunlandi! Siz {jami_savollar} ta savoldan {togri_javoblar_soni} tasiga to'g'ri javob berdingiz ({ball}%).", "info")
        return redirect(url_for('dashboard'))
        
    db.close()
    return render_template('test.html', fan=fan, savollar=savollar)

# Tizimdan chiqish
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    ozi_avtomat_baza_yaratish()
    app.run(debug=True)
