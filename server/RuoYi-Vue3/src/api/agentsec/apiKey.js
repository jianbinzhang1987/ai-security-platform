import request from '@/utils/request'

export function listApiKey(query) {
  return request({
    url: '/agentsec/apiKey/list',
    method: 'get',
    params: query
  })
}
