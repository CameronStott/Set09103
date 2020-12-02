from flask import Flask, render_template, request

app = Flask(__name__)


@app.route('/users/')
def users():
    names = ['simon', 'thomas', 'lee', 'jamie', 'sylvester']
    return render_template('login.html', names=names)


@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/home')
def home():
    return render_template('base.html')


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
