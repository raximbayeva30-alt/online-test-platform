import sqlite3

def baza_yaratish():
    db = sqlite3.connect('imtihon_bazasi.db')
    cursor = db.cursor()
    
    # Eskilarini o'chirish
    cursor.execute("DROP TABLE IF EXISTS foydalanuvchilar")
    cursor.execute("DROP TABLE IF EXISTS testlar")
    cursor.execute("DROP TABLE IF EXISTS natijalar")
    
    # Foydalanuvchilar (Login va Parol bilan)
    cursor.execute("""
        CREATE TABLE foydalanuvchilar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ism TEXT,
            parol TEXT
        )
    """)
    
    # Testlar
    cursor.execute("""
        CREATE TABLE testlar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fan TEXT,
            savol TEXT,
            a TEXT,
            b TEXT,
            togri_javob TEXT
        )
    """)
    
    # Natijalar (Reyting uchun)
    cursor.execute("""
        CREATE TABLE natijalar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ism TEXT,
            fan TEXT,
            ball INTEGER,
            vaqt TEXT,
            sana TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Admin va talaba qo'shish
    cursor.execute("INSERT INTO foydalanuvchilar (ism, parol) VALUES (?, ?)", ('admin', '12345'))
    cursor.execute("INSERT INTO foydalanuvchilar (ism, parol) VALUES (?, ?)", ('talaba', '1111'))
    
    # Savollarni qo'shish
    savollar = [
        # Matematika
        (1, 'Matematika', '15 * 3?', '45', '55', 'A'),
        (2, 'Matematika', '100 / 4?', '25', '20', 'A'),
        (3, 'Matematika', 'Eng kichik tub son qaysi?', '1', '2', 'B'),
        (4, 'Matematika', '12 ning kvadrati nechaga teng?', '144', '124', 'A'),
        (5, 'Matematika', 'Ildiz ostida 81 dan necha chiqadi?', '7', '9', 'B'),

        # Ingliz tili
        (6, 'Ingliz tili', '"Apple" so\'zining tarjimasi?', 'Olma', 'Anor', 'A'),
        (7, 'Ingliz tili', '"Book" so\'zining tarjimasi?', 'Kitob', 'Daftar', 'A'),
        (8, 'Ingliz tili', 'Salomlashish uchun qaysi so\'z ishlatiladi?', 'Hello', 'Goodbye', 'A'),
        (9, 'Ingliz tili', '"Water" nima degani?', 'Suv', 'Havo', 'A'),
        (10, 'Ingliz tili', '"School" so\'zining ma\'nosi?', 'Maktab', 'Boza', 'A'),

        # Dasturlash
        (11, 'Dasturlash', 'Python qanday til?', 'Dasturlash tili', 'Oyin', 'A'),
        (12, 'Dasturlash', 'HTML nima?', 'Belgilash tili', 'Dasturlash tili', 'A'),
        (13, 'Dasturlash', 'O\'zgaruvchi nomi raqam bilan boshlanishi mumkinmi?', 'Yo\'q', 'Ha', 'A'),
        (14, 'Dasturlash', 'Print() vazifasi nima?', 'Ma\'lumotni chiqarish', 'Ma\'lumotni o\'chirish', 'A'),
        (15, 'Dasturlash', 'Dasturdagi xatolik nima deyiladi?', 'Bug', 'Feature', 'A')
    ]
    
    cursor.executemany("INSERT INTO testlar VALUES (?,?,?,?,?,?)", savollar)
    
    db.commit()
    db.close()
    print("Baza muvaffaqiyatli yangilandi! Admin: admin, Parol: 12345")

if __name__ == '__main__':
    baza_yaratish()