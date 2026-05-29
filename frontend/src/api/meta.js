import request from './request'

export function fetchCategories() {
  return request.get('/meta/categories')
}

export function fetchTags() {
  return request.get('/meta/tags')
}

export function fetchMetaOptions() {
  return request.get('/meta/options')
}

