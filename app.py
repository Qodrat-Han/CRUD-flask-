from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
import mysql.connector



app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Konfigurasi database MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'hewan'



# Inisialisasi MySQL dan Bcrypt
mysql = MySQL(app)
bcrypt = Bcrypt(app)

# Halaman login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:  # Cek apakah pengguna sudah login
        return redirect(url_for('dashboard'))  # Arahkan ke halaman dashboard

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Query untuk mendapatkan data pengguna berdasarkan username
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()

        # Jika pengguna ditemukan dan password hash cocok
        if user and bcrypt.check_password_hash(user[3], password):
            session['user_id'] = user[0]  # Set session user_id
            flash('Login berhasil!', 'success')
            return redirect(url_for('dashboard'))  # Redirect ke halaman dashboard setelah login
        else:
            flash('Username atau password salah.', 'danger')

    return render_template('login.html')

# Route untuk register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Ambil data dari form
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        # Hash password
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Query untuk mengecek apakah email atau username sudah terdaftar
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s OR email = %s", (username, email))
        user = cursor.fetchone()
        
        if user:
            flash('Username atau Email sudah terdaftar!', 'danger')
            return render_template('register.html')

        # Jika tidak ada yang terdaftar, masukkan data ke database
        cursor.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", 
                       (username, email, hashed_password))
        mysql.connection.commit()
        cursor.close()
        
        flash('Registrasi berhasil! Silakan login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

#Dashboard
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:  # Jika pengguna belum login
        flash('Silakan login terlebih dahulu.', 'warning')
        return redirect(url_for('login'))  # Arahkan ke halaman login jika belum login

    # Ambil data pengguna berdasarkan session['user_id']
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM users WHERE id = %s", (session['user_id'],))
    user = cursor.fetchone()
    cursor.close()

    # Tampilkan halaman dashboard dengan data pengguna
    return render_template('dashboard.html', user=user)

# Route untuk halaman utama
@app.route('/')
def home():
    if 'user_id' in session:  # Jika sudah login
        return redirect(url_for('dashboard'))  # Arahkan ke halaman dashboard
    else:
        return redirect(url_for('login'))  # Jika belum login, arahkan ke halaman login

# Route utama - Menampilkan daftar kucing
@app.route('/kucing')
def kucing():
    if 'user_id' not in session:  # Periksa apakah pengguna sudah login
        flash('Silakan login terlebih dahulu.', 'warning')
        return redirect(url_for('login'))  # Arahkan ke halaman login jika belum login

    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT id, ras, jenis_kelamin, umur, harga, created_at FROM kucing WHERE 1")
        kucing_list = cursor.fetchall()
        kucing_dict_list = [
            {desc[0]: value for desc, value in zip(cursor.description, row)}
            for row in kucing_list
        ]
        cursor.close()
        return render_template('kucing.html', kucing_list=kucing_dict_list)
    except Exception as e:
        flash(f"Terjadi kesalahan: {e}", 'danger')
        return redirect(url_for('home'))


# Route untuk menambahkan kucing (Create)
@app.route('/tambah_kucing', methods=['GET', 'POST'])
def tambah_kucing():
    if request.method == 'POST':
        ras = request.form.get('ras')
        jenis_kelamin = request.form.get('jenis_kelamin')
        umur = request.form.get('umur')
        harga = request.form.get('harga')

        if ras and jenis_kelamin and umur and harga:
            try:
                harga = float(harga)
                cursor = mysql.connection.cursor()
                cursor.execute(
                    "INSERT INTO kucing (ras, jenis_kelamin, umur, harga) VALUES (%s, %s, %s, %s)",
                    (ras, jenis_kelamin, umur, harga)
                )
                mysql.connection.commit()
                cursor.close()
                flash('Kucing berhasil ditambahkan!', 'success')
                return redirect(url_for('kucing'))
            except Exception as err:
                flash(f"Terjadi kesalahan: {err}", 'danger')
        else:
            flash('Semua kolom harus diisi!', 'warning')

    return render_template('tambah_kucing.html')

# Route untuk mengedit kucing (Update)
@app.route('/edit_kucing/<int:id>', methods=['GET', 'POST'])
def edit_kucing(id):
    cursor = mysql.connection.cursor()

    # Ambil data kucing berdasarkan ID
    cursor.execute("SELECT id, ras, jenis_kelamin, umur, harga, created_at FROM kucing WHERE id = %s", (id,))
    kucing = cursor.fetchone()

    if not kucing:
        flash('Kucing tidak ditemukan!', 'danger')
        return redirect(url_for('kucing'))

    if request.method == 'POST':
        ras = request.form.get('ras')
        jenis_kelamin = request.form.get('jenis_kelamin')
        umur = request.form.get('umur')
        harga = request.form.get('harga')

        if ras and jenis_kelamin and umur and harga:
            try:
                harga = float(harga)
                cursor.execute(
                    """UPDATE kucing SET ras = %s, jenis_kelamin = %s, umur = %s, harga = %s
                    WHERE id = %s""",
                    (ras, jenis_kelamin, umur, harga, id)
                )
                mysql.connection.commit()
                flash('Kucing berhasil diperbarui!', 'success')
                return redirect(url_for('kucing'))
            except Exception as err:
                flash(f"Terjadi kesalahan: {err}", 'danger')
        else:
            flash('Semua kolom harus diisi!', 'warning')

    cursor.close()
    return render_template('edit_kucing.html', kucing=kucing)


# Route untuk menghapus kucing (Delete)
@app.route('/hapus_kucing/<int:id>', methods=['GET', 'POST'])
def hapus_kucing(id):
    try:
        cursor = mysql.connection.cursor()
        # Query untuk menghapus kucing berdasarkan ID
        cursor.execute("DELETE FROM kucing WHERE id = %s", (id,))
        mysql.connection.commit()
        cursor.close()
        flash('Kucing berhasil dihapus!', 'success')
    except Exception as e:
        flash(f"Terjadi kesalahan saat menghapus kucing: {e}", 'danger')
    return redirect(url_for('kucing'))


# Logout
@app.route('/logout', methods=['GET', 'POST'])
def logout():
    # Menghapus 'user_id' dari session
    session.pop('user_id', None)
    
    # Menampilkan pesan flash bahwa logout berhasil
    flash('Anda berhasil logout!', 'info')
    
    # Mengarahkan pengguna kembali ke halaman login
    return redirect(url_for('login'))

@app.route('/seed', methods=['GET'])
def seed_data():
    password_plain = "password123"
    hashed_password = bcrypt.generate_password_hash(password_plain).decode('utf-8')

    cursor = mysql.connection.cursor()
    cursor.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", 
                   ("user1", "user1@example.com", hashed_password))
    mysql.connection.commit()
    cursor.close()
    return "Data berhasil ditambahkan!"

if __name__ == '__main__':
    app.run(debug=True)
