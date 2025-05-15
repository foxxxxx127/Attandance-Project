import request from '@/utils/request'

export function cardApplicationService(data) {
  return request({
    url: '/employee/makeupCardRequest',
    method: 'post',
    data
  })
}