<template>
  <div class="page analysis-page">
    <section class="page-header analysis-hero">
      <div>
        <div class="hero-kicker">AI CONTENT LAB</div>
        <h2 class="page-title">智能内容分析</h2>
        <p class="header-desc">模拟 AI 对内容进行分类、关键词抽取、摘要生成、情感识别、质量和热度评分。</p>
      </div>
      <el-button type="primary" size="large" :disabled="!selectedContentId" :loading="loading" @click="runAnalysis">
        开始分析
      </el-button>
    </section>

    <section class="analysis-layout">
      <article class="selector-card card">
        <div class="card-head">
          <span class="card-kicker">Select Content</span>
          <h3>选择待分析内容</h3>
        </div>
        <el-select
          v-model="selectedContentId"
          filterable
          placeholder="请选择需要分析的内容"
          style="width: 100%"
          @change="loadDetail"
        >
          <el-option v-for="item in contents" :key="item.id" :label="`${item.title}（ID:${item.id}）`" :value="item.id" />
        </el-select>

        <div v-if="detail" class="content-preview">
          <div class="preview-top">
            <el-tag type="primary" effect="light">{{ detail.category || '未分类' }}</el-tag>
            <span>{{ detail.author || '未知作者' }}</span>
          </div>
          <h3>{{ detail.title }}</h3>
          <p>{{ detail.summary || (detail.content || '').slice(0, 180) || '暂无摘要' }}</p>
          <div class="tag-list">
            <el-tag v-for="tag in detail.tags" :key="tag" size="small">{{ tag }}</el-tag>
          </div>
        </div>

        <el-empty v-else description="暂无可分析内容" />
      </article>

      <article class="result-card card">
        <div class="card-head between">
          <div>
            <span class="card-kicker">Analysis Result</span>
            <h3>分析结果</h3>
          </div>
          <el-tag v-if="detail" :type="sentimentType(detail.sentiment)">{{ sentimentLabel(detail.sentiment) }}</el-tag>
        </div>

        <el-empty v-if="!detail" description="请选择内容后执行分析" />
        <template v-else>
          <div class="score-board">
            <div class="score-orb blue">
              <el-progress type="circle" :width="116" :stroke-width="10" :percentage="normalizeScore(detail.quality_score)" />
              <strong>内容质量</strong>
            </div>
            <div class="score-orb purple">
              <el-progress type="circle" :width="116" :stroke-width="10" :percentage="normalizeScore(detail.heat_score)" color="#8b5cf6" />
              <strong>传播热度</strong>
            </div>
            <div class="score-panel">
              <div>
                <span>内容类型</span>
                <strong>{{ contentTypeLabel(detail.content_type) }}</strong>
              </div>
              <div>
                <span>浏览量</span>
                <strong>{{ formatNumber(detail.view_count || 0) }}</strong>
              </div>
              <div>
                <span>点赞量</span>
                <strong>{{ formatNumber(detail.like_count || 0) }}</strong>
              </div>
            </div>
          </div>

          <div class="summary-block">
            <span class="block-title">自动摘要</span>
            <p>{{ detail.summary || '暂无摘要' }}</p>
          </div>

          <div class="summary-block">
            <span class="block-title">关键词 / 标签</span>
            <div class="tag-list strong-tags">
              <el-tag v-for="tag in detail.tags" :key="tag" type="success">{{ tag }}</el-tag>
            </div>
          </div>
        </template>
      </article>
    </section>

    <section class="similar-card card">
      <div class="card-head between">
        <div>
          <span class="card-kicker">Similar Content</span>
          <h3>相似内容推荐</h3>
        </div>
        <span class="muted">基于标签、分类和文本特征的规则推荐</span>
      </div>

      <div v-if="similarContents.length" class="similar-grid">
        <article v-for="item in similarContents" :key="item.id" class="similar-item">
          <div class="similar-score">{{ Number(item.recommend_score || 0).toFixed(1) }}</div>
          <div class="similar-main">
            <h4>{{ item.title }}</h4>
            <p>{{ item.reason || '标签或分类相似' }}</p>
            <div>
              <el-tag size="small">{{ item.category || '未分类' }}</el-tag>
            </div>
          </div>
        </article>
      </div>
      <el-empty v-else description="暂无相似内容推荐" />
    </section>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { analyzeContent, fetchContent, fetchContents } from '../api/content'
import { fetchContentRecommendations } from '../api/recommendations'

const loading = ref(false)
const contents = ref([])
const selectedContentId = ref(null)
const detail = ref(null)
const similarContents = ref([])

function sentimentType(value) {
  return value === 'positive' ? 'success' : value === 'negative' ? 'danger' : 'info'
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

function formatNumber(value) {
  return Number(value || 0).toLocaleString('zh-CN')
}

function normalizeScore(value) {
  const num = Number(value || 0)
  return Math.max(0, Math.min(100, Math.round(num)))
}

async function loadContents() {
  const res = await fetchContents({ page: 1, page_size: 100 })
  contents.value = res.data?.items || []
  if (!selectedContentId.value && contents.value.length) {
    selectedContentId.value = contents.value[0].id
    await loadDetail()
  }
}

async function loadDetail() {
  if (!selectedContentId.value) return
  const res = await fetchContent(selectedContentId.value)
  detail.value = res.data
  await loadSimilar()
}

async function loadSimilar() {
  if (!selectedContentId.value) return
  const res = await fetchContentRecommendations(selectedContentId.value, 8)
  similarContents.value = res.data || []
}

async function runAnalysis() {
  loading.value = true
  try {
    const res = await analyzeContent(selectedContentId.value)
    detail.value = res.data
    await loadSimilar()
    ElMessage.success('智能分析完成')
  } finally {
    loading.value = false
  }
}

onMounted(loadContents)
</script>

<style scoped>
.analysis-page {
  display: grid;
  gap: 20px;
}

.analysis-hero {
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

.analysis-layout {
  display: grid;
  grid-template-columns: 390px minmax(0, 1fr);
  gap: 20px;
}

.selector-card,
.result-card,
.similar-card {
  padding: 22px;
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
  margin: 5px 0 0;
  font-size: 20px;
  font-weight: 900;
}

.content-preview {
  margin-top: 20px;
  padding: 18px;
  border: 1px solid rgba(226, 232, 240, 0.9);
  border-radius: 22px;
  background:
    linear-gradient(135deg, rgba(255, 255, 255, 0.96), rgba(239, 246, 255, 0.7)),
    radial-gradient(circle at top right, rgba(37, 99, 235, 0.1), transparent 40%);
}

.preview-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  color: #94a3b8;
  font-size: 12px;
}

.content-preview h3 {
  margin: 16px 0 9px;
  color: #0f172a;
  line-height: 1.45;
}

.content-preview p {
  color: #64748b;
  line-height: 1.75;
}

.score-board {
  display: grid;
  grid-template-columns: 150px 150px minmax(0, 1fr);
  gap: 18px;
  align-items: stretch;
}

.score-orb,
.score-panel {
  padding: 18px;
  border: 1px solid rgba(226, 232, 240, 0.9);
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.7);
}

.score-orb {
  display: grid;
  justify-items: center;
  gap: 10px;
}

.score-orb strong {
  color: #0f172a;
  font-size: 14px;
}

.score-panel {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.score-panel div {
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 14px;
  border-radius: 18px;
  background: #f8fafc;
}

.score-panel span {
  color: #94a3b8;
  font-size: 12px;
}

.score-panel strong {
  margin-top: 8px;
  color: #0f172a;
  font-size: 22px;
  font-weight: 950;
}

.summary-block {
  margin-top: 18px;
  padding: 18px;
  border: 1px solid rgba(226, 232, 240, 0.9);
  border-radius: 22px;
  background: rgba(248, 250, 252, 0.72);
}

.block-title {
  color: #2563eb;
  font-size: 13px;
  font-weight: 900;
}

.summary-block p {
  margin: 10px 0 0;
  color: #475569;
  line-height: 1.8;
}

.strong-tags {
  margin-top: 12px;
}

.similar-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px;
}

.similar-item {
  display: grid;
  grid-template-columns: 52px minmax(0, 1fr);
  gap: 12px;
  padding: 16px;
  border: 1px solid rgba(226, 232, 240, 0.9);
  border-radius: 22px;
  background: rgba(255, 255, 255, 0.72);
}

.similar-score {
  width: 52px;
  height: 52px;
  display: grid;
  place-items: center;
  color: #fff;
  border-radius: 18px;
  background: linear-gradient(135deg, #2563eb, #06b6d4);
  font-weight: 950;
}

.similar-main {
  min-width: 0;
}

.similar-main h4 {
  overflow: hidden;
  margin: 0;
  color: #0f172a;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 14px;
}

.similar-main p {
  height: 36px;
  overflow: hidden;
  margin: 7px 0 10px;
  color: #64748b;
  font-size: 12px;
  line-height: 1.5;
}

@media (max-width: 1280px) {
  .analysis-layout {
    grid-template-columns: 1fr;
  }

  .similar-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
