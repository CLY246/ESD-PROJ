from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token, jwt_required, JWTManager
import os

app = Flask(__name__)

CORS(app)  

app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+mysqlconnector://root:root@host.docker.internal:3306/user"
app.config["JWT_SECRET_KEY"] = "16d1f8e74e00fe360268751f53f5ee618df825719740cd4dee0d9b98937ceaeb"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)


with app.app_context():
    db.create_all()


@app.route('/api/health')
def health_check():
    return jsonify({"message": "API is running!"})

@app.route('/api/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([{"id": u.id, "name": u.name, "email": u.email} for u in users])

@app.route("/signup", methods=["POST"])
def signup():
    data = request.json
    name = data.get('name') 
    email = data.get('email')
    password = data.get('password')

    if not name or not email or not password:
        return jsonify({"message": "Name, Email, and Password are required"}), 400

    hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
    new_user = User(name=name, email=email, password=hashed_password)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User created successfully"}), 201

@app.route("/login", methods=["POST"])
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email).first()
    if not user or not bcrypt.check_password_hash(user.password, password):
        return jsonify({"message": "Invalid email or password"}), 401

    access_token = create_access_token(identity={"email": user.email})
    return jsonify({
        "message": "Login successful",
        "token": access_token,
        "user": {"id": user.id, "name": user.name, "email": user.email}
    })



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)



