<template>
  <div class="login-page">
    <section class="login-visual">
      <div class="brand-mark">AI</div>
      <p class="visual-kicker">SMART MEDIA ANALYTICS</p>
      <h1>智能传媒内容分析与推荐系统</h1>
      <p class="visual-desc">
        连接内容理解、用户画像和推荐策略，让传媒运营从“管理后台”升级为“数据分析工作台”。
      </p>
      <div class="visual-grid">
        <div>
          <strong>Content</strong>
          <span>内容热度追踪</span>
        </div>
        <div>
          <strong>Audience</strong>
          <span>兴趣画像识别</span>
        </div>
        <div>
          <strong>Recommend</strong>
          <span>推荐效果评估</span>
        </div>
      </div>
    </section>

    <el-card class="login-card" shadow="never">
      <div class="form-head">
        <span>欢迎回来</span>
        <h2>登录洞察平台</h2>
        <p>使用演示账号进入系统，查看内容分析和推荐效果。</p>
      </div>

      <el-form :model="form" label-position="top" @submit.prevent="login">
        <el-form-item label="账号">
          <el-input v-model="form.username" size="large" placeholder="tech_user" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="form.password" size="large" type="password" placeholder="demo" show-password />
        </el-form-item>
        <el-alert
          class="demo-tip"
          title="演示账号：tech_user / demo；也可使用 finance_user、sports_user、ent_user、life_user。"
          type="info"
          :closable="false"
        />
        <el-button type="primary" size="large" class="login-btn" :loading="loading" @click="login">
          进入分析平台
        </el-button>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const auth = useAuthStore()
const loading = ref(false)
const form = reactive({
  username: 'tech_user',
  password: 'demo'
})

async function login() {
  if (!form.username || !form.password) {
    ElMessage.warning('请输入账号和密码')
    return
  }
  loading.value = true
  try {
    await auth.login(form.username, form.password)
    ElMessage.success('登录成功')
    router.push('/dashboard')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: grid;
  grid-template-columns: minmax(0, 1.1fr) 460px;
  align-items: center;
  gap: 48px;
  padding: 54px min(7vw, 96px);
  background:
    radial-gradient(circle at 18% 14%, rgba(34, 211, 238, 0.28), transparent 28%),
    radial-gradient(circle at 78% 22%, rgba(124, 58, 237, 0.24), transparent 30%),
    linear-gradient(135deg, #061224, #102a5c 56%, #1e1b4b);
}

.login-visual {
  position: relative;
  overflow: hidden;
  min-height: 560px;
  padding: 42px;
  color: #fff;
  border: 1px solid rgba(255, 255, 255, 0.14);
  border-radius: 36px;
  background:
    linear-gradient(rgba(255, 255, 255, 0.06) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.06) 1px, transparent 1px),
    rgba(255, 255, 255, 0.07);
  background-size: 34px 34px;
  box-shadow: 0 30px 90px rgba(0, 0, 0, 0.28);
  backdrop-filter: blur(18px);
}

.login-visual::after {
  content: '';
  position: absolute;
  right: -110px;
  bottom: -130px;
  width: 360px;
  height: 360px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(34, 211, 238, 0.42), transparent 66%);
}

.brand-mark {
  width: 58px;
  height: 58px;
  display: grid;
  place-items: center;
  border-radius: 20px;
  background: linear-gradient(135deg, #22d3ee, #2563eb 56%, #8b5cf6);
  box-shadow: 0 18px 38px rgba(37, 99, 235, 0.36);
  font-weight: 950;
}

.visual-kicker {
  margin: 42px 0 14px;
  color: #93c5fd;
  font-size: 12px;
  font-weight: 900;
  letter-spacing: 0.18em;
}

.login-visual h1 {
  max-width: 720px;
  margin: 0;
  font-size: 50px;
  line-height: 1.08;
  font-weight: 950;
  letter-spacing: -0.06em;
}

.visual-desc {
  max-width: 680px;
  margin: 22px 0 0;
  color: #cbd5e1;
  font-size: 17px;
  line-height: 1.85;
}

.visual-grid {
  position: absolute;
  left: 42px;
  right: 42px;
  bottom: 42px;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 14px;
}

.visual-grid div {
  padding: 18px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 22px;
  background: rgba(15, 23, 42, 0.28);
}

.visual-grid strong,
.visual-grid span {
  display: block;
}

.visual-grid strong {
  font-size: 18px;
  font-weight: 900;
}

.visual-grid span {
  margin-top: 8px;
  color: #bfdbfe;
  font-size: 13px;
}

.login-card {
  width: 100%;
  padding: 8px;
  border: 1px solid rgba(255, 255, 255, 0.72) !important;
  border-radius: 30px !important;
  background: rgba(255, 255, 255, 0.92) !important;
  box-shadow: 0 30px 80px rgba(15, 23, 42, 0.26) !important;
  backdrop-filter: blur(20px);
}

.form-head span {
  color: #2563eb;
  font-size: 12px;
  font-weight: 900;
  letter-spacing: 0.14em;
}

.form-head h2 {
  margin: 10px 0 8px;
  color: #0f172a;
  font-size: 30px;
  font-weight: 950;
  letter-spacing: -0.04em;
}

.form-head p {
  margin: 0 0 26px;
  color: #64748b;
  line-height: 1.7;
}

.login-btn {
  width: 100%;
  margin-top: 14px;
}

.demo-tip {
  margin-bottom: 14px;
  border-radius: 14px;
}

@media (max-width: 1040px) {
  .login-page {
    grid-template-columns: 1fr;
  }

  .login-visual {
    min-height: 420px;
  }
}
</style>
