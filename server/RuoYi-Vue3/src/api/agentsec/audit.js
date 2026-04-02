import request from '@/utils/request'

export function listAudit(query) {
  return request({
    url: '/agentsec/audit/list',
    method: 'get',
    params: query
  })
}
