import sqlite3
import time
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

def get_db_connection():
    conn = sqlite3.connect('imtihon_bazasi.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # 1. Foydalanuvchilar jadvali
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS foydalanuvchilar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ism TEXT UNIQUE NOT NULL,
            tel TEXT NOT NULL,
            parol TEXT NOT NULL
        )
    ''')
    
    # 2. Testlar jadvali
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS testlar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fan TEXT NOT NULL,
            savol TEXT NOT NULL,
            variant_a TEXT NOT NULL,
            variant_b TEXT NOT NULL,
            variant_c TEXT NOT NULL,
            variant_d TEXT NOT NULL,
            javob TEXT NOT NULL
        )
    ''')
    
    # 3. Reyting (Natijalar) jadvali — Vaqt va Tel raqam bilan
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS natijalar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ism TEXT NOT NULL,
            tel TEXT NOT NULL,
            fan TEXT NOT NULL,
            to_gri_javoblar INTEGER NOT NULL,
            jami_savollar INTEGER NOT NULL,
            sarflangan_vaqt TEXT NOT NULL
        )
    ''')
    
    # Savollar bo'lmasa avtomat qo'shish
    cursor.execute("SELECT COUNT(*) FROM testlar")
    if cursor.fetchone()[0] == 0:
        barcha_savollar = [
            # --- Matematika ---
            ('Matematika', '5 + 5 nechaga teng?', '8', '9', '10', '11', 'C'),
            ('Matematika', '12 * 4 nechaga teng?', '44', '48', '52', '40', 'B'),
            ('Matematika', '100 / 5 nechaga teng?', '20', '25', '15', '30', 'A'),
            ('Matematika', '7 * 8 nechaga teng?', '54', '56', '58', '60', 'B'),
            ('Matematika', '45 - 15 nechaga teng?', '25', '30', '35', '40', 'B'),
            
            # --- Dasturlash ---
            ('Dasturlash', 'Python-da ekranga maʼlumot chiqarish qaysi funksiya orqali bajariladi?', 'input()', 'print()', 'output()', 'display()', 'B'),
            ('Dasturlash', 'Oʻzgaruvchi turini aniqlash uchun qaysi funksiyadan foydalaniladi?', 'type()', 'kind()', 'int()', 'str()', 'A'),
            ('Dasturlash', 'Python-da roʻyxat (list) qaysi qavslar ichida yoziladi?', '()', '{}', '[]', '<>', 'C'),
            ('Dasturlash', 'Qaysi operator ikki qiymatni tenglikka tekshiradi?', '=', '==', '===', '!=', 'B'),
            ('Dasturlash', 'Python qaysi yili yaratilgan?', '1991', '1995', '2000', '1989', 'A'),
            
            # --- Ingliz tili ---
            ('Ingliz tili', 'He ___ a student.', 'am', 'is', 'are', 'be', 'B'),
            ('Ingliz tili', 'What is the past tense of "GO"?', 'went', 'gone', 'goes', 'going', 'A'),
            ('Ingliz tili', 'Choose the correct plural form: "Child"', 'childs', 'children', 'childrens', 'childes', 'B'),
            ('Ingliz tili', 'I ___ English every day.', 'studies', 'study', 'studying', 'studied', 'B'),
            ('Ingliz tili', 'Which one is a fruit?', 'Carrot', 'Potato', 'Apple', 'Tomato', 'C')
        ]
        cursor.executemany('''
            INSERT INTO testlar (fan, savol, variant_a, variant_b, variant_c, variant_d, javob)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', barcha_savollar)
        
    conn.commit()
    return conn

app = Flask(__name__)
app.secret_key = 'kod_123'

# BOSH SAHIFA
@app.route('/')
def index():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('index.html', user=session['user'])

# RO'YXATDAN O'TISH (REGISTER)
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        ism = request.form.get('ism')
        tel = request.form.get('tel')
        parol = request.form.get('parol')
        
        # Parolni bazaga xavfsiz shifrlab (hash) yozamiz
        shifrlangan_parol = generate_password_hash(parol, method='pbkdf2:sha256')
        
        db = get_db_connection()
        cursor = db.cursor()
        try:
            cursor.execute("INSERT INTO foydalanuvchilar (ism, tel, parol) VALUES (?, ?, ?)", (ism, tel, shifrlangan_parol))
            db.commit()
            db.close()
            
            session['user'] = ism
            session['user_tel'] = tel
            return redirect(url_for('index'))
        except sqlite3.IntegrityError:
            db.close()
            return render_template('register.html', error="Xato! Bu ism band.")
            
    return render_template('register.html')

# TIZIMGA KIRISH (LOGIN)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        ism_yoki_tel = request.form.get('ism')
        parol = request.form.get('parol')
        
        db = get_db_connection()
        cursor = db.cursor()
        
        # Ism yoki Telefon raqam bo'yicha foydalanuvchini qidiramiz
        cursor.execute("SELECT * FROM foydalanuvchilar WHERE ism = ? OR tel = ?", (ism_yoki_tel, ism_yoki_tel))
        user = cursor.fetchone()
        db.close()
        
        # Parolni shifrlangan kod bilan Python ichida solishtiramiz
        if user and check_password_hash(user['parol'], parol):
            session['user'] = user['ism']
            session['user_tel'] = user['tel']
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="Xato! Ism/Telefon yoki parol noto'g'ri.")
            
    return render_template('login.html')

# TEST SAHIFASI
@app.route('/test/<string:fan_nomi>', methods=['GET', 'POST'])
def test(fan_nomi):
    if 'user' not in session:
        return redirect(url_for('login'))
        
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM testlar WHERE fan = ?', (fan_nomi,))
    savollar = cursor.fetchall()
    db.close()
    
    if request.method == 'GET':
        session['boshlangan_vaqt'] = time.time()
        return render_template('test.html', fan=fan_nomi, savollar=savollar)
        
    if request.method == 'POST':
        boshlangan = session.get('boshlangan_vaqt', time.time())
        yakunlangan = time.time()
        farq_soniya = int(yakunlangan - boshlangan)
        
        if farq_soniya < 60:
            sarflangan_vaqt = f"{farq_soniya} soniya"
        else:
            sarflangan_vaqt = f"{farq_soniya // 60} daqiqa {farq_soniya % 60} soniya"
            
        to_gri_javoblar = 0
        for savol in savollar:
            tanlangan_javob = request.form.get(f"savol_{savol['id']}")
            if tanlangan_javob == savol['javob']:
                to_gri_javoblar += 1
                
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute('''
            INSERT INTO natijalar (ism, tel, fan, to_gri_javoblar, jami_savollar, sarflangan_vaqt)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (session['user'], session.get('user_tel', '-'), fan_nomi, to_gri_javoblar, len(savollar), sarflangan_vaqt))
        db.commit()
        db.close()
        
        return render_template('natija.html', fan=fan_nomi, jami=len(savollar), to_gri=to_gri_javoblar, vaqt=sarflangan_vaqt)

# REYTING
@app.route('/')
@app.route('/index')
def index():
    # Baza yuklanayotganda jadvallar va fanlar borligini avtomat tekshirish
    db = get_db_connection()
    cursor = db.cursor()
    
    # 1. Agar jadvallar o'chib ketgan bo'lsa, ularni qayta yaratish
    cursor.execute('''CREATE TABLE IF NOT EXISTS fanlar (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        nomi TEXT
    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS foydalanuvchilar (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ism TEXT,
        tel TEXT,
        parol TEXT
    )''')

    # 2. Agar fanlar yo'q bo'lsa, ularni avtomat bazaga yozish
    cursor.execute("SELECT COUNT(*) FROM fanlar")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO fanlar (nomi) VALUES ('Matematika')")
        cursor.execute("INSERT INTO fanlar (nomi) VALUES ('Dasturlash (Python)')")
        cursor.execute("INSERT INTO fanlar (nomi) VALUES ('Ingliz tili')")
        db.commit()
    
    # 3. Fanlarni bazadan o'qib olib, bosh sahifaga yuborish
    cursor.execute("SELECT * FROM fanlar")
    fanlar = cursor.fetchall()
    db.close()
    
    # Foydalanuvchi tizimga kirgan bo'lsa bosh sahifani, aks holda loginni ko'rsatish
    if 'user' in session:
        return render_template('index.html', fanlar=fanlar, user=session['user'])
    return redirect(url_for('login'))
# TIZIMDAN CHIQISH
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
