from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask import request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash 
from datetime import datetime, timedelta
from model import db, Employee, Attendance, LeaveRequest, OutingRequest, MakeupCardRequest, AttendanceSettings
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy import and_
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
from scr.face_recognition_service import compare_faces
import uuid
from flask import send_from_directory
############################################################
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///attandance.db'  # 数据库文件名
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 关闭警告
db.init_app(app)
CORS(app)  # 启用跨域支持
############################################################
#根目录
@app.route('/')
def index():
    return "数据库连接成功"
############################################################
#员工终端接口
#############################################################
#员工注册接口
@app.route('/register', methods=['POST'])
def register():
    """
    员工注册接口
    """
    data = request.get_json()

    # 获取注册信息
    employee_id = data.get('employee_id')
    password = data.get('password')
    name = data.get('name')
    phone = data.get('phone')
    department = data.get('department')
    role = data.get('role', '员工')  # 默认角色为员工
    email = data.get('email')
    join_date = data.get('join_date')

    if not all([employee_id, password, name, phone, department, email]):
        return jsonify({"message": "缺少必填字段"}), 400
    
    # 检查员工编号是否已存在
    existing_employee = Employee.query.filter_by(employee_id=employee_id).first()
    if existing_employee:
        return jsonify({"message": "员工编号已存在"}), 400

    # 加密密码
    hashed_password = generate_password_hash(password)

    # 创建新员工记录
    new_employee = Employee(
        employee_id=employee_id,
        password=hashed_password,
        name=name,
        phone=phone,
        department=department,
        role=role,
        email=email,
        join_date=datetime.strptime(join_date, '%Y-%m-%d').date() if join_date else None
    )

    # 保存到数据库
    db.session.add(new_employee)
    db.session.commit()

    return jsonify({"message": "注册成功"}), 201
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
    employee.gender = data.get('gender', employee.gender)
    employee.phone = data.get('phone', employee.phone)
    employee.email = data.get('email', employee.email)
    employee.position = data.get('position', employee.position)
    employee.department = data.get('department', employee.department)
    employee.role = data.get('role', employee.role)
    employee.photo = data.get('photo')  # 更新照片路径或 URL

    db.session.commit()

    # 返回更新后的信息
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

    return jsonify({"message": "个人信息更新成功", "updated_info": result}), 200
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
        "join_date": employee.join_date.strftime('%Y-%m-%d') if employee.join_date else None,
        "photo": employee.photo  # 返回照片路径或 URL
    }

    return jsonify(result), 200
#############################################################
# 配置上传文件夹
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 如果文件夹不存在，则创建
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# 允许的文件扩展名
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 静态文件服务，前端可通过 http://127.0.0.1:5000/uploads/xxx.jpg 访问
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# 上传照片接口
@app.route('/upload_photo', methods=['POST'])
def upload_photo():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(save_path)
        # 返回相对路径，前端拼接 http://127.0.0.1:5000 + url 即可访问
        return jsonify({'url': f'/uploads/{filename}'})
    return jsonify({'error': 'Invalid file type'}), 400
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
    leave = LeaveRequest.query.filter(
    and_(
        LeaveRequest.employee_id == employee_id,
        LeaveRequest.start_date <= today,
        LeaveRequest.end_date >= today,
        LeaveRequest.status == '已批准'
        )
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
@app.route('/attendance/<employee_id>', methods=['GET'])
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
    reason = data.get('reason', '')

    leave = LeaveRequest(
        employee_id=employee_id,
        start_date=start_date,
        end_date=end_date,
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
    start_date = datetime.strptime(data.get('start_date'), '%Y-%m-%d').date()
    end_date = datetime.strptime(data.get('end_date'), '%Y-%m-%d').date()
    location = data.get('location', '')
    reason = data.get('reason', '')

    outing = OutingRequest(
        employee_id=employee_id,
        start_date=start_date,
        end_date=end_date,
        reason=reason,
        location=location,
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
    start_date = datetime.strptime(data.get('start_date'), '%Y-%m-%d').date()
    end_date = datetime.strptime(data.get('end_date'), '%Y-%m-%d').date()
    reason = data.get('reason', '')

    request_entry = MakeupCardRequest(
        employee_id=employee_id,
        start_date=start_date,
        end_date=end_date,
        reason=reason,
        status='待审批'
    )

    db.session.add(request_entry)
    db.session.commit()

    return jsonify({'message': '补卡申请已提交'})
#############################################################
@app.route('/employee/approval_records/<employee_id>', methods=['GET'])
def get_approval_records(employee_id):
    """
    获取员工的审批记录，包括事件类型、审批结果和申请原因。
    """
    # 获取查询参数
    event_type = request.args.get('type', '')  # 事件类型（leave, card, field）
    page = int(request.args.get('page', 1))  # 当前页码
    size = int(request.args.get('size', 10))  # 每页记录数

    # 初始化查询结果
    records = []

    # 查询请假审批记录
    if event_type in ('', 'leave'):
        leave_records = LeaveRequest.query.filter_by(employee_id=employee_id).all()
        for record in leave_records:
            records.append({
                "application_time": f"{record.start_date.strftime('%Y-%m-%d')} 至 {record.end_date.strftime('%Y-%m-%d')}",
                "event_type": "请假审批",
                "status": record.status,
                "reason": record.reason  # 添加申请原因
            })

    # 查询补卡审批记录
    if event_type in ('', 'card'):
        card_records = MakeupCardRequest.query.filter_by(employee_id=employee_id).all()
        for record in card_records:
            records.append({
                "application_time": f"{record.start_date.strftime('%Y-%m-%d')} 至 {record.end_date.strftime('%Y-%m-%d')}",
                "event_type": "补卡审批",
                "status": record.status,
                "reason": record.reason  # 添加申请原因
            })

    # 查询外勤审批记录
    if event_type in ('', 'field'):
        field_records = OutingRequest.query.filter_by(employee_id=employee_id).all()
        for record in field_records:
            records.append({
                "application_time": f"{record.start_date.strftime('%Y-%m-%d')} 至 {record.end_date.strftime('%Y-%m-%d')}",
                "event_type": "外勤审批",
                "status": record.status,
                "reason": record.reason  # 添加申请原因
            })

    # 按申请时间排序
    records.sort(key=lambda x: x['application_time'], reverse=True)

    # 分页
    total = len(records)
    start = (page - 1) * size
    end = start + size
    paginated_records = records[start:end]

    # 返回结果
    return jsonify({
        "code": 0,
        "message": "审批记录获取成功",
        "data": {
            "records": paginated_records,
            "total": total
        }
    }), 200
#############################################################
# 员工人脸识别接口
@app.route('/api/face_recognition', methods=['POST'])
def face_recognition_api():
    """
    前端上传两张图片，判断是否为同一个人
    """
    if 'image1' not in request.files or 'image2' not in request.files:
        return jsonify({'code': 1, 'msg': '缺少图片'}), 400

    image1 = request.files['image1']
    image2 = request.files['image2']

    # 临时保存图片
    save_dir = 'temp_faces'
    os.makedirs(save_dir, exist_ok=True)
    path1 = os.path.join(save_dir, f"{uuid.uuid4().hex}_1.jpg")
    path2 = os.path.join(save_dir, f"{uuid.uuid4().hex}_2.jpg")
    image1.save(path1)
    image2.save(path2)

    try:
        result = compare_faces(path1, path2)
        os.remove(path1)
        os.remove(path2)
        return jsonify({'code': 0, 'result': bool(result)})
    except Exception as e:
        os.remove(path1)
        os.remove(path2)
        return jsonify({'code': 2, 'msg': str(e)}), 500
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
    employee_id = request.args.get('employee_id')  # 筛选员工ID
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
    records = query.paginate(page=page, per_page=per_page, error_out=False).items
    
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

################################################################
# 管理员查看员工请假记录接口
# 查询所有请假记录接口
@app.route('/admin/leave', methods=['GET'])
def get_all_leaves():
    leaves = LeaveRequest.query.all()
    result = []
    for leave in leaves:
        # 根据 employee_id 查询 Employee 表获取 name
        employee = Employee.query.filter_by(employee_id=leave.employee_id).first()
        result.append({
            "id": leave.id,
            "employee_id": leave.employee_id,
            "applicant": employee.name if employee else "未知",  # 如果 employee 为 None，设置为 "未知"
            "start_date": leave.start_date.strftime('%Y-%m-%d'),
            "end_date": leave.end_date.strftime('%Y-%m-%d'),
            "reason": leave.reason,
            "status": leave.status
        })
    return jsonify(result), 200
##############################################################
# 管理员审批员工请假记录接口
@app.route('/admin/leave/<int:leave_id>', methods=['POST'])
def approve_leave(leave_id):
    data = request.get_json()
    status = data.get('status')

    if status not in ['已批准', '已拒绝']:
        return jsonify({'error': '无效的审批状态'}), 400

    leave_request = LeaveRequest.query.get(leave_id)
    if not leave_request:
        return jsonify({'error': '未找到对应的请假记录'}), 404

    leave_request.status = status
    db.session.commit()

    return jsonify({'message': f'请假申请已{status}'}), 200
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



