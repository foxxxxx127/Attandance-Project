from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask import request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash 
from datetime import datetime
from model import db, Employee, Attendance, LeaveRequest

############################################################
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///attandance.db'  # 数据库文件名
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 关闭警告
db.init_app(app)

############################################################
#根目录
@app.route('/')
def index():
    return "数据库连接成功"

############################################################
#员工终端接口
############################################################
#员工信息填写接口

@app.route('/update_profile', methods=['POST'])
def update_profile():
    data = request.get_json()
    username = data.get('username')  # 前端提供用户名作为身份识别

    employee = Employee.query.filter_by(username=username).first()
    if not employee:
        return jsonify({"error": "用户不存在"}), 404

    # 更新信息（哪个字段有就更新哪个）
    employee.name = data.get('name', employee.name)
    employee.phone = data.get('phone', employee.phone)
    employee.email = data.get('email', employee.email)
   
    db.session.commit()
    return jsonify({"message": "个人信息更新成功"})

#############################################################
# 员工提交打卡记录接口
@app.route('/attendance', methods=['POST'])
def add_attendance():
    data = request.get_json()
    try:
        new_record = Attendance(
            employee_id=data['employee_id'],
            date=datetime.strptime(data['date'], '%Y-%m-%d').date(),
            time=datetime.strptime(data['time'], '%H:%M:%S').time(),
            type=data['type'],
            status=data['status']
        )
        db.session.add(new_record)
        db.session.commit()
        return jsonify({"message": "打卡记录添加成功"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

##############################################################
# 员工查询打卡记录接口
@app.route('/attendance/<int:employee_id>', methods=['GET'])
def get_attendance(employee_id):
    records = Attendance.query.filter_by(employee_id=employee_id).all()
    if not records:
        return jsonify({"message": "没有找到打卡记录"}), 404

    result = []
    for record in records:
        result.append({
            "date": record.date.strftime('%Y-%m-%d'),
            "time": record.time.strftime('%H:%M:%S'),
            "type": record.type,
            "status": record.status
        })
    return jsonify(result)

###############################################################
# 员工请假申请接口
@app.route('/employee/leaveRequest', methods=['POST'])
def submit_leave_request():
    data = request.get_json()

    employee_id = data.get('employee_id')
    start_date = datetime.strptime(data.get('start_date'), '%Y-%m-%d').date()
    end_date = datetime.strptime(data.get('end_date'), '%Y-%m-%d').date()
    leave_type = data.get('leave_type')
    reason = data.get('reason', '')

    leave = LeaveRequest(
        employee_id=employee_id,
        start_date=start_date,
        end_date=end_date,
        leave_type=leave_type,
        reason=reason,
        status='待审批'
    )

    db.session.add(leave)
    db.session.commit()

    return jsonify({'message': '请假申请已提交'})




############################################################
#管理员终端接口
#############################################################
# 管理端添加员工接口
# POST请求，接收JSON数据，添加员工信息到数据库
@app.route('/add_employee', methods=['POST'])
def add_employee():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    name = data.get('name')
    employee_id = data.get('employee_id')
    phone = data.get('phone')
    position = data.get('position')
    department = data.get('department')
    role = data.get('role', '员工')

    # 判断是否重复
    if Employee.query.filter_by(username=username).first():
        return jsonify({'message': '用户名已存在'}), 400
    if Employee.query.filter_by(employee_id=employee_id).first():
        return jsonify({'message': '员工编号已存在'}), 400

    hashed_password = generate_password_hash(password)
    new_employee = Employee(
        username=username,
        password=hashed_password,
        name=name,
        employee_id=employee_id,
        phone=phone,
        position=position,
        department=department,
        role=role
    )
    db.session.add(new_employee)
    db.session.commit()

    return jsonify({'message': '员工添加成功'}), 201
###############################################################
# 管理员查看员工打卡信息接口
@app.route('/admin/attendance', methods=['GET'])
def get_all_attendance():
    # 获取查询参数
    employee_id = request.args.get('employee_id', type=int)  # 筛选员工ID
    date = request.args.get('date')  # 筛选日期
    page = request.args.get('page', 1, type=int)  # 页码，默认为1
    per_page = request.args.get('per_page', 10, type=int)  # 每页记录数，默认为10

    # 构造查询条件
    query = Attendance.query

    if employee_id:
        query = query.filter(Attendance.employee_id == employee_id)  # 按员工ID筛选
    if date:
        query = query.filter(Attendance.date == date)  # 按日期筛选

    # 执行查询并分页
    records = query.paginate(page, per_page, False).items
    
    result = []
    for r in records:
        result.append({
            'employee_id': r.employee_id,
            'date': r.date.strftime('%Y-%m-%d'),
            'time': r.time.strftime('%H:%M:%S'),
            'type': r.type,
            'status': r.status
        })
    
    return jsonify(result)
##############################################################
# 管理员审批请假接口
@app.route('/admin/leave/<int:leave_id>', methods=['POST'])
def update_leave_status(leave_id):
    data = request.get_json()
    status = data.get('status')  # 应为 '已批准' 或 '已拒绝'

    if status not in ['已批准', '已拒绝']:
        return jsonify({'message': '无效的状态，应为 "已批准" 或 "已拒绝"'}), 400

    leave = LeaveRequest.query.get(leave_id)
    if not leave:
        return jsonify({'message': '请假记录不存在'}), 404

    leave.status = status
    db.session.commit()
    return jsonify({'message': f'请假状态已更新为：{status}'}), 200

###############################################################
# 管理员更改员工打卡方式接口

###############################################################
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # 创建所有定义好的表（第一次运行时自动创建）
    app.run(debug=True)



