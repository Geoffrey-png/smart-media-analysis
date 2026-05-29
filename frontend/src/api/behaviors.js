import request from './request'

export function fetchBehaviors(params) {
  return request.get('/behaviors', { params })
}

export function createBehavior(data) {
  return request.post('/behaviors', data)
}

