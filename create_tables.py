from dotenv import load_dotenv
load_dotenv()

from app import create_app, db
from app.database.models import User

app = create_app()

with app.app_context():
    db.create_all()
    print("Tables created successfully!")
