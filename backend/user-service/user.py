from flask_cors import CORS
from flask import Flask, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, JWTManager
from supabase_auth import sign_up_user, sign_in_user, get_user_info
from supabase_auth import supabase_client
from flask_sqlalchemy import SQLAlchemy
from flasgger import Swagger;

app = Flask(__name__)
app.config["DEBUG"] = True
CORS(app)  

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres.zfuesqdkqrlbnmsfichi:postgres@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize Flasgger with OpenAPI specifications
app.config['SWAGGER'] = {
    'title': 'User Microservice API',
    'version': 1.0,
    "openapi": "3.0.2",
    'description': 'API to create and retrieve users',
}

swagger = Swagger(app)
db = SQLAlchemy()

with app.app_context():
    db.init_app(app)
    db.create_all()

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.String, primary_key=True) 
    username = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    name = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    def json(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "name": self.name,
            "created_at": self.created_at
        }


app.config["JWT_SECRET_KEY"] = "48tpzfa+Uu1RH3Sy4wR4UjdK+MNjTuYqN6gaMSnX5/KpLoQ9/ijwrcaJ37b9yMO2e+4j0LW850H1xGJAic0MHQ=="
jwt = JWTManager(app)

@app.route('/api/health')
def health_check():
    """
    Health check endpoint
    ---
    responses:
      200:
        description: API is running
    """
    return jsonify({"message": "API is running!"})

@app.route('/api/users', methods=['GET'])
def get_users():
    
    """
    Fetch all users
    ---
    responses:
      200:
        description: List of users
        content:
          application/json:
            example:
              - id: "123"
                name: "John Doe"
                email: "john@example.com"
    """
    users = User.query.all()
    return jsonify([{"id": u.id, "name": u.name, "email": u.email} for u in users])

@app.route("/register", methods=["POST"])
def register():
    """
    Registers a user with Supabase Auth and stores metadata including username.
    ---
    tags:
      - Authentication
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              username:
                type: string
                example: johndoe
              email:
                type: string
                example: johndoe@example.com
              password:
                type: string
                example: secret123
              name:
                type: string
                example: John Doe
    responses:
      201:
        description: User registered successfully
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
                  example: User registered successfully
      400:
        description: Missing fields or Supabase error
        content:
          application/json:
            schema:
              type: object
              properties:
                error:
                  type: string
                  example: Missing required fields
      500:
        description: Server error
        content:
          application/json:
            schema:
              type: object
              properties:
                error:
                  type: string
                  example: Internal server error
    """
    try:
        data = request.get_json()
        username = data.get("username")
        email = data.get("email")
        password = data.get("password")
        name = data.get("name")

        if not username or not email or not password:
            return jsonify({"error": "Missing required fields"}), 400

        response = sign_up_user(email, password)

        if "error" in response:
            return jsonify(response), 400

        user_id = response["user_id"]

        supabase_client.table("users").insert({
            "id": user_id,
            "username": username,
            "email": email,
            "name": name
        }).execute()

        return jsonify({"message": "User registered successfully"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/login", methods=["POST"])
def login():
    
    """
    Logs in a user using email or username.
    ---
    tags:
      - Authentication
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              identifier:
                type: string
                example: johndoe@example.com
              password:
                type: string
                example: secret123
    responses:
      200:
        description: Login successful
        content:
          application/json:
            schema:
              type: object
              properties:
                access_token:
                  type: string
                  example: jwt-token
                userid:
                  type: string
                  example: user-id
      400:
        description: Missing required fields
        content:
          application/json:
            schema:
              type: object
              properties:
                error:
                  type: string
                  example: Missing required fields
      401:
        description: Invalid credentials
        content:
          application/json:
            schema:
              type: object
              properties:
                error:
                  type: string
                  example: Invalid login credentials
      404:
        description: User not found
        content:
          application/json:
            schema:
              type: object
              properties:
                error:
                  type: string
                  example: User not found
      500:
        description: Server error
        content:
          application/json:
            schema:
              type: object
              properties:
                error:
                  type: string
                  example: Internal server error
    """
    try:
        data = request.get_json()
        identifier = data.get("identifier")  # Can be email OR username
        password = data.get("password")

        if not identifier or not password:
            return jsonify({"error": "Missing required fields"}), 400

        user_query = supabase_client.table("users").select("email").eq("username", identifier).execute()
        if not user_query.data or len(user_query.data) == 0:
            user_query = supabase_client.table("users").select("email").eq("email", identifier).execute()

        if not user_query.data or len(user_query.data) == 0:
            return jsonify({"error": "User not found"}), 404

        email = user_query.data[0]["email"]

        response = sign_in_user(email, password)

        if "error" in response:
            return jsonify(response), 401

        access_token = create_access_token(identity=response["user_id"])
        return jsonify({"access_token": access_token, "userid": response["user_id"]})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/me", methods=["GET"])
@jwt_required()
def user_info():
    """
    Get Current Logged-In User Info
    ---
    security:
      - bearerAuth: []
    responses:
      200:
        description: User info retrieved successfully
        content:
          application/json:
            example:
              id: "user-id"
              email: "user@example.com"
              role: "authenticated"
              aud: "authenticated"
    """
    access_token = request.headers.get("Authorization").split(" ")[1]
    user_data = get_user_info(access_token)
    return jsonify(user_data)

@app.route("/username/<user_id>", methods=["GET"])
def get_user(user_id):
    """
    Get Username by User ID
    ---
    parameters:
      - name: user_id
        in: path
        required: true
        schema:
          type: string
    responses:
      200:
        description: Username found
        content:
          application/json:
            example:
              UserID: "abc123"
              Username: "johndoe"
      404:
        description: User not found
    """
    user = User.query.filter_by(id=user_id).first()
    
    if user:
        return jsonify({"UserID": user.id, "Username": user.username})
    else:
        return jsonify({"error": "User not found"}), 404
    
@app.route("/email/<user_id>", methods=["GET"])
def get_useremail(user_id):
    """
    Get Email by User ID
    ---
    parameters:
      - name: user_id
        in: path
        required: true
        schema:
          type: string
    responses:
      200:
        description: Email found
        content:
          application/json:
            example:
              UserID: "abc123"
              Email: "johndoe@example.com"
      404:
        description: User not found
      500:
        description: Internal Error
    """
    user = User.query.filter_by(id=user_id).first()
    
    if user:
        return jsonify({"UserID": user.id, "Email": user.email})
    else:
        return jsonify({"error": "User not found"}), 404
    

