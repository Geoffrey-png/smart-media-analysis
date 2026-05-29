<template>
  <article class="stat-card" :class="`tone-${tone}`">
    <div class="stat-top">
      <div class="stat-icon">{{ icon }}</div>
      <span v-if="change" class="stat-change" :class="{ down: trend === 'down' }">
        {{ change }}
      </span>
    </div>
    <div class="label">{{ label }}</div>
    <div class="value">{{ value }}</div>
    <div class="desc">{{ desc }}</div>
  </article>
</template>

<script setup>
defineProps({
  label: String,
  value: [String, Number],
  desc: String,
  icon: {
    type: String,
    default: '◆'
  },
  change: {
    type: String,
    default: ''
  },
  trend: {
    type: String,
    default: 'up'
  },
  tone: {
    type: String,
    default: 'blue'
  }
})
</script>

<style scoped>
.stat-card {
  position: relative;
  min-height: 152px;
  overflow: hidden;
  padding: 20px;
  border: 1px solid rgba(148, 163, 184, 0.16);
  border-radius: 24px;
  background:
    linear-gradient(135deg, rgba(255, 255, 255, 0.98), rgba(248, 250, 252, 0.86)),
    radial-gradient(circle at top right, var(--tone-soft), transparent 42%);
  box-shadow: 0 18px 42px rgba(15, 23, 42, 0.07);
}

.stat-card::after {
  content: '';
  position: absolute;
  right: -34px;
  bottom: -42px;
  width: 110px;
  height: 110px;
  border-radius: 50%;
  background: var(--tone-soft);
}

.stat-top {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.stat-icon {
  width: 42px;
  height: 42px;
  display: grid;
  place-items: center;
  color: var(--tone);
  border-radius: 15px;
  background: var(--tone-soft);
  font-size: 18px;
  font-weight: 900;
}

.stat-change {
  padding: 5px 9px;
  color: #047857;
  border-radius: 999px;
  background: rgba(209, 250, 229, 0.75);
  font-size: 12px;
  font-weight: 850;
}

.stat-change.down {
  color: #b91c1c;
  background: rgba(254, 226, 226, 0.8);
}

.label {
  position: relative;
  z-index: 1;
  margin-top: 18px;
  color: #64748b;
  font-size: 13px;
  font-weight: 760;
}

.value {
  position: relative;
  z-index: 1;
  margin-top: 8px;
  color: #0f172a;
  font-size: 34px;
  font-weight: 900;
  letter-spacing: -0.04em;
}

.desc {
  position: relative;
  z-index: 1;
  margin-top: 7px;
  color: #94a3b8;
  font-size: 13px;
  line-height: 1.5;
}

.tone-blue {
  --tone: #2563eb;
  --tone-soft: rgba(37, 99, 235, 0.13);
}

.tone-cyan {
  --tone: #0891b2;
  --tone-soft: rgba(8, 145, 178, 0.13);
}

.tone-purple {
  --tone: #7c3aed;
  --tone-soft: rgba(124, 58, 237, 0.13);
}

.tone-orange {
  --tone: #ea580c;
  --tone-soft: rgba(234, 88, 12, 0.13);
}
</style>
