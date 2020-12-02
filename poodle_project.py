from flask import Flask, render_template, request, g, redirect, url_for, session
from datetime import datetime
import bcrypt
import sqlite3

app = Flask(__name__)
app.secret_key = "dhsdsyuewehu98763j2kr23ye98yd"
db_location = 'var/poodle.db'
is_admin_val = 0


def get_db():
    db = getattr(g, 'db', None)
    if db is None:
        db = sqlite3.connect(db_location)
        g.db = db
    return db


@app.teardown_appcontext
def close_db_connection(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


def login_query_db(query, args, one=False):
    cursor = get_db().execute(query, args)
    rv = cursor.fetchall()
    cursor.close()
    return (rv[0] if rv else None) if one else rv


def valid_login(username, password):
    global user

    password = password.encode('utf-8')
    users = login_query_db('SELECT password FROM users WHERE username = ?', [username],
                           one=True)
    if users is None:
        return False
    else:
        for user in users:
            user = user

    if bcrypt.checkpw(password, user):
        return True
    else:
        return False


def query_db(query, args):
    cursor = get_db().execute(query, args)
    rv = cursor.fetchall()
    cursor.close()
    return rv


def return_all(query):
    cursor = get_db().execute(query)
    rv = cursor.fetchall()
    cursor.close()
    return rv


def update_query(username, password, admin_input):
    if admin_input == 'Yes':
        adm_no = '1'
    else:
        adm_no = '0'
    cursor = get_db().execute('INSERT INTO users VALUES (?,?,?)', [username, password, adm_no])
    get_db().commit()
    cursor.close()
    return


def is_admin(username):
    admin_query = login_query_db('SELECT * FROM users WHERE username = ? AND is_admin == 1', [username], one=True)
    if admin_query is None:
        return False
    else:
        session['admin'] = 1
        return True


def valid_user(username):
    user = query_db('SELECT * FROM users WHERE username = ?', [username])
    return user


def upload_image(file, subject):
    user = session['user']
    cursor = get_db().execute('INSERT INTO user_work VALUES (?,?,?)', [subject, user, file])
    get_db().commit()
    cursor.close()
    return


def create_message(message, date):
    user = session['user']
    cursor = get_db().execute('INSERT INTO chat VALUES (?,?,?)', [user, message, date])
    get_db().commit()
    cursor.close()
    return


def create_announce(date, announcement):
    cursor = get_db().execute('INSERT INTO announcements VALUES (?,?)', [date, announcement])
    get_db().commit()
    cursor.close()
    return


def upload_work(subject, description, date):
    cursor = get_db().execute('INSERT INTO work VALUES (?,?,?)', [subject, description, date])
    get_db().commit()
    cursor.close()
    return


@app.route('/')
@app.route('/login', methods=['POST', 'GET'])
def login():
    error = None
    rows = return_all('SELECT * FROM announcements')
    if request.method == 'POST':
        if valid_login(request.form['username'], request.form['password']):
            use = request.form['username']
            session['user'] = use
            if is_admin(request.form['username']):
                return render_template('home.html', rows=rows)
            else:
                return render_template('home.html', rows=rows)
        else:
            error = 'Invalid Username or Password Please Try Again'

    return render_template('login.html', error=error)


@app.route('/home')
def home():
    if 'user' in session:
        rows = return_all('SELECT * FROM announcements')
        return render_template('home.html', rows=rows)
    else:
        return redirect(url_for('login'))


@app.route('/logout', methods=['GET'])
def logout():
    session.pop('user', None)
    session.pop('admin', None)
    return redirect(url_for('login'))


@app.route('/admin')
def admin():
    rows = return_all('SELECT * FROM announcements')
    if 'user' in session:
        if 'admin' in session:
            return render_template('admin.html')
        else:
            return render_template('home.html', error='Not An Admin', rows=rows)
    else:
        return redirect(url_for('login'))


@app.route('/social')
def social():
    if 'user' in session:
        return render_template('social.html')
    else:
        return redirect(url_for('login'))


@app.route('/maths', methods=['POST', 'GET'])
def maths():
    subject = 'math'
    rows = query_db('SELECT * FROM work WHERE subject = ?', [subject])
    if 'user' in session:
        return render_template('subject.html', name='Maths', rows=rows)
    else:
        return redirect(url_for('login'))


@app.route('/english', methods=['POST', 'GET'])
def english():
    subject = 'english'
    rows = query_db('SELECT * FROM work WHERE subject = ?', [subject])
    if 'user' in session:
        return render_template('subject.html', name='English', rows=rows)
    else:
        return redirect(url_for('login'))


@app.route('/science', methods=['POST', 'GET'])
def science():
    subject = 'science'
    rows = query_db('SELECT * FROM work WHERE subject = ?', [subject])
    if 'user' in session:
        return render_template('subject.html', name='Science', rows=rows)
    else:
        return redirect(url_for('login'))


@app.route('/creative', methods=['POST', 'GET'])
def creative():
    subject = 'creative'
    rows = query_db('SELECT * FROM work WHERE subject = ?', [subject])
    if 'user' in session:
        if request.method == ['POST']:
            image = request.files['datafile']
            image.save(image.filename)
            print("file uploaded succesful")
        else:
            return render_template('subject.html', name='Drama, Art and Music', rows=rows)
    else:
        return redirect(url_for('login'))


@app.route('/create-user', methods=['GET', 'POST'])
def create_user():
    title = 'Create Users'
    error = None
    if 'user' in session:
        if request.method == 'POST':
            if valid_user(request.form['username']):
                error = 'user already exists'
            else:
                update_query(request.form['username'],
                             bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt()),
                             request.form['is_admin'])

        return render_template('create_records.html', title=title, error=error)
    else:
        return redirect(url_for('login'))


@app.route('/view-records', methods=['GET', 'POST'])
def view_records():
    title = 'View Records'
    error = None
    rows = []
    radio = request.form.get('checkAll')
    if 'user' in session:
        if request.method == 'POST':
            if request.form['username'] is not None or request.form['username'] == '':
                rows = valid_user(request.form['username'])
                if not rows and radio != 'ALL':
                    error = "no user with that username "
            radio = request.form.get('checkAll')
            if radio == 'ALL':
                rows = return_all('SELECT * FROM users')
        return render_template('view_records.html', title=title, rows=rows, error=error)
    else:
        return redirect(url_for('login'))


@app.route('/create-announcement', methods=['GET', 'POST'])
def create_announcement():
    title = 'Upload Work'
    if 'user' in session:
        if request.method == 'POST':
            create_announce(request.form['an_date'], request.form['announce'])
            return render_template('new_work.html', title=title)
        else:
            return render_template('new_work.html', title=title)
    else:
        return redirect(url_for('login'))


@app.route('/create-work', methods=['GET', 'POST'])
def create_work():
    title = 'Upload Work'
    if 'user' in session:
        if request.method == 'POST':
            upload_work(request.form['subject'], request.form['desc'], request.form['date'])
            return render_template('new_work.html', title=title)
        else:
            return render_template('new_work.html', title=title)
    else:
        return redirect(url_for('login'))


@app.route('/view-work')
def view_work():
    title = 'View Work'
    if 'user' in session:
        return render_template('base.html', title=title)
    else:
        return redirect(url_for('login'))


@app.route('/chatroom', methods=['POST', 'GET'])
def chat():
    title = 'Chat Room'
    date_time = datetime.now()
    date_time = date_time.strftime('%d/%m/%Y')
    if 'user' in session:
        if request.method == 'POST':
            create_message(request.form['message'], date_time)
            rows = return_all('SELECT * FROM chat')
        else:
            rows = return_all('SELECT * FROM chat')
        return render_template('chatroom.html', title=title, rows=rows, )
    else:
        return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
