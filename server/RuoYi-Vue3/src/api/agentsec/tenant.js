import request from '@/utils/request'

export function listTenant(query) {
  return request({
    url: '/agentsec/tenant/list',
    method: 'get',
    params: query
  })
}
