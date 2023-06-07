from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/attendance_system'
db = SQLAlchemy(app)

# Employee model
class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    card_id = db.Column(db.String(10), nullable=False)
    attendances = db.relationship('Attendance', backref='employee', lazy=True)

# Attendance model
class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    check_in = db.Column(db.DateTime)
    check_out = db.Column(db.DateTime)

# Routes
@app.route('/employees', methods=['GET'])
def get_employees():
    employees = Employee.query.all()
    return jsonify([employee.name for employee in employees])

@app.route('/employees', methods=['POST'])
def create_employee():
    data = request.get_json()
    employee = Employee(name=data['name'], card_id=data['card_id'])
    db.session.add(employee)
    db.session.commit()
    return jsonify({'message': 'Employee created successfully'})

@app.route('/attendance', methods=['POST'])
def record_attendance():
    data = request.get_json()
    employee = Employee.query.filter_by(card_id=data['card_id']).first()
    if not employee:
        return jsonify({'message': 'Employee not found'})

    attendance = Attendance(employee_id=employee.id, check_in=datetime.now())
    db.session.add(attendance)
    db.session.commit()
    return jsonify({'message': 'Attendance recorded successfully'})

@app.route('/attendance/<int:attendance_id>', methods=['PUT'])
def update_attendance(attendance_id):
    attendance = Attendance.query.get(attendance_id)
    if not attendance:
        return jsonify({'message': 'Attendance not found'})

    attendance.check_out = datetime.now()
    db.session.commit()
    return jsonify({'message': 'Attendance updated successfully'})

@app.route('/attendance/<int:attendance_id>', methods=['DELETE'])
def delete_attendance(attendance_id):
    attendance = Attendance.query.get(attendance_id)
    if not attendance:
        return jsonify({'message': 'Attendance not found'})

    db.session.delete(attendance)
    db.session.commit()
    return jsonify({'message': 'Attendance deleted successfully'})

if __name__ == '__main__':
    app.run()
