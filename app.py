from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
from datetime import datetime, date, time
import datetime

app = Flask(__name__)

# MySQL configurations
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'company_attendance'

mysql = MySQL(app)

@app.route('/attendance', methods=['POST'])
def add_attendance():
    employee_id = request.json['employee_id']
    check_in = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    today = date.today()

    cur = mysql.connection.cursor()

    # Periksa apakah ada absensi dengan employee_id dan tanggal yang sesuai
    cur.execute("SELECT * FROM attendance WHERE employee_id = %s AND DATE(check_in) = %s", (employee_id, today))
    existing_attendance = cur.fetchone()

    # Jika sudah ada absensi, berikan informasi kepada pengguna
    if existing_attendance:
        return jsonify({'message': 'Employee has already checked in today'})

    cur.execute("INSERT INTO attendance (employee_id, check_in) VALUES (%s, %s)", (employee_id, check_in))
    mysql.connection.commit()
    cur.close()

    return jsonify({'message': 'Attendance added successfully'})

@app.route('/attendance/<int:attendance_id>', methods=['PUT'])
def update_attendance(attendance_id):
    check_out = request.json['check_out']

    cur = mysql.connection.cursor()

    # Mendapatkan data check_in dari database
    cur.execute("SELECT check_in FROM attendance WHERE id = %s", (attendance_id,))
    result = cur.fetchone()
    check_in = result[0]

    # Mendapatkan jam check_out maksimal (17:00:00) di hari yang sama dengan check_in
    check_out_max = datetime.datetime.combine(check_in, time(hour=17))

    # Mendapatkan datetime objek dari check_out yang diberikan
    check_out_datetime = datetime.datetime.strptime(check_out, '%Y-%m-%d %H:%M:%S')

    # Memeriksa apakah check_out melebihi batas maksimal
    if check_out_datetime > check_out_max:
        jsonify({'message': 'Check-out melebihi batas waktu maksimal (17:00:00)'})
        check_out = check_out_max
        cur.execute("UPDATE attendance SET check_out = %s WHERE id = %s", (check_out, attendance_id))
        mysql.connection.commit()
        cur.close()

        return jsonify({'message': 'Attendance updated successfully with condition'})

    # Memeriksa apakah check_out lebih awal dari check_in
    if check_out_datetime < check_in:
        return jsonify({'message': 'Check-out can not eralier than check-in'})

    # Memperbarui data check_out di database
    cur.execute("UPDATE attendance SET check_out = %s WHERE id = %s", (check_out, attendance_id))
    mysql.connection.commit()
    cur.close()

    return jsonify({'message': 'Attendance updated successfully'})


@app.route('/attendance/<int:attendance_id>', methods=['DELETE'])
def delete_attendance(attendance_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM attendance WHERE id = %s", (attendance_id,))
    mysql.connection.commit()
    cur.close()

    return jsonify({'message': 'Attendance deleted successfully'})


@app.route('/attendance/close', methods=['PUT'])
def close_attendance():
    cur = mysql.connection.cursor()

    # Mendapatkan data absensi yang belum memiliki check_out
    cur.execute("SELECT id, check_in FROM attendance WHERE check_out IS NULL")
    results = cur.fetchall()

    # Mengupdate check_out untuk setiap absensi yang belum ditutup
    for result in results:
        attendance_id = result[0]
        check_in = result[1]

        if check_in is not None:
            # Mendapatkan jam check_out maksimal (17:00:00) di hari yang sama dengan check_in
            check_out_max = datetime.datetime.combine(check_in.date(), time(hour=17))

            # Memperbarui check_out di database
            cur.execute("UPDATE attendance SET check_out = %s WHERE id = %s", (check_out_max, attendance_id))
            mysql.connection.commit()

    cur.close()

    return jsonify({'message': 'Attendance closed successfully'})

@app.route('/calculate_rating', methods=['POST'])
def calculate_rating():
    cur = mysql.connection.cursor()

    # Mendapatkan daftar karyawan dari tabel karyawan
    cur.execute("SELECT id FROM employees")
    employee_ids = cur.fetchall()

    for employee_id in employee_ids:
        # Mendapatkan total jam kerja per bulan untuk karyawan tertentu
        cur.execute("SELECT SUM(TIME_TO_SEC(TIMEDIFF(check_out, check_in))) AS total_hours FROM attendance WHERE employee_id = %s AND YEAR(check_in) = YEAR(CURDATE()) AND MONTH(check_in) = MONTH(CURDATE())", (employee_id,))
        result = cur.fetchone()
        total_hours = result[0]/3600

        # Menghitung rating berdasarkan total jam kerja
        rating = calculate_rating(total_hours)

        # Memperbarui kolom total_hours dan rating di tabel karyawan
        cur.execute("UPDATE employees SET total_hours = %s, rating = %s WHERE id = %s", (total_hours, rating, employee_id))
        mysql.connection.commit()

    cur.close()

    return jsonify({'message': 'Rating calculated successfully'})

def calculate_rating(total_hours):
    # Menghitung rating berdasarkan total jam kerja
    if total_hours >= 160:
        return 'Very Good'
    elif total_hours >= 120:
        return 'Good'
    else:
        return 'Bad'

@app.route('/employees', methods=['GET'])
def get_employees():
    name = request.args.get('name')  # Mendapatkan parameter 'name' dari query string

    cur = mysql.connection.cursor()
    
    if name:
        # Jika parameter 'name' ada, lakukan pencarian berdasarkan nama
        cur.execute("SELECT * FROM employees WHERE name LIKE %s", ('%' + name + '%',))
    else:
        # Jika parameter 'name' tidak ada, ambil semua data karyawan
        cur.execute("SELECT * FROM employees")

    rows = cur.fetchall()
    cur.close()

    employees = []
    for row in rows:
        employee = {
            'id': row[0],
            'name': row[1],
            'designation': row[2],
            'feedback': row[3],
            'total_hour': row[4],
            'rating': row[5]
        }
        employees.append(employee)

    return jsonify(employees)


if __name__ == '__main__':
    app.run(debug=True)
