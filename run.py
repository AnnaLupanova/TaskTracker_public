import os
from app import create_app, db
from flask import g


app = create_app()
with app.app_context():
    db.create_all()


@app.teardown_appcontext
def close_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


app.run(host='localhost', port=5001, debug=False)