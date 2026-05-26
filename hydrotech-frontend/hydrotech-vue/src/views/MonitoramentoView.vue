<template>
  <div class="mon-page">
    <!-- Animated Gradient Background -->
    <div class="mesh-bg">
      <div class="mesh-blob blob-1"></div>
      <div class="mesh-blob blob-2"></div>
      <div class="mesh-blob blob-3"></div>
    </div>
    <header class="mon-topbar">
      <div class="mon-inner">
        <div class="mon-brand">
          <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="#38BDF8" stroke-width="2.5" stroke-linecap="round"><path d="M2 12c.6.5 1.2 1 2.5 1 2.5 0 2.5-2 5-2 2.6 0 2.4 2 5 2 2.5 0 2.5-2 5-2 1.3 0 1.9.5 2.5 1"/><path d="M2 6c.6.5 1.2 1 2.5 1C7 7 7 5 9.5 5c2.6 0 2.4 2 5 2 2.5 0 2.5-2 5-2 1.3 0 1.9.5 2.5 1"/><path d="M2 18c.6.5 1.2 1 2.5 1 2.5 0 2.5-2 5-2 2.6 0 2.4 2 5 2 2.5 0 2.5-2 5-2 1.3 0 1.9.5 2.5 1"/></svg>
          <span>HydroTech <b>Monitoramento Público</b></span>
        </div>
        <div class="mon-meta">
          <span class="live-pill"><span class="live-dot"></span>AO VIVO · 10s</span>
          <span v-if="lastUpdate" class="upd-time">{{ lastUpdate }}</span>
          <router-link to="/" class="back-lnk">← Início</router-link>
        </div>
      </div>
    </header>

    <div class="mon-filter-bar">
      <div class="mon-inner row">
        <div class="frow">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/></svg>
          <select v-model="filtroEstado" class="f-sel">
            <option value="">Todos os estados</option>
            <option v-for="e in estados" :key="e" :value="e">{{ e }}</option>
          </select>
        </div>
        <div class="fstats">
          <span class="fs fs-t">{{ totalRios }} rios</span>
          <span class="fs fs-h">{{ totalAlto }} alto risco</span>
          <span class="fs fs-m">{{ totalMedio }} médio</span>
          <span class="fs fs-l">{{ totalBaixo }} baixo</span>
        </div>
      </div>
    </div>

    <div v-if="loading" class="mon-state">
      <svg class="spin" width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="#38BDF8" stroke-width="2.5"><circle cx="12" cy="12" r="10" stroke-dasharray="32" stroke-dashoffset="32"><animateTransform attributeName="transform" type="rotate" from="0 12 12" to="360 12 12" dur="0.8s" repeatCount="indefinite"/></circle></svg>
      Carregando dados...
    </div>

    <main v-else class="mon-main">
      <!-- Agrupado por Estado -->
      <div v-for="estado in estadosFiltrados" :key="estado" class="estado-section">
        <div class="estado-header">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>
          {{ estado }}
          <span class="estado-count">{{ riosPorEstado[estado].length }} rios</span>
        </div>

        <!-- Rios do Estado -->
        <div v-for="rio in riosPorEstado[estado]" :key="rio.id" class="rio-block">
          <div class="rio-hdr" :class="rc(rio.risco_inundacao)">
            <div class="rio-hdr-l">
              <div class="rio-icon" :class="rc(rio.risco_inundacao)">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><path d="M2 12c.6.5 1.2 1 2.5 1 2.5 0 2.5-2 5-2 2.6 0 2.4 2 5 2 2.5 0 2.5-2 5-2 1.3 0 1.9.5 2.5 1"/></svg>
              </div>
              <div>
                <div class="rio-nome-container">
                  <h2 class="rio-name">{{ rio.nome }}</h2>
                  <div 
                    class="gemini-hover-trigger"
                    @mouseenter="showGemini(rio.id)"
                    @mouseleave="hideGemini"
                  >
                    ✨ Conheça este rio
                    
                    <transition name="gemini-fade">
                      <div v-if="expandedGemini === rio.id" class="gemini-panel-wrapper" @click.stop>
                        <div v-if="loadingGemini" class="gemini-skeleton">
                          <div class="skeleton-header">
                            <div class="skeleton-pill"></div>
                            <div class="skeleton-pill"></div>
                            <div class="skeleton-pill"></div>
                          </div>
                          <div class="skeleton-body">
                            <div class="skeleton-line skeleton-line-title"></div>
                            <div class="skeleton-line"></div>
                            <div class="skeleton-line"></div>
                            <div class="skeleton-line skeleton-line-short"></div>
                          </div>
                        </div>

                        <div v-else-if="geminiData" class="gemini-card">
                          <div class="gemini-card-header">
                            <div class="gemini-brand">
                              <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor" class="gemini-icon">
                                <path d="M12 2a1 1 0 0 1 .993.883L13 3v2.858c3.21.364 5.778 2.932 6.142 6.142L19.284 13h2.858a1 1 0 0 1 .117 1.993L22 15h-2.858c-.364 3.21-2.932 5.778-6.142 6.142L13 21.284v2.858a1 1 0 0 1-1.993.117L11 24v-2.858c-3.21-.364-5.778-2.932-6.142-6.142L4.716 15H1.858a1 1 0 0 1-.117-1.993L2 13h2.858c.364-3.21 2.932-5.778 6.142-6.142L11 5.716V2.858A1 1 0 0 1 12 2z"/>
                              </svg>
                              <span>Ficha Técnica (Gemini AI)</span>
                            </div>
                            <div v-if="geminiData.using_fallback" class="fallback-tag">
                              💡 Simulação
                            </div>
                          </div>
                          
                          <div class="gemini-metrics">
                            <div class="metric-item">
                              <div class="metric-icon">📏</div>
                              <div class="metric-content">
                                <span class="metric-lbl">Comprimento</span>
                                <span class="metric-val">{{ geminiData.comprimento }}</span>
                              </div>
                            </div>
                            <div class="metric-item">
                              <div class="metric-icon">📍</div>
                              <div class="metric-content">
                                <span class="metric-lbl">Áreas de Maior Risco</span>
                                <span class="metric-val">{{ geminiData.areas_risco }}</span>
                              </div>
                            </div>
                            <div class="metric-item">
                              <div class="metric-icon">🌊</div>
                              <div class="metric-content">
                                <span class="metric-lbl">Foz</span>
                                <span class="metric-val">{{ geminiData.foz }}</span>
                              </div>
                            </div>
                          </div>

                          <div class="gemini-info">
                            <div class="gemini-desc">
                              <h3>Descrição e Histórico de Enchentes</h3>
                              <p>{{ geminiData.descricao_historico_enchentes }}</p>
                            </div>
                            <div class="gemini-curiosidade">
                              <h3>⚠️ Período Crítico</h3>
                              <p>{{ geminiData.periodo_critico }}</p>
                            </div>
                          </div>
                        </div>
                        
                        <div v-else class="gemini-error">
                          ❌ Falha ao carregar informações.
                        </div>
                      </div>
                    </transition>
                  </div>
                </div>
                <p class="rio-loc">{{ rio.cidade }} · {{ rio.estado }}</p>
              </div>
            </div>
            <div class="rio-hdr-r">
              <span class="risk-chip" :class="rc(rio.risco_inundacao)">{{ rl(rio.risco_inundacao) }}</span>
            </div>
          </div>

          <!-- Gráficos por Ponto de Risco (igual ao Dashboard Admin) -->
          <div class="charts-wrap">
            <div v-if="!pontos[rio.id]" class="charts-loading">Carregando pontos...</div>
            <div v-else-if="pontos[rio.id].length === 0" class="charts-empty">Nenhum ponto de risco cadastrado neste rio.</div>
            <TransitionGroup v-else name="list" tag="div" class="charts-grid">
              <div v-for="p in sortedPontos(rio.id)" :key="p.id" class="chart-card">
                <div class="chart-card-hdr">
                  <div>
                    <h3 class="chart-card-title">
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--accent)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>
                      {{ rio.nome }}
                    </h3>
                    <p class="chart-card-sub">
                      <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M12 22s-8-4.5-8-11.8A8 8 0 0 1 12 2a8 8 0 0 1 8 8.2c0 7.3-8 11.8-8 11.8z"/><circle cx="12" cy="10" r="3"/></svg>
                      Ponto: {{ p.descricao.length > 45 ? p.descricao.substring(0,45)+'…' : p.descricao }}
                      &middot;
                      <span :class="'nlv--'+(p.nivel_risco===3?'alto':p.nivel_risco===2?'medio':'baixo')">
                        {{ p.nivel_risco===1?'🟢 Baixo':p.nivel_risco===2?'🟡 Médio':'🔴 Alto' }}
                      </span>
                    </p>
                  </div>
                  <div style="display: flex; gap: 8px; align-items: center;">
                    <button class="abtn abtn-sm" :class="{ 'abtn--fav': isFav(p.id) }" @click="toggleFav(p.id)" style="padding: 4px 8px; font-size: 0.7rem;">
                      <svg width="12" height="12" viewBox="0 0 24 24" :fill="isFav(p.id)?'currentColor':'none'" stroke="currentColor" stroke-width="2" stroke-linecap="round"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
                      {{ isFav(p.id) ? 'Favorito' : 'Favoritar' }}
                    </button>
                    <button class="abtn abtn-sm" :class="{ 'abtn--alr': isAlert(p.id) }" @click="toggleAlert(p.id)" style="padding: 4px 8px; font-size: 0.7rem;">
                      <svg width="12" height="12" viewBox="0 0 24 24" :fill="isAlert(p.id)?'currentColor':'none'" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>
                      {{ isAlert(p.id) ? 'Alertas On' : 'Alertas' }}
                    </button>
                    <span class="live-badge" style="margin-left: 8px;"><span class="live-dot"></span>AO VIVO</span>
                  </div>
                </div>
                <div class="chart-canvas-wrap">
                  <canvas :ref="el => setRef(el, p)"></canvas>
                </div>
              </div>
            </TransitionGroup>
          </div>
        </div>
      </div>

      <div v-if="estadosFiltrados.length === 0 && !loading" class="mon-state">Nenhum rio encontrado.</div>
    </main>

    <footer class="mon-footer">HydroTech · Sistema de Monitoramento Hidrológico · Gráficos atualizados a cada 10 segundos</footer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import api from '../services/api'
import Chart from 'chart.js/auto'

const loading = ref(true)
const rios = ref([])
const pontos = ref({})
const filtroEstado = ref('')
const lastUpdate = ref('')
const canvasMap = ref({})
let charts = {}
let chartLevels = {}
let ticker = null

const expandedGemini = ref(null)
const geminiData = ref(null)
const loadingGemini = ref(false)
let geminiHoverTimer = null

const showGemini = async (rioId) => {
  if (geminiHoverTimer) clearTimeout(geminiHoverTimer)
  
  geminiHoverTimer = setTimeout(async () => {
    if (expandedGemini.value === rioId) return
    
    expandedGemini.value = rioId
    geminiData.value = null
    loadingGemini.value = true
    try {
      // Como agora liberamos o backend pra rotas públicas, batemos no endpoint
      const res = await api.getRioDescricaoGemini(rioId)
      geminiData.value = res.data
    } catch (err) {
      console.error('Erro ao carregar dados do Gemini:', err)
      geminiData.value = null
    } finally {
      loadingGemini.value = false
    }
  }, 250)
}

const hideGemini = () => {
  if (geminiHoverTimer) clearTimeout(geminiHoverTimer)
  expandedGemini.value = null
  geminiData.value = null
}

const favs = ref(new Set(JSON.parse(localStorage.getItem('ht_favs') || '[]')))
const alerts = ref(new Set(JSON.parse(localStorage.getItem('ht_alerts') || '[]')))
const isFav = id => favs.value.has(id)
const isAlert = id => alerts.value.has(id)
const toggleFav = id => {
  const next = new Set(favs.value)
  next.has(id) ? next.delete(id) : next.add(id)
  favs.value = next
  localStorage.setItem('ht_favs', JSON.stringify([...favs.value]))
}
const toggleAlert = id => { isAlert(id) ? alerts.value.delete(id) : alerts.value.add(id); localStorage.setItem('ht_alerts', JSON.stringify([...alerts.value])) }

const rc = r => r >= 3 ? 'risk--high' : r === 2 ? 'risk--medium' : 'risk--low'
const rl = r => ({ 1: 'Baixo', 2: 'Médio', 3: 'Alto', 4: 'Muito Alto' }[r] || 'N/D')

const estados = computed(() => [...new Set(rios.value.map(r => r.estado))].filter(Boolean).sort())
const estadosFiltrados = computed(() => filtroEstado.value ? [filtroEstado.value] : estados.value)

const riosPorEstado = computed(() => {
  const map = {}
  rios.value.forEach(r => { if (!map[r.estado]) map[r.estado] = []; map[r.estado].push(r) })
  Object.keys(map).forEach(estado => {
    map[estado].sort((a, b) => {
      const fa = (pontos.value[a.id] || []).some(p => favs.value.has(p.id)) ? 0 : 1
      const fb = (pontos.value[b.id] || []).some(p => favs.value.has(p.id)) ? 0 : 1
      return fa - fb
    })
  })
  return map
})
const totalRios = computed(() => rios.value.length)
const totalAlto = computed(() => rios.value.filter(r => r.risco_inundacao >= 3).length)
const totalMedio = computed(() => rios.value.filter(r => r.risco_inundacao === 2).length)
const totalBaixo = computed(() => rios.value.filter(r => r.risco_inundacao === 1).length)

const setRef = (el, ponto) => { 
  if (el) {
    const isNew = canvasMap.value[ponto.id] !== el
    canvasMap.value[ponto.id] = el
    if (isNew) {
      nextTick(() => {
        buildChart(ponto)
      })
    }
  }
}

const sortedPontos = (rioId) => {
  const pts = pontos.value[rioId] || []
  return [...pts].sort((a, b) => {
    const fa = favs.value.has(a.id) ? 0 : 1
    const fb = favs.value.has(b.id) ? 0 : 1
    return fa - fb
  })
}

// Igual ao Dashboard Admin
const buildChart = (ponto) => {
  const canvas = canvasMap.value[ponto.id]
  if (!canvas) return
  if (charts[ponto.id]) charts[ponto.id].destroy()
  const ctx = canvas.getContext('2d')
  const nivelColor = ponto.nivel_risco === 3 ? '#EF4444' : ponto.nivel_risco === 2 ? '#F59E0B' : '#10B981'
  const gradient = ctx.createLinearGradient(0, 0, 0, 300)
  gradient.addColorStop(0, nivelColor + '44')
  gradient.addColorStop(1, nivelColor + '00')
  const baseMap = { 1: 0.8, 2: 1.4, 3: 2.0 }
  const base = baseMap[ponto.nivel_risco] || 1.0
  const variance = 0.25
  const labels = Array.from({ length: 15 }, (_, i) => { const d = new Date(); d.setSeconds(d.getSeconds() - (14-i)*10); return d.toLocaleTimeString('pt-BR',{hour:'2-digit',minute:'2-digit',second:'2-digit'}) })
  const data = Array.from({ length: 15 }, () => +(base + (Math.random()*variance*2 - variance)).toFixed(2))
  const atencao = +(base + 0.5).toFixed(2)
  const alerta = +(base + 0.85).toFixed(2)
  const emergencia = +(base + 1.2).toFixed(2)
  chartLevels[ponto.id] = { base, variance, emergencia }
  charts[ponto.id] = new Chart(ctx, {
    type: 'line',
    data: {
      labels,
      datasets: [
        { label: 'Nível (m)', data, borderColor: nivelColor, backgroundColor: gradient, borderWidth: 2.5, pointRadius: 4, pointBackgroundColor: nivelColor, pointBorderColor: '#fff', pointBorderWidth: 1.5, fill: true, tension: 0.4 },
        { label: 'Emergência', data: Array(15).fill(emergencia), borderColor: '#EF4444', borderWidth: 1.5, borderDash: [6,4], pointRadius: 0, fill: false, tension: 0 },
        { label: 'Alerta', data: Array(15).fill(alerta), borderColor: '#F97316', borderWidth: 1.5, borderDash: [6,4], pointRadius: 0, fill: false, tension: 0 },
        { label: 'Atenção', data: Array(15).fill(atencao), borderColor: '#EAB308', borderWidth: 1.5, borderDash: [6,4], pointRadius: 0, fill: false, tension: 0 }
      ]
    },
    options: {
      responsive: true, maintainAspectRatio: false, animation: { duration: 400 },
      plugins: {
        legend: { display: true, position: 'top', labels: { usePointStyle: true, color: '#64748B', font: { size: 11 } } },
        tooltip: { backgroundColor: '#1e293b', titleColor: '#fff', bodyColor: '#38BDF8', padding: 10 }
      },
      scales: {
        y: { min: Math.max(0, base-0.6), max: base+1.5, grid: { color: 'rgba(100,116,139,0.1)' }, ticks: { color: '#64748B' } },
        x: { grid: { display: false }, ticks: { color: '#64748B', maxTicksLimit: 6 } }
      }
    }
  })
}

// Whapi configuration (Sandbox)
const WHAPI_TOKEN = 'YuOAsd5Lgg3bOMZOgueq5KRMB8Zhzlwu';
const CONTATOS = ['5519998534990', '5519997490041'];

const enviarMensagemWhatsApp = async (to, message) => {
  try {
    const response = await fetch('https://gate.whapi.cloud/messages/text', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${WHAPI_TOKEN}`,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify({
        to: `${to}@s.whatsapp.net`,
        body: message
      })
    });
    if (response.ok) {
      console.log(`✅ Alerta enviado para ${to} com sucesso.`);
    } else {
      console.error(`❌ Falha ao enviar para ${to}. Status: ${response.status}`);
    }
  } catch (error) {
    console.error(`Erro na requisição para ${to}: ${error.message}`);
  }
};

const tick = () => {
  const label = new Date().toLocaleTimeString('pt-BR',{hour:'2-digit',minute:'2-digit',second:'2-digit'})
  lastUpdate.value = label
  Object.entries(charts).forEach(([id, chart]) => {
    const lvl = chartLevels[id]; if (!lvl) return
    const ds = chart.data.datasets[0]
    const last = parseFloat(ds.data.at(-1))
    let next = +(Math.max(Math.max(0,lvl.base-0.6), Math.min(lvl.emergencia+0.2, last+(Math.random()*lvl.variance*2-lvl.variance)))).toFixed(2)
    chart.data.labels.push(label); ds.data.push(next)
    chart.data.datasets[1].data.push(chart.data.datasets[1].data[0])
    chart.data.datasets[2].data.push(chart.data.datasets[2].data[0])
    chart.data.datasets[3].data.push(chart.data.datasets[3].data[0])
    if (chart.data.labels.length > 15) { chart.data.labels.shift(); chart.data.datasets.forEach(d => d.data.shift()) }
    chart.update()

    // Integração Whapi: Verifica nível e dispara alerta se necessário
    const numericId = Number(id);
    if (next >= lvl.emergencia && isAlert(numericId)) {
      if (!lvl.alertado) {
        lvl.alertado = true; // Marca como alertado para não disparar a cada 10 segundos
        
        let pontoDesc = "Ponto Desconhecido";
        let rioNome = "";
        
        // Encontra o nome do Rio e a Descrição do Ponto de Risco
        Object.entries(pontos.value).forEach(([rId, pts]) => {
          const pt = pts.find(p => p.id === numericId);
          if (pt) {
            pontoDesc = pt.descricao;
            const r = rios.value.find(rio => rio.id == Number(rId));
            if (r) rioNome = r.nome;
          }
        });
        
        const localNome = rioNome ? `${rioNome} - ${pontoDesc}` : pontoDesc;
        console.log(`⚠️ Nível de emergência atingido em ${localNome}! Disparando alertas via Whapi...`);
        const mensagemAlerta = `⚠️ *ALERTA HYDROTECH*\nO nível em *${localNome}* atingiu ${next}m, nível de EMERGÊNCIA!\nEvite áreas de risco nas proximidades.`;
        
        CONTATOS.forEach(numero => {
          enviarMensagemWhatsApp(numero, mensagemAlerta);
        });
      }
    } else if (next < lvl.emergencia) {
      lvl.alertado = false; // Reseta o estado quando o nível abaixa do ponto de emergência
    }
  })
}

onMounted(async () => {
  try {
    const res = await api.getRiosPublico()
    rios.value = Array.isArray(res.data) ? res.data : res.data.results || []
    await Promise.all(rios.value.map(async rio => {
      try {
        const pr = await api.getPontosRiscoPublico(rio.id)
        pontos.value[rio.id] = Array.isArray(pr.data) ? pr.data : pr.data.results || []
      } catch { pontos.value[rio.id] = [] }
    }))
    lastUpdate.value = new Date().toLocaleTimeString('pt-BR',{hour:'2-digit',minute:'2-digit',second:'2-digit'})
  } catch(e) {
    console.error(e)
  } finally {
    loading.value = false   // <-- primeiro renderiza os canvas
  }
  await nextTick()          // <-- espera o DOM atualizar
  rios.value.forEach(rio => {
    (pontos.value[rio.id] || []).forEach(ponto => buildChart(ponto))
  })
  ticker = setInterval(tick, 10000)
})

onUnmounted(() => {
  if (ticker) clearInterval(ticker)
  Object.values(charts).forEach(c => c.destroy())
})
</script>

<style scoped>
.mon-page { min-height: 100vh; background: var(--bg-primary); color: var(--text-primary); display: flex; flex-direction: column; position: relative; overflow-x: hidden; }

/* Animated Gradient Mesh Background */
.mesh-bg {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
  z-index: 0;
  pointer-events: none;
}
.mesh-blob {
  position: absolute;
  filter: blur(120px);
  opacity: 0.25;
  animation: float 20s infinite alternate;
}
.blob-1 {
  top: -10%; left: -10%; width: 50vw; height: 50vw;
  background: radial-gradient(circle, rgba(14,165,233,0.3) 0%, rgba(14,165,233,0) 70%);
}
.blob-2 {
  bottom: -20%; right: -10%; width: 60vw; height: 60vw;
  background: radial-gradient(circle, rgba(56,189,248,0.2) 0%, rgba(56,189,248,0) 70%);
  animation-delay: -5s;
}
.blob-3 {
  top: 40%; left: 40%; width: 40vw; height: 40vw;
  background: radial-gradient(circle, rgba(2,132,199,0.2) 0%, rgba(2,132,199,0) 70%);
  animation-delay: -10s;
}

@keyframes float {
  0% { transform: translate(0, 0) scale(1); }
  50% { transform: translate(5%, 10%) scale(1.1); }
  100% { transform: translate(-5%, -5%) scale(0.9); }
}

/* Topbar */
.mon-topbar { background: rgba(15, 23, 42, 0.7); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); border-bottom: 1px solid rgba(255,255,255,0.05); padding: 0 24px; position: sticky; top: 0; z-index: 100; }
.mon-inner { max-width: 1300px; margin: 0 auto; position: relative; z-index: 2; }
.mon-inner.row { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px; }
.mon-topbar .mon-inner { display: flex; align-items: center; justify-content: space-between; height: 58px; }
.mon-brand { display: flex; align-items: center; gap: 10px; font-size: 0.95rem; color: var(--text-secondary); }
.mon-brand b { color: var(--accent); }
.mon-meta { display: flex; align-items: center; gap: 14px; }
.live-pill { display: flex; align-items: center; gap: 6px; font-size: 0.7rem; font-weight: 800; color: #EF4444; background: rgba(239,68,68,0.1); padding: 4px 10px; border-radius: 20px; border: 1px solid rgba(239,68,68,0.2); letter-spacing: .5px; }
.live-dot { width: 7px; height: 7px; background: #EF4444; border-radius: 50%; animation: pulse 1.4s infinite; }
.upd-time { font-size: 0.75rem; color: var(--text-muted); }
.back-lnk { font-size: 0.8rem; color: var(--accent); text-decoration: none; font-weight: 600; }
.back-lnk:hover { opacity: .7; }

/* Filter bar */
.mon-filter-bar { background: rgba(15, 23, 42, 0.5); backdrop-filter: blur(10px); border-bottom: 1px solid rgba(255,255,255,0.05); padding: 10px 24px; position: relative; z-index: 2; }
.frow { display: flex; align-items: center; gap: 8px; color: var(--text-secondary); }
.f-sel { padding: 7px 12px; border-radius: var(--radius-md); border: 1px solid rgba(255,255,255,0.1); background: rgba(30, 41, 59, 0.6); color: var(--text-primary); font-size: 0.85rem; }
.fstats { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.fs { font-size: 0.73rem; font-weight: 700; padding: 3px 10px; border-radius: 20px; }
.fs-t { background: rgba(56, 189, 248, 0.1); color: var(--accent); border: 1px solid rgba(56, 189, 248, 0.2); }
.fs-h { background: rgba(239, 68, 68, 0.1); color: var(--risk-high); border: 1px solid rgba(239, 68, 68, 0.2); }
.fs-m { background: rgba(245, 158, 11, 0.1); color: var(--risk-medium); border: 1px solid rgba(245, 158, 11, 0.2); }
.fs-l { background: rgba(16,185,129,.1); color: var(--risk-low); border: 1px solid rgba(16, 185, 129, 0.2); }

/* States */
.mon-state { flex: 1; display: flex; align-items: center; justify-content: center; gap: 12px; padding: 80px; color: var(--text-muted); flex-direction: column; position: relative; z-index: 2; }

/* Main */
.mon-main { flex: 1; max-width: 1300px; margin: 0 auto; width: 100%; padding: 28px 24px; display: flex; flex-direction: column; gap: 36px; position: relative; z-index: 2; }

/* Estado Section */
.estado-section { display: flex; flex-direction: column; gap: 20px; }
.estado-header { display: flex; align-items: center; gap: 8px; font-size: 1rem; font-weight: 800; color: var(--text-primary); padding-bottom: 8px; border-bottom: 2px solid rgba(56, 189, 248, 0.4); }
.estado-count { font-size: 0.75rem; font-weight: 600; background: rgba(56, 189, 248, 0.1); color: var(--accent); padding: 2px 8px; border-radius: 20px; margin-left: 4px; border: 1px solid rgba(56, 189, 248, 0.2); }

/* Rio Block */
.rio-block { background: rgba(15, 23, 42, 0.6); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: var(--radius-xl); overflow: hidden; box-shadow: 0 10px 30px rgba(0,0,0,0.2); }
.rio-hdr { display: flex; align-items: center; justify-content: space-between; padding: 16px 22px; flex-wrap: wrap; gap: 12px; border-bottom: 1px solid rgba(255,255,255,0.05); }
.rio-hdr.risk--high { border-left: 4px solid var(--risk-high); }
.rio-hdr.risk--medium { border-left: 4px solid var(--risk-medium); }
.rio-hdr.risk--low { border-left: 4px solid var(--risk-low); }
.rio-hdr-l { display: flex; align-items: center; gap: 12px; }
.rio-icon { width: 42px; height: 42px; border-radius: var(--radius-lg); display: flex; align-items: center; justify-content: center; }
.rio-icon.risk--high { background: rgba(239, 68, 68, 0.1); color: var(--risk-high); }
.rio-icon.risk--medium { background: rgba(245, 158, 11, 0.1); color: var(--risk-medium); }
.rio-icon.risk--low { background: rgba(16,185,129,.12); color: var(--risk-low); }
.rio-name { font-size: 1.1rem; font-weight: 800; color: var(--text-primary); }
.rio-loc { font-size: 0.78rem; color: var(--text-muted); margin-top: 2px; }
.rio-hdr-r { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.risk-chip { font-size: 0.72rem; font-weight: 800; padding: 4px 12px; border-radius: 20px; }
.risk-chip.risk--high { background: rgba(239, 68, 68, 0.15); color: var(--risk-high); border: 1px solid rgba(239, 68, 68, 0.3); }
.risk-chip.risk--medium { background: rgba(245, 158, 11, 0.15); color: var(--risk-medium); border: 1px solid rgba(245, 158, 11, 0.3); }
.risk-chip.risk--low { background: rgba(16,185,129,.15); color: var(--risk-low); border: 1px solid rgba(16, 185, 129, 0.3); }
.abtn { display: flex; align-items: center; gap: 6px; padding: 7px 13px; border-radius: var(--radius-md); border: 1px solid rgba(255,255,255,0.1); background: rgba(30, 41, 59, 0.4); color: var(--text-muted); font-size: 0.78rem; font-weight: 600; cursor: pointer; transition: all .2s; backdrop-filter: blur(4px); }
.abtn:hover { border-color: var(--accent); color: var(--accent); background: rgba(30, 41, 59, 0.8); }
.abtn--fav { color: #F59E0B; border-color: #F59E0B; background: rgba(245,158,11,.08); }
.abtn--alr { color: var(--accent); border-color: var(--accent); background: rgba(56, 189, 248, 0.1); }

/* Charts area */
.charts-wrap { padding: 20px 22px; }
.charts-loading, .charts-empty { color: var(--text-muted); font-size: 0.85rem; text-align: center; padding: 20px; }
.charts-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(480px, 1fr)); gap: 20px; position: relative; }

/* Transitions */
.list-move,
.list-enter-active,
.list-leave-active {
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}
.list-enter-from,
.list-leave-to {
  opacity: 0;
  transform: translateY(30px) scale(0.95);
}
.list-leave-active {
  position: absolute;
}

/* Chart Card — Glassmorphism */
.chart-card { background: rgba(15, 23, 42, 0.4); border: 1px solid rgba(255,255,255,0.05); border-radius: var(--radius-xl); overflow: hidden; backdrop-filter: blur(10px); }
.chart-card-hdr { display: flex; align-items: flex-start; justify-content: space-between; padding: 18px 22px; border-bottom: 1px solid rgba(255,255,255,0.05); gap: 10px; }
.chart-card-title { display: flex; align-items: center; gap: 8px; font-size: 1rem; font-weight: 700; color: var(--text-primary); }
.chart-card-sub { display: flex; align-items: center; flex-wrap: wrap; gap: 4px; font-size: 0.78rem; color: var(--text-muted); margin-top: 5px; }
.nlv--alto { color: #EF4444; font-weight: 700; }
.nlv--medio { color: #F59E0B; font-weight: 700; }
.nlv--baixo { color: #10B981; font-weight: 700; }
.live-badge { display: flex; align-items: center; gap: 5px; font-size: 0.7rem; font-weight: 800; color: #EF4444; background: rgba(239,68,68,.1); padding: 4px 9px; border-radius: 8px; border: 1px solid rgba(239,68,68,.2); flex-shrink: 0; }
.chart-canvas-wrap { height: 300px; padding: 18px 20px; }

.mon-footer { background: rgba(15, 23, 42, 0.5); backdrop-filter: blur(10px); border-top: 1px solid rgba(255,255,255,0.05); padding: 14px 24px; text-align: center; font-size: 0.73rem; color: var(--text-muted); position: relative; z-index: 2; }

@keyframes pulse { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:.4;transform:scale(1.4)} }
.spin { animation: spin .8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

/* Gemini Styles */
.rio-nome-container {
  display: flex;
  align-items: center;
  gap: 12px;
}

.gemini-hover-trigger {
  position: relative;
  font-size: 0.72rem;
  font-weight: 600;
  color: #818cf8;
  cursor: help;
  padding: 4px 0;
  transition: color 0.2s ease;
}

.gemini-hover-trigger:hover {
  color: #a5b4fc;
}

.gemini-panel-wrapper {
  position: absolute;
  top: calc(100% + 5px);
  left: 0;
  z-index: 100;
  width: 650px;
  max-width: 90vw;
  background: rgba(15, 23, 42, 0.95);
  border: 1px solid rgba(99, 102, 241, 0.3);
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5), 0 0 15px rgba(99, 102, 241, 0.15);
  border-radius: var(--radius-lg);
  backdrop-filter: blur(12px);
  padding: 20px;
  cursor: default;
}

.gemini-fade-enter-active,
.gemini-fade-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.gemini-fade-enter-from,
.gemini-fade-leave-to {
  opacity: 0;
  transform: translateY(5px);
}

.gemini-skeleton {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.skeleton-header {
  display: flex;
  gap: 12px;
}
.skeleton-pill {
  width: 120px;
  height: 32px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: var(--radius-md);
  position: relative;
  overflow: hidden;
}
.skeleton-pill::after {
  content: "";
  position: absolute;
  top: 0; right: 0; bottom: 0; left: 0;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.05), transparent);
  transform: translateX(-100%);
  animation: shimmer 1.5s infinite;
}
.skeleton-body {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.skeleton-line {
  height: 14px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: var(--radius-sm);
  position: relative;
  overflow: hidden;
  width: 100%;
}
.skeleton-line::after {
  content: "";
  position: absolute;
  top: 0; right: 0; bottom: 0; left: 0;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.05), transparent);
  transform: translateX(-100%);
  animation: shimmer 1.5s infinite;
}
.skeleton-line-title {
  height: 20px;
  width: 250px;
  margin-bottom: 8px;
}
.skeleton-line-short {
  width: 60%;
}

@keyframes shimmer {
  100% { transform: translateX(100%); }
}

.gemini-card {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.gemini-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  padding-bottom: 12px;
}
.gemini-brand {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 700;
  font-size: 0.95rem;
  color: #e0e7ff;
}
.gemini-icon {
  color: #818cf8;
  animation: rotateGlow 3s linear infinite;
}

@keyframes rotateGlow {
  0% { transform: rotate(0deg); filter: drop-shadow(0 0 2px rgba(99, 102, 241, 0.4)); }
  50% { filter: drop-shadow(0 0 8px rgba(99, 102, 241, 0.8)); }
  100% { transform: rotate(360deg); filter: drop-shadow(0 0 2px rgba(99, 102, 241, 0.4)); }
}

.fallback-tag {
  background: rgba(217, 119, 6, 0.1);
  border: 1px solid rgba(217, 119, 6, 0.2);
  color: #fbbf24;
  font-size: 0.68rem;
  font-weight: 700;
  padding: 3px 8px;
  border-radius: var(--radius-full);
}

.gemini-metrics {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
}
.metric-item {
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: var(--radius-md);
  padding: 8px 12px;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all var(--transition-fast);
}
.metric-item:hover {
  background: rgba(255, 255, 255, 0.04);
  border-color: rgba(99, 102, 241, 0.2);
}
.metric-icon {
  font-size: 1.5rem;
}
.metric-content {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.metric-lbl {
  font-size: 0.60rem;
  text-transform: uppercase;
  color: var(--text-muted);
  font-weight: 700;
  letter-spacing: 0.05em;
}
.metric-val {
  font-size: 0.78rem;
  color: #fff;
  font-weight: 600;
  line-height: 1.2;
}

.gemini-info {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 24px;
}
.gemini-desc h3, .gemini-curiosidade h3 {
  font-size: 0.82rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #a5b4fc;
  margin-bottom: 8px;
}
.gemini-desc p {
  font-size: 0.875rem;
  line-height: 1.6;
  color: #cbd5e1;
  white-space: pre-line;
}
.gemini-curiosidade {
  background: rgba(99, 102, 241, 0.04);
  border: 1px solid rgba(99, 102, 241, 0.1);
  padding: 12px 16px;
  border-radius: var(--radius-md);
}
.gemini-curiosidade p {
  font-size: 0.85rem;
  color: #e2e8f0;
  line-height: 1.5;
}
.gemini-error {
  color: #fca5a5;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.2);
  padding: 16px;
  border-radius: var(--radius-md);
  text-align: center;
  font-weight: 600;
  font-size: 0.9rem;
}

@media (max-width: 900px) { .charts-grid { grid-template-columns: 1fr; } }
@media (max-width: 600px) { .upd-time { display: none; } .rio-hdr { flex-direction: column; } }
</style>