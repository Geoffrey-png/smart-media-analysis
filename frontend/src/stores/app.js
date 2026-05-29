import { defineStore } from 'pinia'

export const useAppStore = defineStore('app', {
  state: () => ({
    systemName: '智能传媒内容分析与推荐系统'
  })
})

