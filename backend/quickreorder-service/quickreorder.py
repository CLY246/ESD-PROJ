from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flasgger import Swagger

app = Flask(__name__)
CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+mysqlconnector://root:root@host.docker.internal:8889/quickreorder"
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

db = SQLAlchemy(app)

# Initialize Flasgger with OpenAPI specifications
app.config['SWAGGER'] = {
    'title': 'Quick Reorder Microservice API',
    'version': 1.0,
    "openapi": "3.0.2",
    'description': 'API to retrieve vendors and menu items',
}

swagger = Swagger(app)

class QuickReorder(db.Model):
    __tablename__ = 'QuickReorders'
    QuickReorderID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    UserID = db.Column(db.Integer, nullable=False)
    OrderID = db.Column(db.Integer, nullable=False)
    ReorderName = db.Column(db.String(255), nullable=True)

    def json(self):
        return {
            "QuickReorderID": self.QuickReorderID,
            "UserID": self.UserID,
            "OrderID": self.OrderID,
            "ReorderName": self.ReorderName
        }

@app.route('/api/health')
def health_check():
    """
    Health check endpoint
    ---
    responses:
      200:
        description: API is running
    """
    return jsonify({"message": "Quick Reorder API is running!"})

@app.route("/quickreorders", methods=["POST"])
def create_quick_reorder():
    """
    Create a Quick Reorder
    ---
    tags:
      - Quick Reorders
    summary: Create a new quick reorder entry
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required:
              - UserID
              - OrderID
            properties:
              OrderID:
                type: integer
                example: 1001
              QuickReorderID:
                type: integer
                example: 2
              ReorderName:
                type: string
                example: "Lunch Favorite"
              UserID:
                type: integer
                example: 1
    responses:
      201:
        description: Quick reorder created successfully
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
                  example: Quick reorder created successfully
                quick_reorder:
                  type: object
                  properties:
                    QuickReorderID:
                      type: integer
                      example: 1
                    UserID:
                      type: integer
                      example: 1
                    OrderID:
                      type: integer
                      example: 1001
                    ReorderName:
                      type: string
                      example: "Lunch Favorite"
      400:
        description: Missing UserID or OrderID
    """
    data = request.json
    user_id = data.get("UserID")
    order_id = data.get("OrderID")
    reorder_name = data.get("ReorderName")

    if not user_id or not order_id:
        return jsonify({"message": "UserID and OrderID are required"}), 400

    new_reorder = QuickReorder(
        UserID=user_id,
        OrderID=order_id,
        ReorderName=reorder_name
    )

    db.session.add(new_reorder)
    db.session.commit()

    return jsonify({"message": "Quick reorder created successfully", "quick_reorder": new_reorder.json()}), 201

@app.route("/quickreorders/user/<int:user_id>", methods=["GET"])
def get_quick_reorders_by_user(user_id):
    """
    Get Quick Reorders by User
    ---
    tags:
      - Quick Reorders
    summary: Retrieve all quick reorders for a specific user
    parameters:
      - name: user_id
        in: path
        required: true
        schema:
          type: integer
        description: ID of the user to retrieve quick reorders for
    responses:
      200:
        description: A list of quick reorders for the user
        content:
          application/json:
            schema:
              type: array
              items:
                type: object
                properties:
                  QuickReorderID:
                    type: integer
                    example: 1
                  UserID:
                    type: integer
                    example: 1
                  OrderID:
                    type: integer
                    example: 1001
                  ReorderName:
                    type: string
                    example: "Lunch Favorite"
    """
    quick_reorders = QuickReorder.query.filter_by(UserID=user_id).all()
    return jsonify([qr.json() for qr in quick_reorders])

@app.route("/quickreorders/<int:quick_reorder_id>", methods=["DELETE"])
def delete_quick_reorder(quick_reorder_id):
    """
    Delete Quick Reorder
    ---
    tags:
      - Quick Reorders
    summary: Delete a specific quick reorder by its ID
    parameters:
      - name: quick_reorder_id
        in: path
        required: true
        schema:
          type: integer
        description: ID of the quick reorder to delete
    responses:
      200:
        description: Quick reorder deleted successfully
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
                  example: Quick reorder deleted successfully
      404:
        description: Quick reorder not found
    """
    quick_reorder = QuickReorder.query.get(quick_reorder_id)
    if not quick_reorder:
        return jsonify({"message": "Quick reorder not found"}), 404

    db.session.delete(quick_reorder)
    db.session.commit()
    return jsonify({"message": "Quick reorder deleted successfully"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
