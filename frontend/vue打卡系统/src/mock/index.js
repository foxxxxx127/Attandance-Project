import Mock from 'mockjs'
Mock.mock('http://localhost:8080/login', {
    "code": 0,      // ← 直接返回 code，去掉外层 ret 和 data
    "message": "补卡请求提交成功",
    "userId":"张三"
})