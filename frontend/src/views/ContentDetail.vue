<template>
  <div class="page detail-page">
    <section class="page-header detail-hero">
      <div>
        <div class="hero-kicker">CONTENT DETAIL</div>
        <h2 class="page-title">内容详情</h2>
        <p class="header-desc">查看单篇内容的正文、摘要、标签、互动数据和审核信息。</p>
      </div>
      <div class="hero-actions">
        <el-button type="primary" :loading="likeLoading" @click="recordLike">点赞并更新画像</el-button>
        <el-button type="success" @click="handleAnalyze">智能分析</el-button>
        <el-button @click="router.push(`/contents/${route.params.id}/edit`)">编辑</el-button>
        <el-button @click="router.back()">返回</el-button>
      </div>
    </section>

    <section v-if="detail" class="detail-layout">
      <article class="article-card card">
        <div class="article-meta">
          <el-tag :type="statusType(detail.status)">{{ statusLabel(detail.status) }}</el-tag>
          <span>{{ detail.author || '未知作者' }}</span>
          <span>{{ detail.category || '未分类' }}</span>
          <span>{{ formatTime(detail.publish_time) }}</span>
          <a v-if="detail.source_url" :href="detail.source_url" target="_blank" rel="noreferrer">
            来源：{{ detail.source_name || '原文' }}
          </a>
        </div>

        <h1>{{ detail.title }}</h1>
        <div class="tag-list article-tags">
          <el-tag v-for="tag in detail.tags" :key="tag">{{ tag }}</el-tag>
        </div>

        <el-image v-if="detail.cover_url" :src="resolveFileUrl(detail.cover_url)" fit="cover" class="cover" />

        <div class="summary-box">
          <span>自动摘要</span>
          <p>{{ detail.summary || '暂无摘要' }}</p>
        </div>

        <div class="content-block">
          <span>正文内容</span>
          <p>{{ detail.content }}</p>
        </div>
      </article>

      <aside class="side-metrics">
        <div class="metric-card">
          <span>浏览</span>
          <strong>{{ formatNumber(detail.view_count || 0) }}</strong>
        </div>
        <div class="metric-card">
          <span>点赞</span>
          <strong>{{ formatNumber(detail.like_count || 0) }}</strong>
        </div>
        <div class="metric-card">
          <span>收藏</span>
          <strong>{{ formatNumber(detail.favorite_count || 0) }}</strong>
        </div>
        <div class="metric-card">
          <span>评论</span>
          <strong>{{ formatNumber(detail.comment_count || 0) }}</strong>
        </div>

        <div class="score-card card">
          <div class="card-head">
            <span class="card-kicker">Scores</span>
            <h3>分析评分</h3>
          </div>
          <div class="score-item">
            <span>热度分</span>
            <strong>{{ Number(detail.heat_score || 0).toFixed(1) }}</strong>
          </div>
          <div class="score-item">
            <span>质量分</span>
            <strong>{{ Number(detail.quality_score || 0).toFixed(1) }}</strong>
          </div>
          <div class="score-item">
            <span>情感</span>
            <strong>{{ sentimentLabel(detail.sentiment) }}</strong>
          </div>
          <div class="score-item">
            <span>类型</span>
            <strong>{{ contentTypeLabel(detail.content_type) }}</strong>
          </div>
        </div>

        <div class="audit-info card">
          <div class="card-head">
            <span class="card-kicker">Review</span>
            <h3>审核信息</h3>
          </div>
          <p><b>审核人：</b>{{ detail.auditor || '-' }}</p>
          <p><b>审核意见：</b>{{ detail.audit_comment || '-' }}</p>
          <p><b>敏感词：</b>{{ (detail.sensitive_words || []).join('、') || '-' }}</p>
        </div>
      </aside>
    </section>

    <el-empty v-else description="正在加载内容详情" />
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { analyzeContent, fetchContent } from '../api/content'
import { createBehavior } from '../api/behaviors'
import { useAuthStore } from '../stores/auth'
import { resolveFileUrl } from '../utils/url'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const detail = ref(null)
const likeLoading = ref(false)
const viewRecorded = ref(false)

function formatTime(value) {
  return value ? value.replace('T', ' ').slice(0, 19) : ''
}

function formatNumber(value) {
  return Number(value || 0).toLocaleString('zh-CN')
}

function statusLabel(value) {
  return {
    draft: '草稿',
    pending: '待审核',
    published: '已发布',
    rejected: '已拒绝',
    offline: '已下架'
  }[value] || value || '未知'
}

function statusType(value) {
  return {
    draft: 'info',
    pending: 'warning',
    published: 'success',
    rejected: 'danger',
    offline: 'info'
  }[value] || 'info'
}

function sentimentLabel(value) {
  return {
    positive: '正向',
    negative: '负向',
    neutral: '中性'
  }[value] || value || '未知'
}

function contentTypeLabel(value) {
  return {
    article: '文章',
    video: '视频',
    image: '图片'
  }[value] || value || '内容'
}

async function loadDetail() {
  const res = await fetchContent(route.params.id)
  detail.value = res.data
}

async function recordBehavior(actionType, duration = 0) {
  if (!auth.user?.id) {
    await auth.loadCurrentUser().catch(() => {})
  }
  if (!auth.user?.id) return
  const res = await createBehavior({
    user_id: auth.user.id,
    content_id: Number(route.params.id),
    action_type: actionType,
    duration
  })
  if (res.data?.profile?.interest_tags?.length) {
    auth.loadCurrentUser().catch(() => {})
  }
}

async function recordView() {
  if (viewRecorded.value) return
  viewRecorded.value = true
  await recordBehavior('view', 30).catch(() => {})
  await loadDetail()
}

async function recordLike() {
  likeLoading.value = true
  try {
    await recordBehavior('like', 0)
    ElMessage.success('已点赞，用户画像已更新')
    await loadDetail()
  } finally {
    likeLoading.value = false
  }
}

async function handleAnalyze() {
  await analyzeContent(route.params.id)
  ElMessage.success('分析完成')
  loadDetail()
}

onMounted(async () => {
  await loadDetail()
  await recordView()
})
</script>

<style scoped>
.detail-page {
  display: grid;
  gap: 20px;
}

.detail-hero {
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

.hero-actions {
  display: flex;
  gap: 10px;
}

.detail-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 340px;
  gap: 20px;
}

.article-card,
.score-card,
.audit-info {
  padding: 24px;
}

.article-meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 10px;
  color: #64748b;
  font-size: 13px;
}

.article-card h1 {
  margin: 22px 0 14px;
  color: #0f172a;
  font-size: 34px;
  line-height: 1.22;
  font-weight: 950;
  letter-spacing: -0.05em;
}

.article-tags {
  margin-bottom: 18px;
}

.cover {
  width: 100%;
  max-height: 420px;
  border-radius: 24px;
}

.summary-box,
.content-block {
  margin-top: 20px;
  padding: 20px;
  border: 1px solid rgba(226, 232, 240, 0.9);
  border-radius: 22px;
  background: rgba(248, 250, 252, 0.72);
}

.summary-box span,
.content-block span {
  color: #2563eb;
  font-size: 13px;
  font-weight: 900;
}

.summary-box p,
.content-block p {
  margin: 10px 0 0;
  color: #475569;
  line-height: 1.9;
  white-space: pre-wrap;
}

.side-metrics {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  align-content: start;
  gap: 14px;
}

.metric-card {
  padding: 18px;
  border: 1px solid var(--line);
  border-radius: 22px;
  background:
    linear-gradient(135deg, rgba(255, 255, 255, 0.96), rgba(239, 246, 255, 0.68)),
    radial-gradient(circle at right top, rgba(14, 165, 233, 0.12), transparent 42%);
  box-shadow: var(--shadow-card);
}

.metric-card span,
.metric-card strong {
  display: block;
}

.metric-card span {
  color: #64748b;
  font-size: 13px;
}

.metric-card strong {
  margin-top: 8px;
  color: #0f172a;
  font-size: 28px;
  font-weight: 950;
}

.score-card,
.audit-info {
  grid-column: 1 / -1;
}

.card-head {
  margin-bottom: 14px;
}

.card-head h3 {
  margin: 5px 0 0;
  font-size: 19px;
  font-weight: 900;
}

.score-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 12px 0;
  border-bottom: 1px solid rgba(226, 232, 240, 0.86);
}

.score-item:last-child {
  border-bottom: 0;
}

.score-item span,
.audit-info p {
  color: #64748b;
}

.score-item strong {
  color: #0f172a;
}

.audit-info p {
  margin: 10px 0 0;
  line-height: 1.65;
}

@media (max-width: 1280px) {
  .detail-layout {
    grid-template-columns: 1fr;
  }
}
</style>
