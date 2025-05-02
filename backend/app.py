from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask import request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash 
from datetime import datetime, timedelta
from model import db, Employee, Attendance, LeaveRequest, OutingRequest, MakeupCardRequest, AttendanceSettings
from apscheduler.schedulers.background import BackgroundScheduler
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
#员工登录接口
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    employee_id = data.get('employee_id')
    password = data.get('password')

    # 根据 employee_id 查找员工
    employee = Employee.query.filter_by(employee_id=employee_id).first()

    if not employee:
        return jsonify({'message': '员工编号不存在'}), 404
    
    # 校验密码
    if not check_password_hash(employee.password, password):
        return jsonify({'message': '密码错误'}), 401
    
    return jsonify({'message': '登录成功'}), 200
############################################################
#员工信息填写接口

@app.route('/update_profile', methods=['POST'])
def update_profile():
    data = request.get_json()
    employee_id = data.get('employee_id')  # 前端提供作为身份识别

    employee = Employee.query.filter_by(employee_id=employee_id).first()
    if not employee:
        return jsonify({"error": "用户不存在"}), 404

    # 更新信息（哪个字段有就更新哪个）
    employee.name = data.get('name', employee.name)
    employee.phone = data.get('phone', employee.phone)
    employee.email = data.get('email', employee.email)

   
    db.session.commit()
    return jsonify({"message": "个人信息更新成功"})
#############################################################
#员工修改密码接口
@app.route('/change_password', methods=['POST'])
def change_password():
    data = request.get_json()
    employee_id = data.get('employee_id')
    old_password = data.get('old_password')
    new_password = data.get('new_password')

    if not all([employee_id, old_password, new_password]):
        return jsonify({"error": "参数不完整"}), 400

    employee = Employee.query.filter_by(employee_id=employee_id).first()
    if not employee:
        return jsonify({"error": "用户不存在"}), 404

    if not check_password_hash(employee.password, old_password):
        return jsonify({"error": "原密码错误"}), 401

    employee.password = generate_password_hash(new_password)
    db.session.commit()

    return jsonify({"message": "密码修改成功"}), 200

#############################################################
#员工查看个人信息接口

@app.route('/get_profile', methods=['GET'])
def get_profile():
    employee_id = request.args.get('employee_id')  # 从查询参数中获取 employee_id

    if not employee_id:
        return jsonify({"error": "缺少 employee_id 参数"}), 400

    employee = Employee.query.filter_by(employee_id=employee_id).first()
    if not employee:
        return jsonify({"error": "用户不存在"}), 404

    result = {
        "employee_id": employee.employee_id,
        "name": employee.name,
        "gender": employee.gender,
        "phone": employee.phone,
        "email": employee.email,
        "position": employee.position,
        "department": employee.department,
        "role": employee.role,
        "join_date": employee.join_date.strftime('%Y-%m-%d') if employee.join_date else None
    }

    return jsonify(result), 200

#############################################################
# 员工提交打卡记录接口
@app.route('/employee/clock_in', methods=['POST'])
def clock_in():
    data = request.get_json()
    employee_id = data.get('employee_id')
    clock_in_time = datetime.strptime(data.get('time'), '%H:%M:%S').time()
    
    # 设定上班时间（可以存储在数据库中，假设为9:00:00）
    work_start_time = datetime.strptime('09:00:00', '%H:%M:%S').time()
    
    # 获取今天的日期
    today = datetime.today().date()
    
    # 查找是否有请假记录
    leave = LeaveRequest.query.filter_by(
        employee_id=employee_id,
        start_date__lte=today,
        end_date__gte=today,
        status='已批准'
    ).first()
    
    # 如果有请假，记录为“请假”
    if leave:
        new_attendance = Attendance(
            employee_id=employee_id,
            date=today,
            time=clock_in_time,
            type='打卡',
            status='请假'
        )
    else:
        # 判断是否迟到
        if clock_in_time > work_start_time:
            status = '迟到'
        else:
            status = '正常'
        
        # 记录考勤
        new_attendance = Attendance(
            employee_id=employee_id,
            date=today,
            time=clock_in_time,
            type='打卡',
            status=status
        )
    
    db.session.add(new_attendance)
    db.session.commit()

    return jsonify({'message': '打卡成功'}), 200

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
#员工申请外勤
@app.route('/employee/outingRequest', methods=['POST'])
def submit_outing_request():
    data = request.get_json()

    employee_id = data.get('employee_id')
    date = datetime.strptime(data.get('date'), '%Y-%m-%d').date()
    start_time = datetime.strptime(data.get('start_time'), '%H:%M:%S').time()
    end_time = datetime.strptime(data.get('end_time'), '%H:%M:%S').time()
    reason = data.get('reason', '')

    outing = OutingRequest(
        employee_id=employee_id,
        date=date,
        start_time=start_time,
        end_time=end_time,
        reason=reason,
        status='待审批'
    )

    db.session.add(outing)
    db.session.commit()

    return jsonify({'message': '外勤申请已提交'})

############################################################
#员工申请补卡
@app.route('/employee/makeupCardRequest', methods=['POST'])
def submit_makeup_card_request():
    data = request.get_json()

    employee_id = data.get('employee_id')
    date = datetime.strptime(data.get('date'), '%Y-%m-%d').date()
    time = datetime.strptime(data.get('time'), '%H:%M:%S').time()
    reason = data.get('reason', '')

    request_entry = MakeupCardRequest(
        employee_id=employee_id,
        date=date,
        time=time,
        reason=reason,
        status='待审批'
    )

    db.session.add(request_entry)
    db.session.commit()

    return jsonify({'message': '补卡申请已提交'})



############################################################
#管理员终端接口
#############################################################
# 管理端添加员工接口
# 添加员工接口
@app.route('/add_employee', methods=['POST'])
def add_employee():
    data = request.get_json()
    
    # 获取请求中的数据
    name = data.get('name')
    employee_id = data.get('employee_id')
    phone = data.get('phone')
    position = data.get('position')
    department = data.get('department')
    role = data.get('role', '员工')  # 默认角色为员工
    
    # 判断是否有重复的员工编号
    if Employee.query.filter_by(employee_id=employee_id).first():
        return jsonify({'message': '员工编号已存在'}), 400
    
    # 设置默认密码为 '123456' 并加密
    hashed_password = generate_password_hash('123456')

    # 创建新员工实例
    new_employee = Employee(
        employee_id=employee_id,
        name=name,
        phone=phone,
        position=position,
        department=department,
        role=role,
        password=hashed_password
    )
    
    # 将新员工添加到数据库
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
# 管理员审批员工请假记录接口
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

    if status == '已批准':
        # 审批通过后为每个请假日期添加或更新考勤记录
        current_date = leave.start_date
        while current_date <= leave.end_date:
            attendance = Attendance.query.filter_by(
                employee_id=leave.employee_id,
                date=current_date
            ).first()

            if attendance:
                attendance.status = '请假'
                attendance.type = '系统'
            else:
                new_attendance = Attendance(
                    employee_id=leave.employee_id,
                    date=current_date,
                    time=datetime.strptime('00:00:00', '%H:%M:%S').time(),
                    status='请假',
                    type='系统'
                )
                db.session.add(new_attendance)
            current_date += timedelta(days=1)

    db.session.commit()
    return jsonify({'message': f'请假状态已更新为：{status}'}), 200

###############################################################
# 管理员审批员工外勤接口
@app.route('/admin/outing/approve/<int:outing_id>', methods=['POST'])
def approve_outing_request(outing_id):
    data = request.get_json()
    status = data.get('status')  # 应为 '已批准' 或 '已拒绝'

    # 检查状态是否有效
    if status not in ['已批准', '已拒绝']:
        return jsonify({'message': '无效的状态，应为 "已批准" 或 "已拒绝"'}), 400

    # 查找外勤申请记录
    outing = OutingRequest.query.get(outing_id)
    if not outing:
        return jsonify({'message': '外勤申请记录不存在'}), 404

    # 更新状态
    outing.status = status
    db.session.commit()

    return jsonify({'message': f'外勤申请状态已更新为：{status}'}), 200


###############################################################
#管理员审批员工补卡接口
@app.route('/admin/makeupCardRequest/<int:request_id>', methods=['POST'])
def approve_makeup_card_request(request_id):
    data = request.get_json()
    status = data.get('status')  # '已批准' 或 '已拒绝'

    # 验证状态是否合法
    if status not in ['已批准', '已拒绝']:
        return jsonify({'message': '无效的状态，应为 "已批准" 或 "已拒绝"'}), 400

    # 查找补卡申请
    request_entry = MakeupCardRequest.query.get(request_id)
    if not request_entry:
        return jsonify({'message': '补卡申请不存在'}), 404

    # 更新申请状态
    request_entry.status = status
    db.session.commit()

    return jsonify({'message': f'补卡申请已更新为：{status}'}), 200


###############################################################
@app.route('/admin/employee/clock_in_settings/<int:employee_id>', methods=['POST'])
def update_employee_clock_in_settings(employee_id):
    data = request.get_json()

    clock_in_method = data.get('clock_in_method')  # 打卡方式: '人脸'、'地点'、'混合'
    clock_in_time = data.get('clock_in_time')  # 打卡时间
    clock_in_location = data.get('clock_in_location')  # 打卡地点

    # 校验打卡方式是否合法
    if clock_in_method not in ['人脸', '地点', '混合']:
        return jsonify({'message': '无效的打卡方式，必须是 “人脸”、“地点” 或 “混合”'}), 400

    # 查找该员工的打卡设置
    employee_settings = AttendanceSettings.query.filter_by(employee_id=employee_id).first()

    if not employee_settings:
        return jsonify({'message': '该员工没有设置打卡方式'}), 404

    # 更新打卡方式
    employee_settings.clock_in_method = clock_in_method
    
    if clock_in_time:
        try:
            # 将打卡时间字符串转换为时间类型
            employee_settings.clock_in_time = datetime.strptime(clock_in_time, '%H:%M:%S').time()
        except ValueError:
            return jsonify({'message': '无效的打卡时间格式'}), 400

    if clock_in_location:
        employee_settings.clock_in_location = clock_in_location
    
    db.session.commit()

    return jsonify({'message': '员工打卡方式更新成功'}), 200

###############################################################
#考勤系统定时任务
def check_attendance():
    today = datetime.today().date()
    employees = Employee.query.all()

    for employee in employees:
        # 检查是否有当天的考勤记录
        attendance = Attendance.query.filter_by(employee_id=employee.id, date=today).first()
        
        if not attendance:
            # 如果没有考勤记录，检查是否有请假
            leave = LeaveRequest.query.filter_by(
                employee_id=employee.id,
                start_date__lte=today,
                end_date__gte=today,
                status='已批准'
            ).first()
            
            if leave:
                # 如果有请假，记录为“请假”
                new_attendance = Attendance(
                    employee_id=employee.id,
                    date=today,
                    time=datetime.strptime('00:00:00', '%H:%M:%S').time(),  # 设置时间为00:00:00，表示全天请假
                    type='系统',
                    status='请假'
                )
                db.session.add(new_attendance)
            else:
                # 如果没有请假，记录为“缺勤”
                new_attendance = Attendance(
                    employee_id=employee.id,
                    date=today,
                    time=datetime.min.time(),  # 设置时间为最小时间值
                    type='系统',
                    status='缺勤'
                )
                db.session.add(new_attendance)
        
        # 提交数据库操作
        db.session.commit()

# 设置定时任务，使用APS调度器
scheduler = BackgroundScheduler()
scheduler.add_job(func=check_attendance, trigger="cron", hour=0, minute=0)  # 每天午夜0点执行
scheduler.start()
###############################################################
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # 创建所有定义好的表（第一次运行时自动创建）
    app.run(debug=True)



