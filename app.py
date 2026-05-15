import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session

def get_db_connection():
    conn = sqlite3.connect('imtihon_bazasi.db')
    conn.row_factory = sqlite3.Row
    
    cursor = conn.cursor()
    
    # 1. Foydalanuvchilar jadvali (Ism, Tel va Parol bilan)
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
    
    # 3. Agar bazada savollar bo'lmasa, fanlarni avtomat qo'shish
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

@app.route('/')
def index():
    if 'user' in session:
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute('SELECT DISTINCT fan FROM testlar')
        fanlar = cursor.fetchall()
        db.close()
        return render_template('index.html', fanlar=fanlar, user=session['user'])
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        ism = request.form.get('ism')
        tel = request.form.get('tel')
        parol = request.form.get('parol')
        
        db = get_db_connection()
        cursor = db.cursor()
        try:
            cursor.execute("INSERT INTO foydalanuvchilar (ism, tel, parol) VALUES (?, ?, ?)", (ism, tel, parol))
            db.commit()
            db.close()
            session['user'] = ism
            return redirect(url_for('index'))
        except sqlite3.IntegrityError:
            db.close()
            return render_template('register.html', error="Xato! Bu ism band.")
            
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        ism_yoki_tel = request.form.get('ism')
        parol = request.form.get('parol')
        
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute('''
            SELECT * FROM foydalanuvchilar 
            WHERE (ism = ? OR tel = ?) AND parol = ?
        ''', (ism_yoki_tel, ism_yoki_tel, parol))
        user = cursor.fetchone()
        db.close()
        
        if user:
            session['user'] = user['ism']
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="Xato! Ism/Telefon yoki parol noto'g'ri.")
            
    return render_template('login.html')

@app.route('/test/<string:fan_nomi>', methods=['GET', 'POST'])
def test(fan_nomi):
    if 'user' not in session:
        return redirect(url_for('login'))
        
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM testlar WHERE fan = ?', (fan_nomi,))
    savollar = cursor.fetchall()
    db.close()
    
    if request.method == 'POST':
        to_gri_javoblar = 0
        for savol in savollar:
            tanlangan_javob = request.form.get(f"savol_{savol['id']}")
            if tanlangan_javob == savol['javob']:
                to_gri_javoblar += 1
        return render_template('natija.html', fan=fan_nomi, jami=len(savollar), to_gri=to_gri_javoblar)
        
    return render_template('test.html', fan=fan_nomi, savollar=savollar)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
