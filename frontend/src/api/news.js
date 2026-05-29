import request from './request'

export function fetchNewsSources() {
  return request.get('/news/sources')
}

export function importNews(data) {
  return request.post('/news/import', data)
}
