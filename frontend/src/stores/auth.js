import { defineStore } from 'pinia'
import { fetchCurrentUser, loginApi } from '../api/auth'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('smart-media-token') || '',
    user: JSON.parse(localStorage.getItem('smart-media-user') || 'null')
  }),
  actions: {
    async login(username, password) {
      const res = await loginApi({ username, password })
      this.token = res.data.access_token
      this.user = res.data.user
      localStorage.setItem('smart-media-token', this.token)
      localStorage.setItem('smart-media-user', JSON.stringify(this.user))
      return res.data
    },
    async loadCurrentUser() {
      if (!this.token) return null
      const res = await fetchCurrentUser()
      this.user = res.data
      localStorage.setItem('smart-media-user', JSON.stringify(this.user))
      return this.user
    },
    logout() {
      this.token = ''
      this.user = null
      localStorage.removeItem('smart-media-token')
      localStorage.removeItem('smart-media-user')
    }
  }
})

