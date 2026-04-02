import request from '@/utils/request'

export function listAgentApp(query) {
  return request({
    url: '/agentsec/app/list',
    method: 'get',
    params: query
  })
}

export function getAgentApp(appId) {
  return request({
    url: '/agentsec/app/' + appId,
    method: 'get'
  })
}

export function addAgentApp(data) {
  return request({
    url: '/agentsec/app',
    method: 'post',
    data
  })
}

export function updateAgentConfig(appId, data) {
  return request({
    url: '/agentsec/app/config/' + appId,
    method: 'put',
    data
  })
}
