import request from '@/utils/request'

export function listAlertRule(query) {
  return request({
    url: '/agentsec/rule/list',
    method: 'get',
    params: query
  })
}

export function addAlertRule(data) {
  return request({
    url: '/agentsec/rule',
    method: 'post',
    data
  })
}

export function testAlertRule(ruleId) {
  return request({
    url: '/agentsec/rule/test/' + ruleId,
    method: 'post'
  })
}
