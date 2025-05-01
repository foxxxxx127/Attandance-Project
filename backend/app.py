from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask import request, jsonify
from werkzeug.security import generate_password_hash

############################################################
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///attandance.db'  # 数据库文件名
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 关闭警告

db = SQLAlchemy(app)  # 创建数据库对象

############################################################
# 定义一个员工表
class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)  # 登录账号
    password = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(50))           # 姓名
    employee_id = db.Column(db.String(20), unique=True)  # 员工编号
    phone = db.Column(db.String(20))          # 手机号
    position = db.Column(db.String(50))       # 职位
    department = db.Column(db.String(50))     # 部门
    role = db.Column(db.String(10))           # 员工/管理员
############################################################
#根目录
@app.route('/')
def index():
    return "数据库连接成功"


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
############################################################

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # 创建所有定义好的表（第一次运行时自动创建）
    app.run(debug=True)



