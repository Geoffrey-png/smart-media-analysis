<template>
  <div class="page behavior-page">
    <section class="page-header behavior-hero">
      <div>
        <div class="hero-kicker">USER BEHAVIOR STREAM</div>
        <h2 class="page-title">行为流</h2>
        <p class="header-desc">记录用户浏览、点赞、收藏、评论、分享等行为，为画像和推荐效果分析提供数据来源。</p>
      </div>
      <el-button type="primary" size="large" @click="dialogVisible = true">记录行为</el-button>
    </section>

    <section class="behavior-card card">
      <div class="toolbar behavior-toolbar">
        <el-input-number v-model="filters.user_id" :min="0" placeholder="用户ID" />
        <el-input-number v-model="filters.content_id" :min="0" placeholder="内容ID" />
        <el-select v-model="filters.action_type" placeholder="行为类型" clearable style="width: 150px">
          <el-option v-for="item in actions" :key="item" :label="actionLabel(item)" :value="item" />
        </el-select>
        <el-button type="primary" @click="loadData">查询</el-button>
        <el-button @click="reset">重置</el-button>
      </div>

      <div class="stream-summary">
        <div v-for="item in actionStats" :key="item.action" class="stream-stat">
          <span>{{ actionLabel(item.action) }}</span>
          <strong>{{ item.count }}</strong>
        </div>
      </div>

      <div class="table-head">
        <div>
          <span class="card-kicker">Behavior Records</span>
          <h3>行为明细</h3>
        </div>
        <span class="muted">当前展示 {{ tableData.length }} 条</span>
      </div>

      <el-table :data="tableData">
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="user_id" label="用户ID" width="110" />
        <el-table-column prop="content_id" label="内容ID" width="110" />
        <el-table-column label="行为" width="130">
          <template #default="{ row }">
            <el-tag :type="actionType(row.action_type)" size="small">{{ actionLabel(row.action_type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="停留时间" width="120">
          <template #default="{ row }">{{ row.duration || 0 }} 秒</template>
        </el-table-column>
        <el-table-column label="时间" min-width="180">
          <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
        </el-table-column>
      </el-table>
    </section>

    <el-dialog v-model="dialogVisible" title="记录用户行为" width="500px">
      <el-form :model="form" label-width="92px">
        <el-form-item label="用户ID"><el-input-number v-model="form.user_id" :min="1" /></el-form-item>
        <el-form-item label="内容ID"><el-input-number v-model="form.content_id" :min="1" /></el-form-item>
        <el-form-item label="行为">
          <el-select v-model="form.action_type">
            <el-option v-for="item in actions" :key="item" :label="actionLabel(item)" :value="item" />
          </el-select>
        </el-form-item>
        <el-form-item label="停留秒数"><el-input-number v-model="form.duration" :min="0" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { createBehavior, fetchBehaviors } from '../api/behaviors'

const actions = ['view', 'like', 'favorite', 'comment', 'share', 'dislike']
const tableData = ref([])
const dialogVisible = ref(false)
const filters = reactive({ page: 1, page_size: 50, user_id: null, content_id: null, action_type: '' })
const form = reactive({ user_id: 1, content_id: 1, action_type: 'view', duration: 30 })

const actionStats = computed(() => {
  return actions.map(action => ({
    action,
    count: tableData.value.filter(item => item.action_type === action).length
  }))
})

function actionLabel(value) {
  return {
    view: '浏览',
    like: '点赞',
    favorite: '收藏',
    comment: '评论',
    share: '分享',
    dislike: '不喜欢'
  }[value] || value
}

function actionType(value) {
  return {
    view: 'primary',
    like: 'success',
    favorite: 'warning',
    comment: 'info',
    share: 'success',
    dislike: 'danger'
  }[value] || 'info'
}

function formatTime(value) {
  return value ? value.replace('T', ' ').slice(0, 19) : '-'
}

async function loadData() {
  const params = { ...filters }
  if (!params.user_id) delete params.user_id
  if (!params.content_id) delete params.content_id
  if (!params.action_type) delete params.action_type
  const res = await fetchBehaviors(params)
  tableData.value = res.data?.items || []
}

function reset() {
  filters.user_id = null
  filters.content_id = null
  filters.action_type = ''
  loadData()
}

async function submit() {
  await createBehavior(form)
  ElMessage.success('记录成功')
  dialogVisible.value = false
  loadData()
}

onMounted(loadData)
</script>

<style scoped>
.behavior-page {
  display: grid;
  gap: 20px;
}

.behavior-hero {
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

.behavior-card {
  padding: 22px;
}

.behavior-toolbar {
  margin: 0 0 18px;
  padding: 0;
  border: 0;
  background: transparent;
  box-shadow: none;
}

.stream-summary {
  display: grid;
  grid-template-columns: repeat(6, minmax(0, 1fr));
  gap: 12px;
  margin-bottom: 24px;
}

.stream-stat {
  padding: 16px;
  border: 1px solid rgba(226, 232, 240, 0.9);
  border-radius: 20px;
  background:
    linear-gradient(135deg, rgba(255, 255, 255, 0.96), rgba(239, 246, 255, 0.68)),
    radial-gradient(circle at right top, rgba(14, 165, 233, 0.1), transparent 42%);
}

.stream-stat span,
.stream-stat strong {
  display: block;
}

.stream-stat span {
  color: #64748b;
  font-size: 13px;
}

.stream-stat strong {
  margin-top: 8px;
  color: #0f172a;
  font-size: 28px;
  font-weight: 950;
}

.table-head {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 12px;
}

.table-head h3 {
  margin: 5px 0 0;
  font-size: 19px;
  font-weight: 900;
}

@media (max-width: 1280px) {
  .stream-summary {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}
</style>
