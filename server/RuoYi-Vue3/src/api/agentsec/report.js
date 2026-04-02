import request from '@/utils/request'

export function listSecurityReport(query) {
  return request({
    url: '/agentsec/report/list',
    method: 'get',
    params: query
  })
}

export function createSecurityReport(data) {
  return request({
    url: '/agentsec/report',
    method: 'post',
    data
  })
}
