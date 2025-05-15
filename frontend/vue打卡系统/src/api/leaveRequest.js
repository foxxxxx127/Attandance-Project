// src/api/leave.js
import request from '@/utils/request'

export function submitLeaveRequest(data) {
  return request({
    url: '/employee/leaveRequest',
    method: 'post',
    data
  })
}
