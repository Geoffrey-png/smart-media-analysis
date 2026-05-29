import request from './request'

export function fetchContents(params) {
  return request.get('/contents', { params })
}

export function fetchContent(id) {
  return request.get(`/contents/${id}`)
}

export function createContent(data) {
  return request.post('/contents', data)
}

export function updateContent(id, data) {
  return request.put(`/contents/${id}`, data)
}

export function deleteContent(id) {
  return request.delete(`/contents/${id}`)
}

export function analyzeContent(id) {
  return request.post(`/contents/${id}/analyze`)
}

export function auditContent(id, data) {
  return request.post(`/contents/${id}/audit`, data)
}

export function fetchPendingContents(params) {
  return request.get('/contents/audit/pending', { params })
}

export function fetchHotContents(limit = 10) {
  return request.get('/contents/hot', { params: { limit } })
}
