<template>
  <div class="dashboard">

    <!-- Page Header -->
    <div class="page-header">
      <div class="page-header-left">
        <p class="page-label">Painel do Sistema</p>
        <h1 class="page-title">Visão geral do monitoramento hidrológico</h1>
      </div>
      <div class="live-badge" v-if="!loading">
        <span class="live-pulse"></span>
        Atualizações ao Vivo Ativas
      </div>
    </div>

    <!-- Stats Row -->
    <div class="stats-row">
      <div class="stat-card">
        <p class="stat-label">Nível de Risco Atual</p>
        <div class="stat-risk" :class="'stat-risk--' + riskLevel">
          <span class="risk-value">{{ riskLabel }}</span>
          <span class="risk-tag" :class="'tag--' + riskLevel">
            {{ riskLevel === 'low' ? 'Estável' : riskLevel === 'medium' ? 'Observação' : 'Crítico' }}
          </span>
        </div>
      </div>
      <div class="stat-card">
        <p class="stat-label">Total de Rios</p>
        <p class="stat-number">{{ rios.length }}</p>
        <p class="stat-sub">Estações ativas</p>
      </div>
      <div class="stat-card">
        <p class="stat-label">Zonas de Alto Risco</p>
        <p class="stat-number" :class="riosAltoRisco > 0 ? 'stat-number--danger' : 'stat-number--muted'">{{ riosAltoRisco }}</p>
        <p class="stat-sub">Requerem atenção</p>
      </div>
      <div class="stat-card">
        <p class="stat-label">Zonas de Risco Médio</p>
        <p class="stat-number" :class="riosMedioRisco > 0 ? 'stat-number--warn' : 'stat-number--muted'">{{ riosMedioRisco }}</p>
        <p class="stat-sub">Em observação</p>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="dash-loading">
      <svg class="spin" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="var(--accent)" stroke-width="2.5">
        <circle cx="12" cy="12" r="10" stroke-dasharray="32" stroke-dashoffset="32">
          <animateTransform attributeName="transform" type="rotate" from="0 12 12" to="360 12 12" dur="0.8s" repeatCount="indefinite"/>
        </circle>
      </svg>
      Carregando dados...
    </div>

    <!-- Empty -->
    <div v-else-if="rios.length === 0" class="empty-block">
      <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round">
        <path d="M2 12c.6.5 1.2 1 2.5 1 2.5 0 2.5-2 5-2 2.6 0 2.4 2 5 2 2.5 0 2.5-2 5-2 1.3 0 1.9.5 2.5 1"/>
      </svg>
      <p>Nenhum rio cadastrado</p>
      <span>Vá em <router-link to="/rios">Rios</router-link> para cadastrar rios e pontos de risco.</span>
    </div>

    <!-- Rivers by State -->
    <div v-else class="estados-wrapper">
      <div v-for="estado in estadosList" :key="estado" class="estado-bloco">
        <div class="estado-header">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
            <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
            <circle cx="12" cy="10" r="3"/>
          </svg>
          {{ estado }}
          <span class="estado-count">{{ riosPorEstado[estado].length }} {{ riosPorEstado[estado].length === 1 ? 'rio' : 'rios' }}</span>
        </div>

        <div v-for="rio in riosPorEstado[estado]" :key="rio.id" class="rio-bloco">
          <div class="rio-header" :class="getBadgeClass(rio.risco_inundacao)">
            <div class="rio-header-left">
              <div class="rio-icon" :class="getBadgeClass(rio.risco_inundacao)">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round">
                  <path d="M2 12c.6.5 1.2 1 2.5 1 2.5 0 2.5-2 5-2 2.6 0 2.4 2 5 2 2.5 0 2.5-2 5-2 1.3 0 1.9.5 2.5 1"/>
                </svg>
              </div>
              <div>
                <h2 class="rio-nome">{{ rio.nome }}</h2>
                <p class="rio-loc">{{ rio.cidade }} · {{ rio.estado }}</p>
              </div>
            </div>
            <div class="rio-header-right">
              <span class="badge" :class="getBadgeClass(rio.risco_inundacao)">
                <span class="badge-dot"></span>Risco {{ getRiskLabel(rio.risco_inundacao) }}
              </span>
              <span class="station-code">SP-BAS-{{ String(rio.id).padStart(3, '0') }}</span>
            </div>
          </div>

          <!-- Charts grid -->
          <div class="rio-charts">
            <div v-if="!pontosPorRio[rio.id]" class="pontos-loading">
              <svg class="spin" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--accent)" stroke-width="2.5">
                <circle cx="12" cy="12" r="10" stroke-dasharray="32" stroke-dashoffset="32">
                  <animateTransform attributeName="transform" type="rotate" from="0 12 12" to="360 12 12" dur="0.8s" repeatCount="indefinite"/>
                </circle>
              </svg>
              Carregando pontos...
            </div>
            <div v-else-if="pontosPorRio[rio.id].length === 0" class="pontos-empty">
              Nenhum ponto de risco. <router-link to="/rios">Adicionar</router-link>
            </div>
            <div v-else class="charts-grid">
              <div v-for="ponto in pontosPorRio[rio.id]" :key="ponto.id" class="chart-card">
                <div class="chart-card-header">
                  <div>
                    <h3 class="chart-title">
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--accent)" stroke-width="2" stroke-linecap="round">
                        <path d="M22 12h-4l-3 9L9 3l-3 9H2"/>
                      </svg>
                      {{ rio.nome }}
                    </h3>
                    <p class="chart-sub">
                      <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
                        <path d="M12 22s-8-4.5-8-11.8A8 8 0 0 1 12 2a8 8 0 0 1 8 8.2c0 7.3-8 11.8-8 11.8z"/>
                        <circle cx="12" cy="10" r="3"/>
                      </svg>
                      {{ ponto.descricao.length > 45 ? ponto.descricao.substring(0,45)+'…' : ponto.descricao }}
                      &nbsp;·&nbsp;
                      <span :class="getPontoNivelClass(ponto.nivel_risco)">
                        {{ ponto.nivel_risco === 1 ? '● Baixo' : ponto.nivel_risco === 2 ? '● Médio' : '● Alto' }}
                      </span>
                    </p>
                  </div>
                  <span class="live-tag"><span class="live-dot"></span>Ao Vivo</span>
                </div>
                <div class="chart-wrap">
                  <canvas :ref="el => setChartRef(el, ponto.id)"></canvas>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import api from '../services/api'
import Chart from 'chart.js/auto'

const chartCanvases = ref({})
let chartInstances = {}
let chartLevels = {}
let chartInterval = null

const setChartRef = (el, id) => { if (el) chartCanvases.value[id] = el }

const rios = ref([])
const loading = ref(true)
const lastUpdate = ref('')
const pontosPorRio = ref({})
const todosPontos = ref([])

const normalizeRisk = (risco) => {
  if (typeof risco === 'number') return risco
  if (typeof risco === 'string') {
    const lower = risco.toLowerCase().trim()
    if (lower === 'baixo') return 1
    if (lower === 'médio' || lower === 'medio') return 2
    if (lower === 'alto') return 3
    if (lower === 'muito alto') return 4
    const parsed = parseInt(lower, 10)
    return Number.isNaN(parsed) ? null : parsed
  }
  return null
}

const getRiskLabel = (risco) => {
  const v = normalizeRisk(risco)
  return v === 1 ? 'Baixo' : v === 2 ? 'Médio' : v === 3 ? 'Alto' : v === 4 ? 'Muito Alto' : 'Desconhecido'
}

const riosAltoRisco = computed(() =>
  rios.value.filter(r => { const v = normalizeRisk(r.risco_inundacao); return v === 3 || v === 4 }).length
)
const riosMedioRisco = computed(() =>
  rios.value.filter(r => normalizeRisk(r.risco_inundacao) === 2).length
)
const riskLabel = computed(() => {
  if (riosAltoRisco.value > 0) return 'ALTO'
  if (riosMedioRisco.value > 0) return 'MÉDIO'
  return 'BAIXO'
})
const riskLevel = computed(() => {
  if (riskLabel.value === 'ALTO') return 'high'
  if (riskLabel.value === 'MÉDIO') return 'medium'
  return 'low'
})

const getBadgeClass = (risco) => {
  const v = normalizeRisk(risco)
  if (v === 3 || v === 4) return 'badge--high'
  if (v === 2) return 'badge--medium'
  return 'badge--low'
}

const estadosList = computed(() => [...new Set(rios.value.map(r => r.estado))].filter(Boolean).sort())
const riosPorEstado = computed(() => {
  const map = {}
  rios.value.forEach(r => { if (!map[r.estado]) map[r.estado] = []; map[r.estado].push(r) })
  return map
})

const getPontoNivelClass = (nivel) => {
  if (nivel === 3) return 'nivel--alto'
  if (nivel === 2) return 'nivel--medio'
  return 'nivel--baixo'
}

const load = async () => {
  loading.value = true
  try {
    const res = await api.getRios()
    rios.value = Array.isArray(res.data) ? res.data : res.data.results || []
    const promises = rios.value.map(async (rio) => {
      try {
        const pr = await api.getPontosRisco(rio.id)
        const pontos = Array.isArray(pr.data) ? pr.data : pr.data.results || []
        pontosPorRio.value[rio.id] = pontos
        return pontos.map(ponto => ({ rio, ponto }))
      } catch { pontosPorRio.value[rio.id] = []; return [] }
    })
    const resultados = await Promise.all(promises)
    todosPontos.value = resultados.flat()
  } catch (err) {
    console.error('Erro ao carregar:', err)
  } finally {
    loading.value = false
    lastUpdate.value = new Date().toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
    await nextTick()
    if (todosPontos.value.length > 0) initCharts()
  }
}

const initCharts = () => {
  Object.values(chartInstances).forEach(c => c.destroy())
  chartInstances = {}

  todosPontos.value.forEach(({ ponto }) => {
    const canvas = chartCanvases.value[ponto.id]
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    const riskColors = { 1: getComputedStyle(document.documentElement).getPropertyValue('--risk-low').trim(), 2: getComputedStyle(document.documentElement).getPropertyValue('--risk-medium').trim(), 3: getComputedStyle(document.documentElement).getPropertyValue('--risk-high').trim() };
const nivelColor = riskColors[ponto.nivel_risco] || getComputedStyle(document.documentElement).getPropertyValue('--risk-low').trim();
    const gradient = ctx.createLinearGradient(0, 0, 0, 220)
    gradient.addColorStop(0, nivelColor + '40')
    gradient.addColorStop(1, nivelColor + '05')
    const baseMap = { 1: 0.8, 2: 1.4, 3: 2.0 }
    const base = baseMap[ponto.nivel_risco] || 1.0
    const variance = 0.25
    const data = Array.from({ length: 15 }, () => (base + (Math.random() * variance * 2 - variance)).toFixed(2))
    const labels = Array.from({ length: 15 }, (_, i) => {
      const d = new Date(); d.setSeconds(d.getSeconds() - (15 - i) * 10)
      return d.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
    })
    const atencao = (base + 0.5).toFixed(2)
    const alerta = (base + 0.85).toFixed(2)
    const emergencia = (base + 1.2).toFixed(2)
    chartLevels[ponto.id] = { base, variance, emergenciaLevel: parseFloat(emergencia) }

    chartInstances[ponto.id] = new Chart(ctx, {
      type: 'line',
      data: {
        labels,
        datasets: [
          { label: 'Nível (m)', data, borderColor: nivelColor, backgroundColor: gradient, borderWidth: 2, pointRadius: 3, pointHoverRadius: 5, pointBackgroundColor: nivelColor, pointBorderColor: 'transparent', fill: true, tension: 0.4 },
          { label: 'Emergência', data: Array(15).fill(emergencia), borderColor: riskColors[3], borderWidth: 1, borderDash: [5, 4], pointRadius: 0, fill: false },
          { label: 'Alerta', data: Array(15).fill(alerta), borderColor: riskColors[2], borderWidth: 1, borderDash: [5, 4], pointRadius: 0, fill: false },
          { label: 'Atenção', data: Array(15).fill(atencao), borderColor: riskColors[2], borderWidth: 1, borderDash: [5, 4], pointRadius: 0, fill: false }
        ]
      },
      options: {
        responsive: true, maintainAspectRatio: false, animation: { duration: 300 },
        plugins: {
          legend: { display: true, position: 'top', labels: { usePointStyle: true, color: getComputedStyle(document.documentElement).getPropertyValue('--text-muted').trim(), font: { size: 10 }, boxWidth: 8 } },
          tooltip: { backgroundColor: getComputedStyle(document.documentElement).getPropertyValue('--bg-elevated').trim() || '#0D1B2E', titleColor: getComputedStyle(document.documentElement).getPropertyValue('--text-primary').trim(), bodyColor: getComputedStyle(document.documentElement).getPropertyValue('--accent').trim(), borderColor: 'rgba(0,0,0,0.08)', borderWidth: 1, padding: 10 }
        },
        scales: {
          y: { min: Math.max(0, base - 0.6), max: base + 1.5, grid: { color: 'rgba(100,116,139,0.1)' }, ticks: { color: getComputedStyle(document.documentElement).getPropertyValue('--text-muted').trim(), font: { size: 10 } } },
          x: { grid: { display: false }, ticks: { color: getComputedStyle(document.documentElement).getPropertyValue('--text-muted').trim(), maxTicksLimit: 6, font: { size: 10 } } }
        }
      }
    })
  })

  if (chartInterval) clearInterval(chartInterval)
  chartInterval = setInterval(() => {
    const newLabel = new Date().toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
    Object.entries(chartInstances).forEach(([pontoId, chart]) => {
      const levels = chartLevels[pontoId]; if (!levels) return
      const ds = chart.data.datasets[0]
      let v = parseFloat(ds.data.slice(-1)[0]) + (Math.random() * levels.variance * 2 - levels.variance)
      v = Math.max(Math.max(0, levels.base - 0.6), Math.min(levels.emergenciaLevel + 0.2, v))
      chart.data.labels.push(newLabel); ds.data.push(v.toFixed(2))
      chart.data.datasets[1].data.push(chart.data.datasets[1].data[0])
      chart.data.datasets[2].data.push(chart.data.datasets[2].data[0])
      chart.data.datasets[3].data.push(chart.data.datasets[3].data[0])
      if (chart.data.labels.length > 15) { chart.data.labels.shift(); chart.data.datasets.forEach(d => d.data.shift()) }
      chart.update()
    })
    lastUpdate.value = newLabel
  }, 10000)
}

onMounted(() => load())
onUnmounted(() => { if (chartInterval) clearInterval(chartInterval); Object.values(chartInstances).forEach(c => c.destroy()); chartLevels = {} })
</script>

<style scoped>
.dashboard { display: flex; flex-direction: column; gap: 24px; animation: fadeInUp 0.35s ease-out; }

/* Header */
.page-header { display: flex; align-items: flex-end; justify-content: space-between; flex-wrap: wrap; gap: 12px; }
.page-label { font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: var(--text-muted); margin-bottom: 4px; }
.page-title { font-size: 1.5rem; font-weight: 800; letter-spacing: -0.02em; }

.live-badge {
  display: flex; align-items: center; gap: 8px;
  font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em;
  color: var(--status-active);
  padding: 5px 12px;
  border-radius: var(--radius-full);
  background: var(--status-active-bg);
  border: 1px solid rgba(16,185,129,0.2);
}

.live-pulse {
  width: 7px; height: 7px; border-radius: 50%;
  background: var(--status-active); animation: pulse 2s infinite;
}

/* Stats */
.stats-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }

.stat-card {
  background: var(--bg-card); border: 1px solid var(--border);
  border-radius: var(--radius-lg); padding: 20px 22px;
  transition: border-color var(--transition-fast), transform var(--transition-normal);
}
.stat-card:hover { border-color: var(--accent); transform: translateY(-2px); }

.stat-label { font-size: 0.68rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: var(--text-muted); margin-bottom: 10px; }

.stat-risk { display: flex; align-items: center; gap: 10px; }
.risk-value { font-size: 1.6rem; font-weight: 800; letter-spacing: -0.02em; }
.stat-risk--high .risk-value { color: var(--risk-high); }
.stat-risk--medium .risk-value { color: var(--risk-medium); }
.stat-risk--low .risk-value { color: var(--risk-low); }

.risk-tag { font-size: 0.65rem; font-weight: 700; padding: 3px 8px; border-radius: var(--radius-full); text-transform: uppercase; letter-spacing: 0.04em; }
.tag--high { background: var(--risk-high-bg); color: var(--risk-high); }
.tag--medium { background: var(--risk-medium-bg); color: var(--risk-medium); }
.tag--low { background: var(--risk-low-bg); color: var(--risk-low); }

.stat-number { font-size: 2rem; font-weight: 800; color: var(--text-primary); letter-spacing: -0.03em; line-height: 1; }
.stat-number--danger { color: var(--risk-high); }
.stat-number--warn { color: var(--risk-medium); }
.stat-number--muted { color: var(--text-muted); }
.stat-sub { font-size: 0.72rem; color: var(--text-muted); margin-top: 4px; }

/* Loading / Empty */
.dash-loading { display: flex; align-items: center; justify-content: center; gap: 12px; padding: 60px; color: var(--text-muted); font-size: 0.875rem; }
.empty-block { display: flex; flex-direction: column; align-items: center; gap: 10px; padding: 56px 24px; text-align: center; color: var(--text-muted); background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius-xl); }
.empty-block p { font-size: 0.95rem; font-weight: 600; color: var(--text-secondary); }
.empty-block a { color: var(--accent); font-weight: 600; }

/* States */
.estados-wrapper { display: flex; flex-direction: column; gap: 32px; }
.estado-bloco { display: flex; flex-direction: column; gap: 16px; }
.estado-header { display: flex; align-items: center; gap: 8px; font-size: 0.78rem; font-weight: 800; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.06em; padding-bottom: 8px; border-bottom: 1px solid var(--border); }
.estado-count { font-size: 0.65rem; background: var(--accent-soft); color: var(--accent); padding: 2px 8px; border-radius: var(--radius-full); margin-left: 4px; }

/* River Block */
.rio-bloco { background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius-xl); overflow: hidden; }

.rio-header { display: flex; align-items: center; justify-content: space-between; padding: 14px 20px; border-bottom: 1px solid var(--border-light); flex-wrap: wrap; gap: 10px; }
.rio-header.badge--high { border-left: 3px solid var(--risk-high); }
.rio-header.badge--medium { border-left: 3px solid var(--risk-medium); }
.rio-header.badge--low { border-left: 3px solid var(--risk-low); }
.rio-header-left { display: flex; align-items: center; gap: 12px; }
.rio-icon { width: 38px; height: 38px; border-radius: var(--radius-md); display: flex; align-items: center; justify-content: center; }
.rio-icon.badge--high { background: var(--risk-high-bg); color: var(--risk-high); }
.rio-icon.badge--medium { background: var(--risk-medium-bg); color: var(--risk-medium); }
.rio-icon.badge--low { background: var(--risk-low-bg); color: var(--risk-low); }
.rio-nome { font-size: 1rem; font-weight: 700; }
.rio-loc { font-size: 0.72rem; color: var(--text-muted); margin-top: 2px; }
.rio-header-right { display: flex; align-items: center; gap: 10px; }
.station-code { font-size: 0.7rem; font-family: var(--font-mono); color: var(--text-muted); }

/* Charts */
.rio-charts { padding: 18px 20px; }
.pontos-loading { display: flex; align-items: center; gap: 8px; color: var(--text-muted); font-size: 0.8rem; padding: 8px 0; }
.pontos-empty { color: var(--text-muted); font-size: 0.82rem; padding: 8px 0; }
.pontos-empty a { color: var(--accent); font-weight: 600; }

.charts-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(480px, 1fr)); gap: 20px; }

.chart-card { background: var(--bg-secondary); border: 1px solid var(--border); border-radius: var(--radius-lg); overflow: hidden; }

.chart-card-header { display: flex; align-items: flex-start; justify-content: space-between; padding: 16px 20px; border-bottom: 1px solid var(--border-light); gap: 12px; }

.chart-title { display: flex; align-items: center; gap: 8px; font-size: 0.95rem; font-weight: 700; }

.chart-sub { display: flex; align-items: center; flex-wrap: wrap; gap: 4px; font-size: 0.75rem; color: var(--text-muted); margin-top: 4px; }

.nivel--alto { color: var(--risk-high); font-weight: 700; }
.nivel--medio { color: var(--risk-medium); font-weight: 700; }
.nivel--baixo { color: var(--risk-low); font-weight: 700; }

.live-tag { display: flex; align-items: center; gap: 5px; font-size: 0.65rem; font-weight: 800; color: var(--risk-high); background: var(--risk-high-bg); padding: 4px 8px; border-radius: var(--radius-sm); text-transform: uppercase; letter-spacing: 0.04em; white-space: nowrap; border: 1px solid rgba(220,38,38,0.2); flex-shrink: 0; }

.live-dot { width: 6px; height: 6px; border-radius: 50%; background: var(--risk-high); animation: pulse 1.5s infinite; }

.chart-wrap { height: 260px; padding: 16px 20px; }

@media (max-width: 1024px) { .stats-row { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 640px) { .stats-row { grid-template-columns: 1fr; } .charts-grid { grid-template-columns: 1fr; } }
</style>