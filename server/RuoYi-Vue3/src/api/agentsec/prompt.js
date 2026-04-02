import request from '@/utils/request'

export function listPrompt(query) {
  return request({
    url: '/agentsec/prompt/list',
    method: 'get',
    params: query
  })
}

export function searchPrompt(data) {
  return request({
    url: '/agentsec/prompt/search',
    method: 'post',
    data
  })
}
