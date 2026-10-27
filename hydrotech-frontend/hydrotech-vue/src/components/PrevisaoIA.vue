<template>
  <section class="forecast" aria-label="Previsão de nível por inteligência artificial">
    <h4>Previsão por IA · Gemini</h4>
    <p class="description">Analise as leituras registradas deste ponto para estimar o tempo até o limite crítico.</p>
    <div class="actions">
      <button :disabled="loading" @click="analisar(false)">{{ loading ? 'Analisando…' : 'Analisar medições' }}</button>
      <button class="secondary" :disabled="loading" @click="analisar(true)">Demonstração com dados simulados</button>
    </div>
    <p v-if="error" role="alert" class="error">{{ error }}</p>
    <div v-if="result" aria-live="polite">
      <p class="source">{{ result.origem === 'demonstracao' ? 'DEMONSTRAÇÃO — dados simulados, sem medições reais' : 'Histórico de medições registrado no servidor' }}</p>
      <p v-if="result.ia" class="eta">{{ formatHours(result.ia.horas_estimadas) }} até o limite crítico, se a tendência continuar</p>
      <p v-else>{{ statusText }}</p>
      <dl v-if="result.nivel_atual !== null">
        <div><dt>Nível atual</dt><dd>{{ result.nivel_atual }} m</dd></div>
        <div><dt>Limite crítico</dt><dd>{{ result.limite_critico }} m</dd></div>
        <div v-if="result.taxa_m_h !== null"><dt>Tendência</dt><dd>{{ result.tendencia }} ({{ result.taxa_m_h }} m/h)</dd></div>
      </dl>
      <template v-if="result.ia">
        <p>{{ result.ia.justificativa }}</p>
        <p class="description">{{ result.ia.limitacoes }}</p>
        <small>{{ result.ia.modelo }} · {{ new Date(result.gerado_em).toLocaleString('pt-BR') }}</small>
      </template>
      <p class="notice">{{ result.aviso }}</p>
    </div>
  </section>
</template>

<script setup>
import { computed, ref } from 'vue'
import api from '@/services/api'
const props = defineProps({ pontoId: { type: Number, required: true } })
const loading = ref(false)
const result = ref(null)
const error = ref('')
const statusText = computed(() => {
  if (result.value?.status_ia === 'nao_configurada') return 'Gemini não configurado no servidor. A previsão por IA está indisponível.'
  return {
    dados_insuficientes: 'Dados insuficientes: registre pelo menos 6 leituras cobrindo 20 minutos.',
    dados_desatualizados: 'Leituras desatualizadas. A última leitura deve ter no máximo 30 minutos.',
    limite_atingido: 'O nível registrado já atingiu o limite crítico.',
    sem_cruzamento: 'Sem projeção de cruzamento na tendência atual; isso não garante segurança.',
    fora_do_horizonte: 'Cruzamento projetado além do horizonte de 24 horas. Aguarde novas leituras.',
  }[result.value?.status] || 'Previsão indisponível.'
})
function formatHours(hours) {
  const minutes = Math.max(1, Math.round(hours * 60))
  return minutes < 60 ? `Cerca de ${minutes} min` : `Cerca de ${Math.floor(minutes / 60)} h ${minutes % 60} min`
}
async function analisar(demo) {
  loading.value = true
  error.value = ''
  result.value = null
  try {
    result.value = (await api.getPrevisao(props.pontoId, demo)).data
  } catch (err) {
    error.value = err.response?.status === 429 ? 'Muitas consultas. Aguarde um minuto.' :
      err.response?.data?.detail || 'Não foi possível consultar a IA. Verifique a conexão e tente novamente.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.forecast { padding: 18px; border-top: 1px solid var(--border); color: var(--text-primary); }
h4 { margin-bottom: 8px; }
p { margin: 10px 0; font-size: .85rem; }
.description, small { color: var(--text-secondary); }
.actions { display: flex; flex-wrap: wrap; gap: 8px; margin: 12px 0; }
button { background: var(--accent); color: white; padding: 10px 12px; }
button.secondary { background: var(--bg-elevated); color: var(--text-primary); border: 1px solid var(--border); }
button:disabled { opacity: .5; cursor: wait; }
.source { color: var(--risk-medium); font-weight: 700; }
.eta { font-size: 1.1rem; font-weight: 700; }
dl { display: flex; flex-wrap: wrap; gap: 16px; margin: 14px 0; font-size: .8rem; }
dt { color: var(--text-secondary); } dd { margin: 4px 0; font-weight: 600; }
.error { color: var(--risk-high); } .notice { color: var(--text-secondary); font-size: .75rem; }
</style>
