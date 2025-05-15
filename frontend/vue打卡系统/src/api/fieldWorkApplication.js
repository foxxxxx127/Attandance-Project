import request from '@/utils/request'

export function submitFieldWorkApplication(data) {
  return request({
    url: '/employee/outingRequest',
    method: 'post',
    data
  })
}