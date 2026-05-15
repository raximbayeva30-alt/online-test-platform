from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import time
import os

app = Flask(__name__)
app.secret_key = 'kod_123'

def get_db_connection():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, 'imtihon_bazasi.db')
    return sqlite3.connect(db_path)

@app.route('/')
def index():
    if 'user' not in session:
        return redirect(url_for('login'))
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("SELECT DISTINCT fan FROM testlar")
    fanlar = cursor.fetchall()
    db.close()
    return render_template('index.html', user=session['user'], fanlar=fanlar)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        ism = request.form.get('ism')
        parol = request.form.get('parol')
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM foydalanuvchilar WHERE ism=? AND parol=?", (ism, parol))
        user = cursor.fetchone()
        db.close()
        if user:
            session['user'] = ism
            return redirect(url_for('index'))
        return "Xato! Ism yoki parol noto'g'ri. <a href='/login'>Orqaga</a>"
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        ism = request.form.get('ism')
        parol = request.form.get('parol')
        db = get_db_connection()
        cursor = db.cursor()
        try:
            cursor.execute("INSERT INTO foydalanuvchilar (ism, parol) VALUES (?, ?)", (ism, parol))
            db.commit()
            session['user'] = ism
            return redirect(url_for('index'))
        except:
            return "Xato! Bu ism band. <a href='/register'>Orqaga</a>"
        finally:
            db.close()
    return render_template('register.html')

@app.route('/test', methods=['GET', 'POST'])
def test():
    if 'user' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        if 'yakunlash' in request.form:
            farq = int(time.time() - session.get('start_time', time.time()))
            vaqt_matni = f"{farq // 60} min {farq % 60} sek"
            fan = request.form.get('fan')
            db = get_db_connection()
            cursor = db.cursor()
            cursor.execute("SELECT * FROM testlar WHERE fan=?", (fan,))
            savollar = cursor.fetchall()
            ball = 0
            for s in savollar:
                javob = request.form.get(f'q{s[0]}')
                if javob == s[5]: ball += 1
            cursor.execute("INSERT INTO natijalar (ism, fan, ball, vaqt) VALUES (?, ?, ?, ?)", (session['user'], fan, ball, vaqt_matni))
            db.commit()
            db.close()
            return render_template('natija.html', ball=ball, jami=len(savollar), vaqt=vaqt_matni)
        
        fan = request.form.get('fan')
        session['start_time'] = time.time()
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM testlar WHERE fan=?", (fan,))
        savollar = cursor.fetchall()
        db.close()
        return render_template('test.html', savollar=savollar, fan=fan, user=session['user'])

@app.route('/rating')
def rating():
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("SELECT ism, fan, ball, vaqt FROM natijalar ORDER BY ball DESC")
    natijalar = cursor.fetchall()
    db.close()
    return render_template('rating.html', natijalar=natijalar)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run()
