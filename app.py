from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import time

app = Flask(__name__)
app.secret_key = 'maxfiy_kalit_999'

@app.route('/')
def index():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    db = sqlite3.connect('imtihon_bazasi.db')
    cursor = db.cursor()
    cursor.execute("SELECT DISTINCT fan FROM testlar")
    fanlar = [{'fan': f[0]} for f in cursor.fetchall()]
    db.close()
    return render_template('index.html', user=session['user'], fanlar=fanlar)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        ism = request.form.get('ism')
        parol = request.form.get('parol')
        
        db = sqlite3.connect('imtihon_bazasi.db')
        cursor = db.cursor()
        cursor.execute("SELECT * FROM foydalanuvchilar WHERE ism=? AND parol=?", (ism, parol))
        user = cursor.fetchone()
        db.close()

        if user:
            session['user'] = ism
            return redirect(url_for('index'))
        else:
            return "Xato! Ism yoki parol noto'g'ri. <a href='/login'>Orqaga</a>"
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        ism = request.form.get('ism')
        parol = request.form.get('parol')
        
        db = sqlite3.connect('imtihon_bazasi.db')
        cursor = db.cursor()
        
        # Check if user already exists
        cursor.execute("SELECT * FROM foydalanuvchilar WHERE ism=?", (ism,))
        if cursor.fetchone():
            db.close()
            return "Xato! Bu ism band. <a href='/register'>Orqaga</a>"
            
        cursor.execute("INSERT INTO foydalanuvchilar (ism, parol) VALUES (?, ?)", (ism, parol))
        db.commit()
        db.close()

        session['user'] = ism
        return redirect(url_for('index'))
        
    return render_template('register.html')

@app.route('/test', methods=['GET', 'POST'])
def test():
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        if 'yakunlash' in request.form:
            # Vaqtni hisoblash
            tugash_vaqti = time.time()
            boshlash_vaqti = session.get('start_time', tugash_vaqti)
            farq = int(tugash_vaqti - boshlash_vaqti)
            vaqt_matni = f"{farq // 60} min {farq % 60} sek"

            # Ballni hisoblash
            fan = request.form.get('fan')
            db = sqlite3.connect('imtihon_bazasi.db')
            cursor = db.cursor()
            cursor.execute("SELECT * FROM testlar WHERE fan=?", (fan,))
            savollar = cursor.fetchall()
            
            ball = 0
            for s in savollar:
                javob = request.form.get(f'q{s[0]}')
                if javob == s[5]: ball += 1
            
            # Natijani bazaga saqlash
            cursor.execute("INSERT INTO natijalar (ism, fan, ball, vaqt) VALUES (?, ?, ?, ?)",
                           (session['user'], fan, ball, vaqt_matni))
            db.commit()
            db.close()
            
            return render_template('natija.html', ball=ball, jami=len(savollar), vaqt=vaqt_matni)

        # Testni boshlash
        fan = request.form.get('fan')
        session['start_time'] = time.time()
        db = sqlite3.connect('imtihon_bazasi.db')
        cursor = db.cursor()
        cursor.execute("SELECT * FROM testlar WHERE fan=?", (fan,))
        savollar = [{'id': s[0], 'savol': s[2], 'a': s[3], 'b': s[4]} for s in cursor.fetchall()]
        db.close()
        return render_template('test.html', savollar=savollar, fan=fan, user=session['user'])

@app.route('/rating')
def rating():
    db = sqlite3.connect('imtihon_bazasi.db')
    cursor = db.cursor()
    cursor.execute("SELECT ism, fan, ball, vaqt FROM natijalar ORDER BY ball DESC")
    top_natijalar = cursor.fetchall()
    db.close()
    return render_template('rating.html', natijalar=top_natijalar)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)