<template>
  <div class="page profile-page">
    <section class="page-header profile-hero">
      <div>
        <div class="hero-kicker">AUDIENCE INSIGHT</div>
        <h2 class="page-title">用户画像详情</h2>
        <p class="header-desc">查看用户兴趣权重、最近行为和面向该用户的推荐内容。</p>
      </div>
      <el-button @click="router.back()">返回</el-button>
    </section>

    <section v-if="profile.user" class="profile-layout">
      <aside class="profile-side">
        <article class="persona-card card">
          <div class="persona-avatar">{{ avatarText(profile.user) }}</div>
          <h3>{{ profile.user.nickname || profile.user.username }}</h3>
          <p>{{ profile.user.city || '未知城市' }} · {{ profile.user.age || '-' }} 岁</p>
          <div class="persona-meta">
            <div>
              <span>用户名</span>
              <strong>{{ profile.user.username }}</strong>
            </div>
            <div>
              <span>性别</span>
              <strong>{{ genderLabel(profile.user.gender) }}</strong>
            </div>
          </div>
        </article>

        <article class="interest-card card">
          <div class="card-head">
            <span class="card-kicker">Interest Weight</span>
            <h3>兴趣权重</h3>
          </div>
          <div v-for="item in profile.interest_tags" :key="item.tag" class="interest-row">
            <div>
              <span>{{ item.tag }}</span>
              <strong>{{ item.weight }}</strong>
            </div>
            <el-progress :percentage="Math.min(item.weight * 10, 100)" />
          </div>
        </article>
      </aside>

      <main class="profile-main">
        <article class="recommend-card card">
          <div class="card-head between">
            <div>
              <span class="card-kicker">Recommended Contents</span>
              <h3>推荐内容</h3>
            </div>
            <span class="muted">{{ recommendations.length }} 条</span>
          </div>
          <div class="recommend-list">
            <div v-for="item in recommendations" :key="item.id" class="recommend-row">
              <div class="score">{{ Number(item.recommend_score || 0).toFixed(1) }}</div>
              <div class="recommend-main">
                <strong>{{ item.title }}</strong>
                <p>{{ item.reason || '根据用户兴趣和内容标签推荐' }}</p>
              </div>
              <el-tag>{{ item.category || '未分类' }}</el-tag>
            </div>
          </div>
        </article>

        <article class="behavior-card card">
          <div class="card-head between">
            <div>
              <span class="card-kicker">Recent Behaviors</span>
              <h3>最近行为</h3>
            </div>
          </div>
          <el-table :data="profile.recent_contents || []">
            <el-table-column label="行为" width="100">
              <template #default="{ row }">
                <el-tag size="small">{{ actionLabel(row.behavior) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="停留秒数" width="100">
              <template #default="{ row }">{{ row.duration || 0 }}</template>
            </el-table-column>
            <el-table-column label="内容" min-width="240">
              <template #default="{ row }">{{ row.content?.title }}</template>
            </el-table-column>
            <el-table-column label="时间" width="180">
              <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
            </el-table-column>
          </el-table>
        </article>
      </main>
    </section>

    <el-empty v-else description="正在加载用户画像" />
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { fetchUserProfile } from '../api/users'
import { fetchUserRecommendations } from '../api/recommendations'

const route = useRoute()
const router = useRouter()
const profile = ref({})
const recommendations = ref([])

function avatarText(user) {
  return String(user.nickname || user.username || 'U').slice(0, 1).toUpperCase()
}

function genderLabel(value) {
  return {
    male: '男',
    female: '女',
    unknown: '未知'
  }[value] || value || '未知'
}

function actionLabel(value) {
  return {
    view: '浏览',
    like: '点赞',
    favorite: '收藏',
    comment: '评论',
    share: '分享',
    dislike: '不喜欢'
  }[value] || value || '-'
}

function formatTime(value) {
  return value ? value.replace('T', ' ').slice(0, 19) : '-'
}

async function loadData() {
  const [profileRes, recommendRes] = await Promise.all([
    fetchUserProfile(route.params.id),
    fetchUserRecommendations(route.params.id, 10)
  ])
  profile.value = profileRes.data || {}
  recommendations.value = recommendRes.data || []
}

onMounted(loadData)
</script>

<style scoped>
.profile-page {
  display: grid;
  gap: 20px;
}

.profile-hero {
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

.profile-layout {
  display: grid;
  grid-template-columns: 360px minmax(0, 1fr);
  gap: 20px;
}

.profile-side,
.profile-main {
  display: grid;
  align-content: start;
  gap: 20px;
}

.persona-card,
.interest-card,
.recommend-card,
.behavior-card {
  padding: 24px;
}

.persona-card {
  text-align: center;
  background:
    radial-gradient(circle at top right, rgba(37, 99, 235, 0.12), transparent 36%),
    linear-gradient(135deg, rgba(255, 255, 255, 0.96), rgba(239, 246, 255, 0.76)) !important;
}

.persona-avatar {
  width: 78px;
  height: 78px;
  display: grid;
  place-items: center;
  margin: 0 auto;
  color: white;
  border-radius: 28px;
  background: linear-gradient(135deg, #2563eb, #7c3aed);
  font-size: 28px;
  font-weight: 950;
}

.persona-card h3 {
  margin: 18px 0 7px;
  color: #0f172a;
  font-size: 24px;
  font-weight: 950;
}

.persona-card p {
  margin: 0;
  color: #64748b;
}

.persona-meta {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  margin-top: 22px;
}

.persona-meta div {
  padding: 14px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.72);
}

.persona-meta span,
.persona-meta strong {
  display: block;
}

.persona-meta span {
  color: #94a3b8;
  font-size: 12px;
}

.persona-meta strong {
  margin-top: 6px;
  color: #0f172a;
}

.card-head {
  margin-bottom: 16px;
}

.card-head.between {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.card-head h3 {
  margin: 6px 0 0;
  font-size: 20px;
  font-weight: 900;
}

.interest-row {
  margin-bottom: 14px;
}

.interest-row div {
  display: flex;
  justify-content: space-between;
  margin-bottom: 7px;
  color: #475569;
  font-weight: 800;
}

.recommend-list {
  display: grid;
  gap: 12px;
}

.recommend-row {
  display: grid;
  grid-template-columns: 54px minmax(0, 1fr) auto;
  gap: 14px;
  align-items: center;
  padding: 14px;
  border: 1px solid rgba(226, 232, 240, 0.9);
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.72);
}

.score {
  width: 54px;
  height: 54px;
  display: grid;
  place-items: center;
  color: #fff;
  border-radius: 18px;
  background: linear-gradient(135deg, #2563eb, #06b6d4);
  font-weight: 950;
}

.recommend-main {
  min-width: 0;
}

.recommend-main strong {
  display: block;
  overflow: hidden;
  color: #0f172a;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.recommend-main p {
  margin: 6px 0 0;
  color: #64748b;
  font-size: 12px;
}

@media (max-width: 1280px) {
  .profile-layout {
    grid-template-columns: 1fr;
  }
}
</style>
