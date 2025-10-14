from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "Servidor Flask funcionando correctamente 🚀"

@app.route('/api/users')
def get_users():
    return {"users": ["user1", "user2", "user3"]}

if __name__ == '__main__':
    app.run(debug=True)
