import request from '@/utils/request'

export function createBlock(data) {
  return request({
    url: '/agentsec/block',
    method: 'post',
    data
  })
}

export function listBlockLog(query) {
  return request({
    url: '/agentsec/blockLog/list',
    method: 'get',
    params: query
  })
}
