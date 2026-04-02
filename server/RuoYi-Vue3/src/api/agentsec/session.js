import request from '@/utils/request'

export function listSession(query) {
  return request({
    url: '/agentsec/session/list',
    method: 'get',
    params: query
  })
}

export function getSession(sessionId) {
  return request({
    url: '/agentsec/session/' + sessionId,
    method: 'get'
  })
}
