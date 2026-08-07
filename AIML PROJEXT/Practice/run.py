# run.py
from src import create_app,db
import os

app = create_app(os.environ.get('FLASK_ENV', 'development'))
with app.app_context():
    db.create_all()
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, port=port)
