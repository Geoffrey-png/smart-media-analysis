<template>
  <div class="page reco-page">
    <section class="page-header reco-hero">
      <div>
        <div class="hero-kicker">RECOMMENDATION STUDIO</div>
        <h2 class="page-title">推荐实验</h2>
        <p class="header-desc">根据用户画像、内容热度和行为反馈生成推荐。普通用户只能查看自己的推荐。</p>
      </div>
      <el-button type="primary" size="large" :loading="loading" @click="loadRecommendations">刷新推荐</el-button>
    </section>

    <section class="studio-card card">
      <div class="toolbar studio-toolbar">
        <el-select v-if="canSelectUser" v-model="selectedUserId" placeholder="选择用户画像" style="width: 280px" clearable>
          <el-option v-for="user in users" :key="user.id" :label="`${user.nickname || user.username}（ID:${user.id}）`" :value="user.id" />
        </el-select>
        <div v-else class="self-user">当前用户：{{ auth.user?.nickname || auth.user?.username }}</div>
        <el-segmented v-model="mode" :options="modeOptions" />
        <el-button type="primary" @click="loadRecommendations">生成推荐</el-button>
      </div>

      <div class="mode-panel">
        <div>
          <span class="card-kicker">Current Strategy</span>
          <h3>{{ currentMode.label }}</h3>
          <p>{{ currentMode.desc }}</p>
        </div>
        <div class="result-count">
          <strong>{{ recommendations.length }}</strong>
          <span>条推荐结果</span>
        </div>
      </div>

      <div v-loading="loading" class="recommend-grid">
        <article v-for="item in recommendations" :key="item.id" class="recommend-card">
          <div class="recommend-head">
            <el-tag effect="light">{{ item.category || '未分类' }}</el-tag>
            <span>{{ Number(item.recommend_score || 0).toFixed(1) }}</span>
          </div>
          <h3>{{ item.title || '未命名内容' }}</h3>
          <p>{{ item.reason || '根据内容热度、标签相似度和用户画像综合推荐' }}</p>
          <div class="tag-list">
            <el-tag v-for="tag in (item.tags || []).slice(0, 4)" :key="tag" size="small">{{ tag }}</el-tag>
          </div>
          <div class="recommend-footer">
            <div>
              <strong>{{ Number(item.heat_score || 0).toFixed(1) }}</strong>
              <span>热度</span>
            </div>
            <div>
              <strong>{{ Number(item.quality_score || 0).toFixed(1) }}</strong>
              <span>质量</span>
            </div>
            <el-button type="primary" text @click="openContent(item)">查看</el-button>
          </div>
        </article>
      </div>

      <el-empty v-if="!loading && !recommendations.length" description="暂无推荐结果，请先浏览或点赞一些内容" />
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { fetchUsers } from '../api/users'
import {
  fetchHotRecommendations,
  fetchMixedRecommendations,
  fetchUserRecommendations,
  recordRecommendationClick
} from '../api/recommendations'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const auth = useAuthStore()
const users = ref([])
const selectedUserId = ref(null)
const mode = ref('user')
const recommendations = ref([])
const loading = ref(false)

const canSelectUser = computed(() => ['admin', 'editor'].includes(auth.user?.role))
const currentUserId = computed(() => selectedUserId.value || auth.user?.id)

const modeOptions = [
  { label: '个性化', value: 'user' },
  { label: '热门', value: 'hot' },
  { label: '综合', value: 'mixed' }
]

const modeMeta = {
  user: { label: '个性化推荐', desc: '根据用户行为画像与内容标签匹配，验证画像驱动推荐链路。' },
  hot: { label: '热门推荐', desc: '优先展示热度高、互动强的内容，适合冷启动或首页流量位。' },
  mixed: { label: '综合推荐', desc: '融合用户兴趣、内容质量、热度与多样性，适合主推荐流。' }
}

const currentMode = computed(() => modeMeta[mode.value] || modeMeta.user)

async function loadUsers() {
  if (!auth.user) {
    await auth.loadCurrentUser().catch(() => {})
  }
  if (!canSelectUser.value) {
    selectedUserId.value = auth.user?.id || null
    return
  }
  const res = await fetchUsers({ page: 1, page_size: 100 })
  users.value = res.data?.items || []
  selectedUserId.value = users.value[0]?.id || auth.user?.id || null
}

async function loadRecommendations() {
  loading.value = true
  try {
    let res
    if (mode.value === 'hot') {
      res = await fetchHotRecommendations(20)
    } else if (mode.value === 'mixed') {
      res = await fetchMixedRecommendations({ user_id: currentUserId.value, limit: 20 })
    } else {
      if (!currentUserId.value) {
        ElMessage.warning('请先登录')
        recommendations.value = []
        return
      }
      res = await fetchUserRecommendations(currentUserId.value, 20)
    }
    recommendations.value = res.data || []
  } finally {
    loading.value = false
  }
}

async function openContent(row) {
  await recordRecommendationClick({
    user_id: currentUserId.value,
    content_id: row.id,
    scene: mode.value,
    recommend_score: row.recommend_score || 0,
    reason: row.reason || ''
  })
  router.push(`/contents/${row.id}`)
}

onMounted(async () => {
  await loadUsers()
  await loadRecommendations()
})
</script>

<style scoped>
.reco-page {
  display: grid;
  gap: 20px;
}

.reco-hero {
  align-items: center;
}

.hero-kicker,
.card-kicker {
  color: #2563eb;
  font-size: 11px;
  font-weight: 900;
  letter-spacing: 0.14em;
}

.header-desc {
  max-width: 760px;
  margin: 9px 0 0;
  color: #64748b;
  line-height: 1.7;
}

.studio-card {
  padding: 22px;
}

.studio-toolbar {
  margin: 0 0 18px;
  padding: 0;
  border: 0;
  background: transparent;
  box-shadow: none;
}

.self-user {
  height: 40px;
  display: inline-flex;
  align-items: center;
  padding: 0 14px;
  border-radius: 14px;
  background: #f1f5f9;
  color: #475569;
  font-weight: 800;
}

.mode-panel {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  margin-bottom: 20px;
  padding: 22px;
  border: 1px solid rgba(226, 232, 240, 0.9);
  border-radius: 24px;
  background:
    linear-gradient(135deg, rgba(239, 246, 255, 0.9), rgba(255, 255, 255, 0.78)),
    radial-gradient(circle at right, rgba(14, 165, 233, 0.12), transparent 38%);
}

.mode-panel h3 {
  margin: 6px 0 7px;
  font-size: 22px;
  font-weight: 950;
}

.mode-panel p {
  margin: 0;
  color: #64748b;
  line-height: 1.7;
}

.result-count {
  min-width: 130px;
  padding: 16px;
  text-align: center;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.75);
}

.result-count strong,
.result-count span {
  display: block;
}

.result-count strong {
  color: #2563eb;
  font-size: 34px;
  font-weight: 950;
}

.result-count span {
  color: #94a3b8;
  font-size: 12px;
}

.recommend-grid {
  min-height: 240px;
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
}

.recommend-card {
  display: flex;
  min-height: 250px;
  flex-direction: column;
  padding: 18px;
  border: 1px solid rgba(226, 232, 240, 0.9);
  border-radius: 24px;
  background:
    linear-gradient(135deg, rgba(255, 255, 255, 0.96), rgba(248, 250, 252, 0.82)),
    radial-gradient(circle at top right, rgba(37, 99, 235, 0.1), transparent 42%);
}

.recommend-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.recommend-head span {
  color: #2563eb;
  font-size: 22px;
  font-weight: 950;
}

.recommend-card h3 {
  margin: 16px 0 9px;
  color: #0f172a;
  font-size: 16px;
  line-height: 1.45;
}

.recommend-card p {
  min-height: 44px;
  margin: 0 0 12px;
  color: #64748b;
  font-size: 13px;
  line-height: 1.65;
}

.recommend-footer {
  display: grid;
  grid-template-columns: 1fr 1fr auto;
  gap: 10px;
  align-items: center;
  margin-top: auto;
  padding-top: 16px;
}

.recommend-footer div {
  padding: 10px;
  border-radius: 14px;
  background: #f8fafc;
}

.recommend-footer strong,
.recommend-footer span {
  display: block;
}

.recommend-footer strong {
  color: #0f172a;
  font-weight: 950;
}

.recommend-footer span {
  margin-top: 3px;
  color: #94a3b8;
  font-size: 12px;
}

@media (max-width: 1480px) {
  .recommend-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (max-width: 1180px) {
  .recommend-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
