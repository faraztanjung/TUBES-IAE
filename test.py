# @app.route('/employees', methods=['GET'])
# def get_employees():
#     cur = mysql.connection.cursor()
#     cur.execute("SELECT * FROM employees")
#     rows = cur.fetchall()
#     cur.close()

#     employees = []
#     for row in rows:
#         employee = {
#             'id': row[0],
#             'name': row[1],
#             'designation': row[2],
#             'feedback': row[3]
#         }
#         employees.append(employee)

#     return jsonify(employees)


# @app.route('/employees', methods=['POST'])
# def add_employee():
#     name = request.json['name']
#     designation = request.json['designation']

#     cur = mysql.connection.cursor()
#     cur.execute("INSERT INTO employees (name, designation) VALUES (%s, %s)", (name, designation))
#     mysql.connection.commit()
#     cur.close()

#     return jsonify({'message': 'Employee added successfully'})


# @app.route('/employees/<int:employee_id>', methods=['GET'])
# def get_employee(employee_id):
#     cur = mysql.connection.cursor()
#     cur.execute("SELECT * FROM employees WHERE id = %s", (employee_id,))
#     row = cur.fetchone()
#     cur.close()

#     if row:
#         employee = {
#             'id': row[0],
#             'name': row[1],
#             'designation': row[2],
#             'feedback': row[3]
#         }
#         return jsonify(employee)
#     else:
#         return jsonify({'message': 'Employee not found'}), 404


# @app.route('/employees/<int:employee_id>', methods=['PUT'])
# def update_employee(employee_id):
#     name = request.json['name']
#     designation = request.json['designation']

#     cur = mysql.connection.cursor()
#     cur.execute("UPDATE employees SET name = %s, designation = %s WHERE id = %s", (name, designation, employee_id))
#     mysql.connection.commit()
#     cur.close()

#     return jsonify({'message': 'Employee updated successfully'})


# @app.route('/employees/<int:employee_id>', methods=['DELETE'])
# def delete_employee(employee_id):
#     cur = mysql.connection.cursor()
#     cur.execute("DELETE FROM employees WHERE id = %s", (employee_id,))
#     mysql.connection.commit()
#     cur.close()

#     return jsonify({'message': 'Employee deleted successfully'})

