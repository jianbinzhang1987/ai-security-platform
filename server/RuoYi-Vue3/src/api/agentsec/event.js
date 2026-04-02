import request from '@/utils/request'

export function listRiskEvent(query) {
  return request({
    url: '/agentsec/event/list',
    method: 'get',
    params: query
  })
}

export function updateRiskEvent(eventId, data) {
  return request({
    url: '/agentsec/event/' + eventId,
    method: 'put',
    data
  })
}
