from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)

CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+mysqlconnector://root:root@host.docker.internal:3306/queuemanagement"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

db = SQLAlchemy(app)

class OrderQueue(db.Model):
    __tablename__ = 'OrderQueue'

    QueueID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    OrderID = db.Column(db.Integer, nullable=False)
    Timestamp = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())
    EstimatedWaitTime = db.Column(db.Integer, nullable=False)  # in minutes
    Status = db.Column(db.Enum('Pending', 'In Progress', 'Completed', name='order_status'), default='Pending')

    def json(self):
        return {
            "QueueID": self.QueueID,
            "OrderID": self.OrderID,
            "Timestamp": self.Timestamp,
            "EstimatedWaitTime": self.EstimatedWaitTime,
            "Status": self.Status
        }

@app.route('/api/health')
def health_check():
    return jsonify({"message": "API is running!"})

@app.route("/api/orderqueue", methods=["GET"])
def get_order_queue():
    queue = OrderQueue.query.all()
    return jsonify({"orderQueue": [q.json() for q in queue]})

@app.route("/api/orderqueue", methods=["POST"])
def add_to_queue():
    data = request.json
    order_id = data.get('OrderID')
    estimated_wait_time = data.get('EstimatedWaitTime')

    if not order_id or not estimated_wait_time:
        return jsonify({"message": "OrderID and EstimatedWaitTime are required"}), 400

    new_queue_entry = OrderQueue(
        OrderID=order_id,
        EstimatedWaitTime=estimated_wait_time
    )

    db.session.add(new_queue_entry)
    db.session.commit()

    return jsonify({"message": "Order added to queue successfully", "QueueID": new_queue_entry.QueueID}), 201

@app.route("/api/orderqueue/<int:queue_id>", methods=["GET"])
def get_queue_entry(queue_id):
    queue_entry = OrderQueue.query.filter_by(QueueID=queue_id).first()

    if not queue_entry:
        return jsonify({"message": "Queue entry not found"}), 404

    return jsonify(queue_entry.json())

@app.route("/api/orderqueue/<int:queue_id>", methods=["PUT"])
def update_queue_entry(queue_id):
    data = request.json
    status = data.get('Status')

    if status not in ['Pending', 'In Progress', 'Completed']:
        return jsonify({"message": "Invalid status"}), 400

    queue_entry = OrderQueue.query.filter_by(QueueID=queue_id).first()

    if not queue_entry:
        return jsonify({"message": "Queue entry not found"}), 404

    queue_entry.Status = status
    db.session.commit()

    return jsonify({"message": "Queue entry status updated successfully", "QueueID": queue_id})

@app.route("/api/orderqueue/<int:queue_id>", methods=["DELETE"])
def delete_queue_entry(queue_id):
    queue_entry = OrderQueue.query.filter_by(QueueID=queue_id).first()

    if not queue_entry:
        return jsonify({"message": "Queue entry not found"}), 404

    db.session.delete(queue_entry)
    db.session.commit()

    return jsonify({"message": "Queue entry deleted successfully"})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
