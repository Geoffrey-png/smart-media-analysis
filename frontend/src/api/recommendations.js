import request from './request'

export function fetchHotRecommendations(limit = 10) {
  return request.get('/recommendations/hot', { params: { limit } })
}

export function fetchUserRecommendations(userId, limit = 10) {
  return request.get(`/recommendations/user/${userId}`, { params: { limit } })
}

export function fetchContentRecommendations(contentId, limit = 10) {
  return request.get(`/recommendations/content/${contentId}`, { params: { limit } })
}

export function fetchMixedRecommendations(params) {
  return request.get('/recommendations/mixed', { params })
}

export function recordRecommendationClick(data) {
  return request.post('/recommendations/click', data)
}

export function fetchRecommendationAnalytics() {
  return request.get('/recommendations/analytics/summary')
}
