from flask import Flask, render_template, url_for, request, g, redirect, flash, make_response, session
import os

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['SQLALCHEMY_DATABASE_URI']
app.config['SECRET_KEY'] = os.environ['SECRET_KEY_FLASK']



@app.route('/')
@app.route('/home')
def home():
    content = render_template('index.html')
    res = make_response(content)
    return res


if __name__ == '__main__':
    app.app_context().push()
    # db.create_all()
    app.run(debug=True)
    # app.run()
