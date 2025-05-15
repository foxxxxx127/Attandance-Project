from flask_sqlalchemy import SQLAlchemy

###############################################################
db = SQLAlchemy()  # 创建数据库对象

############################################################
# 定义一个员工表
class Employee(db.Model):
    __tablename__ = 'employee'

    id = db.Column(db.Integer, primary_key=True) # 主键
    employee_id = db.Column(db.String(20), unique=True)  # 员工编号
    password = db.Column(db.String(100), nullable=False) # 密码
    name = db.Column(db.String(50))           # 姓名
    gender = db.Column(db.String(10))         # 性别
    phone = db.Column(db.String(20))          # 手机号
    position = db.Column(db.String(50))       # 职位
    department = db.Column(db.String(50))     # 部门
    role = db.Column(db.String(10))           # 员工/管理员
    email = db.Column(db.String(100))         # 邮箱
    join_date = db.Column(db.Date)            # 入职日期
    photo = db.Column(db.String(255))  # 员工照片路径或 URL


    #关系定义
    attendances = db.relationship('Attendance', backref='employee', lazy=True)
    leave_requests = db.relationship('LeaveRequest', backref='employee', lazy=True)  
    outing_requests = db.relationship('OutingRequest', backref='employee', lazy=True)
    makeup_card_requests = db.relationship('MakeupCardRequest', backref='employee', lazy=True)

##############################################################
# 定义一个考勤表
class Attendance(db.Model):
    __tablename__ = 'attendance'

    id = db.Column(db.Integer, primary_key=True)  # 唯一标识每条打卡记录
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)  # 所属员工
    date = db.Column(db.Date, nullable=False)  # 打卡的日期（例如 2025-05-02）
    time = db.Column(db.Time, nullable=False)  # 打卡时间（例如 08:30:00）
    type = db.Column(db.String(10), nullable=False)  # 打卡方式（人脸/混合/定位）
    status = db.Column(db.String(20))  #正常、迟到、早退、缺勤等状态

################################################################
# models.py

class LeaveRequest(db.Model):
    __tablename__ = 'leave_requests'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    reason = db.Column(db.String(255))
    status = db.Column(db.String(20), default='待审批')  # 或 '已批准'、'已拒绝'

#############################################################
#外出申请表
class OutingRequest(db.Model):
    __tablename__ = 'outing_requests'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)  # 设置外键
    start_date = db.Column(db.Date, nullable=False)  # 外勤开始日期
    end_date = db.Column(db.Date, nullable=False)    # 外勤结束日期
    location = db.Column(db.String(255), nullable=False)  # 外勤地点
    reason = db.Column(db.String(255), nullable=False)    # 外勤原因
    status = db.Column(db.String(20), default='待审批')    # 状态

##############################################################
#补卡申请表
class MakeupCardRequest(db.Model):
    __tablename__ = 'makeup_card_requests'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)  # 设置外键
    start_date = db.Column(db.Date, nullable=False)  # 补卡开始日期
    end_date = db.Column(db.Date, nullable=False)    # 补卡结束日期
    reason = db.Column(db.String(255), nullable=False)  # 补卡原因
    status = db.Column(db.String(20), default='待审批')  # 状态
    
#################################################################
class AttendanceSettings(db.Model):
    __tablename__ = 'attendance_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    clock_in_method = db.Column(db.String(20))  # 打卡方式: '人脸'、'地点'、'混合'
    clock_in_time = db.Column(db.Time)  # 打卡时间
    clock_in_location = db.Column(db.String(255))  # 打卡地点

    