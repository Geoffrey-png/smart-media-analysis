export function resolveFileUrl(url) {
  if (!url) return ''
  if (/^https?:\/\//i.test(url)) return url
  const backendBase = import.meta.env.VITE_BACKEND_BASE_URL || 'http://localhost:8000'
  if (url.startsWith('/uploads/')) {
    return `${backendBase}${url}`
  }
  return url
}

