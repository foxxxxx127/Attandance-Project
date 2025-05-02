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


    #关系定义
    attendances = db.relationship('Attendance', backref='employee', lazy=True)
    leave_requests = db.relationship('LeaveRequest', backref='employee', lazy=True)  
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
    leave_type = db.Column(db.String(20), nullable=False)  # 如：病假、事假
    reason = db.Column(db.String(255))
    status = db.Column(db.String(20), default='待审批')  # 或 '已批准'、'已拒绝'

