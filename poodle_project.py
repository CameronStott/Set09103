from flask import Flask, render_template, request, g, redirect, url_for
import sqlite3

app = Flask(__name__)
db_location = 'var/poodle.db'
loginSuccess = 0


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


def query_db(query, args, one=False):
    cursor = get_db().execute(query, args)
    rv = cursor.fetchall()
    cursor.close()
    return (rv[0] if rv else None) if one else rv


def valid_login(username, password):
    user = query_db('SELECT * FROM users WHERE username = ? AND password = ?', [username, password], one=True)
    if user is None:
        return False
    else:

        return True


def is_admin(username, password):
    admin = query_db('SELECT * FROM users WHERE username = ? AND password = ?', [username, password], one=True)
    if admin == 1:
        return True
    else:
        return False


@app.route('/')
@app.route('/login', methods=['POST', 'GET'])
def login():
    error = None
    if request.method == 'POST':
        if valid_login(request.form['username'], request.form['password']):
            global loginSuccess
            loginSuccess = 1
            if is_admin(request.form['username'], request.form['password']):
                return render_template('home.html', value=True)

            else:
                return render_template('home.html')

        else:
            error = 'invalid username or password'

    return render_template('login.html', error=error)


@app.route('/home', methods=['POST', 'GET'])
def home():
    if loginSuccess == 0:
        return redirect(url_for('login'))
    else:
        return render_template('home.html')


@app.route('/logout', methods=['GET'])
def logout():
    global loginSuccess
    loginSuccess = 0
    return redirect(url_for('login'))


@app.route('/admin')
def admin():
    if loginSuccess == 0:
        return redirect(url_for('login'))
    else:
        return render_template('admin.html')


@app.route('/social')
def social():
    if loginSuccess == 0:
        return redirect(url_for('login'))
    else:
        return render_template('social.html')


@app.route('/maths')
def maths():
    if loginSuccess == 0:
        return redirect(url_for('login'))
    else:
        return render_template('subject.html')


@app.route('/english')
def english():
    if loginSuccess == 0:
        return redirect(url_for('login'))
    else:
        return render_template('subject.html')


@app.route('/science')
def science():
    if loginSuccess == 0:
        return redirect(url_for('login'))
    else:
        return render_template('subject.html')


@app.route('/creative')
def creative():
    if loginSuccess == 0:
        return redirect(url_for('login'))
    else:
        return render_template('subject.html')


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
