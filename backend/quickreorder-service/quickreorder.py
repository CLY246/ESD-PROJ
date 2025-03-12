from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+mysqlconnector://root:root@host.docker.internal:8889/quickreorder"
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

db = SQLAlchemy(app)

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
    return jsonify({"message": "Quick Reorder API is running!"})

@app.route("/quickreorders", methods=["POST"])
def create_quick_reorder():
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
    quick_reorders = QuickReorder.query.filter_by(UserID=user_id).all()
    return jsonify([qr.json() for qr in quick_reorders])

@app.route("/quickreorders/<int:quick_reorder_id>", methods=["DELETE"])
def delete_quick_reorder(quick_reorder_id):
    quick_reorder = QuickReorder.query.get(quick_reorder_id)
    if not quick_reorder:
        return jsonify({"message": "Quick reorder not found"}), 404

    db.session.delete(quick_reorder)
    db.session.commit()
    return jsonify({"message": "Quick reorder deleted successfully"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
