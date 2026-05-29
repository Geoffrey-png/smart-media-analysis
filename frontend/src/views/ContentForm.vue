<template>
  <div class="page form-page">
    <section class="page-header form-hero">
      <div>
        <div class="hero-kicker">CONTENT EDITOR</div>
        <h2 class="page-title">{{ isEdit ? '编辑内容' : '新增内容' }}</h2>
        <p class="header-desc">这里不是普通表单，而是内容资产录入和结构化管理入口。</p>
      </div>
      <el-button @click="router.back()">返回</el-button>
    </section>

    <section class="form-layout">
      <article class="form-card card">
        <el-form ref="formRef" :model="form" :rules="rules" label-width="100px" class="content-form">
          <el-form-item label="标题" prop="title">
            <el-input v-model="form.title" placeholder="请输入内容标题" />
          </el-form-item>
          <el-form-item label="作者">
            <el-input v-model="form.author" />
          </el-form-item>
          <el-form-item label="分类">
            <el-select v-model="form.category" placeholder="请选择分类">
              <el-option v-for="item in categories" :key="item.name" :label="item.name" :value="item.name" />
            </el-select>
          </el-form-item>
          <el-form-item label="内容类型">
            <el-radio-group v-model="form.content_type">
              <el-radio-button v-for="item in contentTypes" :key="item.value" :label="item.value">
                {{ item.label }}
              </el-radio-button>
            </el-radio-group>
          </el-form-item>
          <el-form-item label="封面/视频">
            <div class="cover-upload">
              <el-input v-model="form.cover_url" placeholder="输入资源地址，或上传后自动填充" />
              <el-upload :show-file-list="false" :http-request="handleUpload" accept=".jpg,.jpeg,.png,.gif,.webp,.mp4,.mov,.avi">
                <el-button :loading="uploading">上传文件</el-button>
              </el-upload>
            </div>
          </el-form-item>
          <el-form-item label="标签">
            <el-input v-model="tagInput" placeholder="多个标签用逗号分隔，例如 科技,AI,传媒" />
          </el-form-item>
          <el-form-item label="状态">
            <el-select v-model="form.status" style="width: 180px">
              <el-option label="草稿" value="draft" />
              <el-option label="待审核" value="pending" />
              <el-option label="已发布" value="published" />
              <el-option label="已拒绝" value="rejected" />
              <el-option label="已下架" value="offline" />
            </el-select>
          </el-form-item>
          <el-form-item label="摘要">
            <el-input v-model="form.summary" type="textarea" :rows="3" placeholder="可留空，由智能分析生成" />
          </el-form-item>
          <el-form-item label="正文" prop="content">
            <el-input v-model="form.content" type="textarea" :rows="12" placeholder="请输入正文内容" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="submit">保存</el-button>
            <el-button @click="router.back()">取消</el-button>
          </el-form-item>
        </el-form>
      </article>

      <aside class="form-side">
        <div class="tip-card">
          <span class="card-kicker">Checklist</span>
          <h3>录入建议</h3>
          <ul>
            <li>标题要能体现主题，不要只写“今日新闻”这种泛标题。</li>
            <li>标签尽量控制在 3~8 个，便于推荐和检索。</li>
            <li>若有封面图或视频资源，尽量补充，分析效果更完整。</li>
            <li>正文越完整，摘要和关键词提取越准确。</li>
          </ul>
        </div>

        <div class="tip-card stat-card">
          <span class="card-kicker">Status</span>
          <h3>当前内容状态</h3>
          <div class="status-pill">{{ statusLabel(form.status) }}</div>
          <p>保存后可进入智能分析、内容审核和推荐实验流程。</p>
        </div>
      </aside>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { createContent, fetchContent, updateContent } from '../api/content'
import { fetchMetaOptions } from '../api/meta'
import { uploadFile } from '../api/uploads'
import { resolveFileUrl } from '../utils/url'

const route = useRoute()
const router = useRouter()
const formRef = ref()
const tagInput = ref('')
const uploading = ref(false)
const categories = ref([
  { id: 1, name: '科技' },
  { id: 2, name: '财经' },
  { id: 3, name: '体育' },
  { id: 4, name: '娱乐' },
  { id: 5, name: '社会' },
  { id: 6, name: '文化' },
  { id: 7, name: '国际' },
  { id: 8, name: '健康' },
  { id: 9, name: '综合' }
])
const contentTypes = ref([
  { label: '文章', value: 'article' },
  { label: '视频', value: 'video' },
  { label: '图片', value: 'image' }
])
const isEdit = computed(() => Boolean(route.params.id))
const form = reactive({
  title: '',
  summary: '',
  content: '',
  author: '系统编辑',
  category: '综合',
  tags: [],
  cover_url: '',
  content_type: 'article',
  status: 'published'
})
const rules = {
  title: [{ required: true, message: '请输入标题', trigger: 'blur' }],
  content: [{ required: true, message: '请输入正文内容', trigger: 'blur' }]
}

function splitTags(value) {
  return String(value || '')
    .replace(/[，、]/g, ',')
    .split(',')
    .map(item => item.trim())
    .filter(Boolean)
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

async function loadDetail() {
  if (!isEdit.value) return
  const res = await fetchContent(route.params.id)
  Object.assign(form, res.data)
  tagInput.value = (res.data.tags || []).join(',')
  form.status = res.data.status || 'published'
}

async function loadMeta() {
  const res = await fetchMetaOptions()
  const options = res.data || {}
  categories.value = options.categories || categories.value
  contentTypes.value = (options.content_types || contentTypes.value).map(item => ({
    ...item,
    label: {
      article: '文章',
      video: '视频',
      image: '图片'
    }[item.value] || item.label || item.value
  }))
}

async function handleUpload(options) {
  uploading.value = true
  try {
    const res = await uploadFile(options.file)
    form.cover_url = resolveFileUrl(res.data.url)
    ElMessage.success('上传成功')
    options.onSuccess?.(res.data)
  } catch (error) {
    options.onError?.(error)
  } finally {
    uploading.value = false
  }
}

async function submit() {
  await formRef.value.validate()
  const payload = { ...form, tags: splitTags(tagInput.value) }
  if (isEdit.value) {
    await updateContent(route.params.id, payload)
    ElMessage.success('更新成功')
  } else {
    await createContent(payload)
    ElMessage.success('创建成功')
  }
  router.push('/contents')
}

onMounted(() => {
  loadMeta()
  loadDetail()
})
</script>

<style scoped>
.form-page {
  display: grid;
  gap: 20px;
}

.form-hero {
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

.form-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 340px;
  gap: 20px;
}

.form-card,
.tip-card {
  padding: 24px;
}

.content-form :deep(.el-form-item__label) {
  font-weight: 800;
}

.cover-upload {
  display: flex;
  width: 100%;
  gap: 12px;
  align-items: center;
}

.cover-upload :deep(.el-input) {
  flex: 1;
}

.form-side {
  display: grid;
  align-content: start;
  gap: 16px;
}

.tip-card {
  border: 1px solid var(--line);
  border-radius: 24px;
  background:
    linear-gradient(135deg, rgba(255, 255, 255, 0.96), rgba(239, 246, 255, 0.68)),
    radial-gradient(circle at top right, rgba(14, 165, 233, 0.12), transparent 42%);
  box-shadow: var(--shadow-card);
}

.tip-card h3 {
  margin: 6px 0 12px;
  font-size: 20px;
  font-weight: 900;
}

.tip-card ul {
  margin: 0;
  padding-left: 18px;
  color: #64748b;
  line-height: 1.8;
}

.status-pill {
  display: inline-flex;
  align-items: center;
  margin: 10px 0 12px;
  padding: 8px 12px;
  color: #2563eb;
  border-radius: 999px;
  background: rgba(219, 234, 254, 0.86);
  font-weight: 900;
}

.stat-card p {
  margin: 0;
  color: #64748b;
  line-height: 1.7;
}

@media (max-width: 1280px) {
  .form-layout {
    grid-template-columns: 1fr;
  }
}
</style>
