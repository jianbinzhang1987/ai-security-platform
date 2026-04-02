import request from '@/utils/request'

export function getDashboardSummary() {
  return request({
    url: '/agentsec/dashboard/summary',
    method: 'get'
  })
}

export function getDashboardTimeseries(params) {
  return request({
    url: '/agentsec/dashboard/timeseries',
    method: 'get',
    params
  })
}
