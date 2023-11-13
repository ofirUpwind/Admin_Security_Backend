from website import create_app
from dotenv import load_dotenv
from flask_cors import CORS
from flask_migrate import Migrate
from website import db

load_dotenv()

app = create_app()
CORS(app, origins=["http://localhost:3000"], supports_credentials=True)
migrate = Migrate(app, db)


if __name__ == '__main__':
    app.run(debug=True)
