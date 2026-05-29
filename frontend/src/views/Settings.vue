<template>
  <div class="page settings-page">
    <section class="page-header settings-hero">
      <div>
        <div class="hero-kicker">SYSTEM PROFILE</div>
        <h2 class="page-title">系统设置</h2>
        <p class="header-desc">这里展示当前项目技术栈、推荐策略和后续扩展方向，定位为教学实训版。</p>
      </div>
    </section>

    <section class="settings-grid">
      <article class="profile-card card">
        <div class="profile-logo">AI</div>
        <h3>智能传媒内容分析与推荐系统</h3>
        <p>
          当前版本用于实训和演示，重点展示内容分析、用户行为采集、推荐结果生成和效果评估。
        </p>
        <el-alert
          title="当前为教学 / 实训版本：推荐算法为可解释规则 + 用户画像融合，不是生产级深度学习排序系统。"
          type="info"
          show-icon
          :closable="false"
        />
      </article>

      <article class="stack-card card">
        <div class="card-head">
          <span class="card-kicker">Tech Stack</span>
          <h3>技术栈</h3>
        </div>
        <div class="stack-list">
          <div>
            <strong>后端</strong>
            <span>Python FastAPI + SQLAlchemy + SQLite</span>
          </div>
          <div>
            <strong>前端</strong>
            <span>Vue 3 + Vite + Element Plus + ECharts</span>
          </div>
          <div>
            <strong>推荐策略</strong>
            <span>热门推荐、标签匹配、用户画像、相似内容、多样性调整</span>
          </div>
        </div>
      </article>

      <article class="roadmap-card card">
        <div class="card-head">
          <span class="card-kicker">Roadmap</span>
          <h3>后续扩展</h3>
        </div>
        <div class="roadmap-list">
          <div v-for="item in roadmap" :key="item.title" class="roadmap-item">
            <div class="roadmap-index">{{ item.index }}</div>
            <div>
              <strong>{{ item.title }}</strong>
              <p>{{ item.desc }}</p>
            </div>
          </div>
        </div>
      </article>
    </section>
  </div>
</template>

<script setup>
const roadmap = [
  { index: '01', title: '角色权限 RBAC', desc: '区分管理员、编辑、审核员和观察者，避免所有登录用户都有高危操作权限。' },
  { index: '02', title: '搜索与检索增强', desc: '由 SQL LIKE 升级到 SQLite FTS 或 Elasticsearch，提高内容检索体验。' },
  { index: '03', title: '推荐实验体系', desc: '加入曝光去重、推荐批次、A/B 实验和转化漏斗分析。' },
  { index: '04', title: '模型能力升级', desc: '将规则分析替换为真实 NLP 模型或大模型接口，实现更高质量的摘要和标签。' }
]
</script>

<style scoped>
.settings-page {
  display: grid;
  gap: 20px;
}

.settings-hero {
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

.settings-grid {
  display: grid;
  grid-template-columns: 0.9fr 1fr;
  gap: 20px;
}

.profile-card,
.stack-card,
.roadmap-card {
  padding: 24px;
}

.profile-card {
  grid-row: span 2;
  min-height: 430px;
  background:
    radial-gradient(circle at top right, rgba(37, 99, 235, 0.12), transparent 36%),
    linear-gradient(135deg, rgba(255, 255, 255, 0.96), rgba(239, 246, 255, 0.76)) !important;
}

.profile-logo {
  width: 64px;
  height: 64px;
  display: grid;
  place-items: center;
  color: white;
  border-radius: 22px;
  background: linear-gradient(135deg, #22d3ee, #2563eb 56%, #8b5cf6);
  box-shadow: 0 18px 38px rgba(37, 99, 235, 0.28);
  font-weight: 950;
}

.profile-card h3 {
  max-width: 420px;
  margin: 26px 0 14px;
  color: #0f172a;
  font-size: 30px;
  line-height: 1.2;
  font-weight: 950;
  letter-spacing: -0.05em;
}

.profile-card p {
  margin: 0 0 22px;
  color: #64748b;
  line-height: 1.8;
}

.card-head {
  margin-bottom: 16px;
}

.card-head h3 {
  margin: 6px 0 0;
  font-size: 20px;
  font-weight: 900;
}

.stack-list,
.roadmap-list {
  display: grid;
  gap: 14px;
}

.stack-list div,
.roadmap-item {
  padding: 16px;
  border: 1px solid rgba(226, 232, 240, 0.9);
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.72);
}

.stack-list strong,
.stack-list span {
  display: block;
}

.stack-list strong {
  color: #0f172a;
  font-size: 15px;
}

.stack-list span {
  margin-top: 7px;
  color: #64748b;
  line-height: 1.6;
}

.roadmap-item {
  display: grid;
  grid-template-columns: 46px minmax(0, 1fr);
  gap: 14px;
}

.roadmap-index {
  width: 46px;
  height: 46px;
  display: grid;
  place-items: center;
  color: #2563eb;
  border-radius: 16px;
  background: rgba(219, 234, 254, 0.86);
  font-weight: 950;
}

.roadmap-item strong {
  color: #0f172a;
  font-size: 15px;
}

.roadmap-item p {
  margin: 6px 0 0;
  color: #64748b;
  line-height: 1.65;
}

@media (max-width: 1180px) {
  .settings-grid {
    grid-template-columns: 1fr;
  }
}
</style>
