<template>
  <div class="rios">

    <!-- Page Header -->
    <div class="page-header">
      <div>
        <p class="page-label">Registro Centralizado</p>
        <h1 class="page-title">Gestão de Rios</h1>
        <p class="page-subtitle">Registro centralizado de infraestrutura hidráulica e pontos de levantamento hidrológico.</p>
      </div>
      <div class="page-header-right">
        <div class="estacoes-count">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M2 6c.6.5 1.2 1 2.5 1C7 7 7 5 9.5 5c2.6 0 2.4 2 5 2 2.5 0 2.5-2 5-2 1.3 0 1.9.5 2.5 1"/></svg>
          <span>Estações Ativas</span>
          <span class="estacoes-num">{{ rios.length }}</span>
        </div>
      </div>
    </div>

    <!-- Form Split Panel -->
    <div class="form-split">
      <!-- Left Info Panel -->
      <div class="form-split-left">
        <p class="split-title">Registro de Infraestrutura</p>
        <p class="split-desc">Garanta que todos os metadados das novas estações fluviais sigam a Diretiva Técnica 402-B para conformidade ambiental.</p>
        <div class="split-checks">
          <div class="split-check">
            <div class="split-check-icon">
              <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round"><polyline points="20 6 9 17 4 12"/></svg>
            </div>
            Sincronização de Dados em Tempo Real
          </div>
        </div>
      </div>

      <!-- Right Form -->
      <div class="form-split-right">
        <p class="form-right-title">{{ form.id ? 'Editar Rio' : 'Registrar Novo Rio' }}</p>
        <div class="form-grid">
          <div class="form-group">
            <label for="rio-nome">Nome do Rio</label>
            <div class="input-wrapper">
              <svg class="input-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z"/></svg>
              <input id="rio-nome" v-model="form.nome" placeholder="ex: Rio Amazonas"/>
            </div>
          </div>
          <div class="form-group">
            <label for="rio-cidade">Cidade</label>
            <div class="input-wrapper">
              <svg class="input-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M3 21h18"/><path d="M5 21V7l8-4v18"/><path d="M19 21V11l-6-4"/></svg>
              <input id="rio-cidade" v-model="form.cidade" placeholder="ex: Manaus"/>
            </div>
          </div>
          <div class="form-group">
            <label for="rio-estado">Estado</label>
            <div class="input-wrapper select-wrapper">
              <svg class="input-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/></svg>
              <select id="rio-estado" v-model="form.estado" :disabled="loadingEstados">
                <option value="">{{ loadingEstados ? 'Carregando...' : 'ex: AM' }}</option>
                <option v-for="uf in estados" :key="uf.sigla" :value="uf.sigla">{{ uf.nome }} ({{ uf.sigla }})</option>
              </select>
            </div>
          </div>
          <div class="form-group">
            <label for="rio-risco">Nível de Risco de Enchente</label>
            <select id="rio-risco" v-model="form.risco_inundacao">
              <option value="">Selecionar Nível</option>
              <option value="1">🟢 Baixo</option>
              <option value="2">🟡 Médio</option>
              <option value="3">🔴 Alto</option>
              <option value="4">🔴 Muito Alto</option>
            </select>
          </div>
        </div>
        <div class="form-actions">
          <button class="btn-primary" @click="save" :disabled="saving">
            <svg v-if="saving" class="spinner" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10" stroke-dasharray="32" stroke-dashoffset="32"><animateTransform attributeName="transform" type="rotate" from="0 12 12" to="360 12 12" dur="0.8s" repeatCount="indefinite"/></circle></svg>
            {{ saving ? 'Salvando...' : form.id ? 'Atualizar Estação' : 'Registrar Estação' }}
            <svg v-if="!saving" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>
          </button>
          <button class="btn-secondary" v-if="form.id" @click="reset">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
            Cancelar
          </button>
        </div>
      </div>
    </div>



    <!-- Table Card -->
    <div class="table-section">
      <div class="table-header">
        <h2 class="table-title">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M2 6c.6.5 1.2 1 2.5 1C7 7 7 5 9.5 5c2.6 0 2.4 2 5 2 2.5 0 2.5-2 5-2 1.3 0 1.9.5 2.5 1"/><path d="M2 12c.6.5 1.2 1 2.5 1 2.5 0 2.5-2 5-2 2.6 0 2.4 2 5 2 2.5 0 2.5-2 5-2 1.3 0 1.9.5 2.5 1"/><path d="M2 18c.6.5 1.2 1 2.5 1 2.5 0 2.5-2 5-2 2.6 0 2.4 2 5 2 2.5 0 2.5-2 5-2 1.3 0 1.9.5 2.5 1"/></svg>
          Lista de Rios
        </h2>
        <span class="table-count">{{ rios.length }} registros</span>
      </div>

      <div class="table-wrapper">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Nome</th>
              <th>Cidade</th>
              <th>Estado</th>
              <th>Risco</th>
              <th>Ações</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="rios.length === 0">
              <td colspan="6" class="empty-state">
                <div class="empty-content">
                  <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"><path d="M2 6c.6.5 1.2 1 2.5 1C7 7 7 5 9.5 5c2.6 0 2.4 2 5 2 2.5 0 2.5-2 5-2 1.3 0 1.9.5 2.5 1"/><path d="M2 12c.6.5 1.2 1 2.5 1 2.5 0 2.5-2 5-2 2.6 0 2.4 2 5 2 2.5 0 2.5-2 5-2 1.3 0 1.9.5 2.5 1"/></svg>
                  <p>Nenhum rio cadastrado</p>
                  <span>Use o formulário acima para cadastrar o primeiro rio</span>
                </div>
              </td>
            </tr>
            <tr v-for="rio in rios" :key="rio.id" class="table-row-animated">
              <td class="td-id">#{{ rio.id }}</td>
              <td class="td-name">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--accent)" stroke-width="2" stroke-linecap="round"><path d="M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z"/></svg>
                {{ rio.nome }}
              </td>
              <td>{{ rio.cidade }}</td>
              <td><span class="state-badge">{{ rio.estado }}</span></td>
              <td>
                <span class="badge" :class="getBadgeClass(rio.risco_inundacao)">
                  <span class="badge-dot"></span>
                  {{ getRiskLabel(rio.risco_inundacao) }}
                </span>
              </td>
              <td class="td-actions">
                <button class="btn-action btn-action--pontos" @click="togglePontos(rio)" :title="expandedRio === rio.id ? 'Fechar Pontos' : 'Ver Pontos de Risco'" :class="{ active: expandedRio === rio.id }">
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M12 22s-8-4.5-8-11.8A8 8 0 0 1 12 2a8 8 0 0 1 8 8.2c0 7.3-8 11.8-8 11.8z"/><circle cx="12" cy="10" r="3"/></svg>
                </button>
                <button class="btn-action btn-action--edit" @click="edit(rio)" title="Editar">
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z"/></svg>
                </button>
                <button class="btn-action btn-action--delete" @click="remove(rio.id)" title="Excluir">
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Painel de Pontos de Risco (1:N) -->
    <div v-if="expandedRio" class="pontos-section">
      <div class="pontos-header">
        <h2 class="pontos-title">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M12 22s-8-4.5-8-11.8A8 8 0 0 1 12 2a8 8 0 0 1 8 8.2c0 7.3-8 11.8-8 11.8z"/><circle cx="12" cy="10" r="3"/></svg>
          Pontos de Risco — {{ rios.find(r => r.id === expandedRio)?.nome }}
        </h2>
        <button class="btn-secondary btn-sm" @click="expandedRio = null">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
          Fechar
        </button>
      </div>

      <!-- Form Ponto Risco (somente Defesa Civil) -->
      <div v-if="isDefesaCivil" class="ponto-form">
        <h3 class="ponto-form-title">{{ pontoForm.id ? 'Editar Ponto' : 'Novo Ponto de Risco' }}</h3>
        <div class="ponto-form-grid">
          <div class="form-group form-group--wide">
            <label>Nome do Ponto de Risco</label>
            <input v-model="pontoForm.descricao" placeholder="Ex: Ponto Morumbi, Margem Norte do Rio" />
          </div>
          <div class="form-group">
            <label>Latitude</label>
            <input v-model.number="pontoForm.latitude" type="number" step="0.000001" placeholder="Ex: -23.550520" />
          </div>
          <div class="form-group">
            <label>Longitude</label>
            <input v-model.number="pontoForm.longitude" type="number" step="0.000001" placeholder="Ex: -46.633309" />
          </div>
          <div class="form-group">
            <label>Nível de Risco</label>
            <select v-model="pontoForm.nivel_risco">
              <option value="">Selecione...</option>
              <option value="1">🟢 Baixo</option>
              <option value="2">🟡 Médio</option>
              <option value="3">🔴 Alto</option>
            </select>
          </div>
        </div>
        <div class="form-actions">
          <button class="btn-primary" @click="savePonto" :disabled="savingPonto">
            <svg v-if="savingPonto" class="spinner" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10" stroke-dasharray="32" stroke-dashoffset="32"><animateTransform attributeName="transform" type="rotate" from="0 12 12" to="360 12 12" dur="0.8s" repeatCount="indefinite"/></circle></svg>
            {{ savingPonto ? 'Salvando...' : pontoForm.id ? 'Atualizar' : 'Adicionar Ponto' }}
          </button>
          <button v-if="pontoForm.id" class="btn-secondary" @click="resetPonto">Cancelar</button>
        </div>
      </div>

      <!-- Aviso para usuarios sem permissao -->
      <div v-if="!isDefesaCivil" class="ponto-aviso">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
        Apenas usuários Defesa Civil podem cadastrar pontos de risco. Você pode apenas visualizá-los.
      </div>

      <!-- Lista Pontos -->
      <div v-if="loadingPontos" class="pontos-loading">Carregando pontos...</div>
      <div v-else-if="pontos.length === 0" class="pontos-empty">Nenhum ponto de risco cadastrado para este rio.</div>
      <div v-else class="pontos-list">
        <div v-for="p in pontos" :key="p.id" class="ponto-card" :class="getPontoClass(p.nivel_risco)">
          <div class="ponto-card-top">
            <span class="ponto-nivel" :class="getPontoClass(p.nivel_risco)">
              {{ p.nivel_risco === 1 ? '🟢 Baixo' : p.nivel_risco === 2 ? '🟡 Médio' : '🔴 Alto' }}
            </span>
            <div v-if="isDefesaCivil" class="ponto-actions">
              <button class="btn-action btn-action--edit" @click="editPonto(p)" title="Editar"><svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z"/></svg></button>
              <button class="btn-action btn-action--delete" @click="removePonto(p.id)" title="Excluir"><svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg></button>
            </div>
          </div>
          <p class="ponto-desc">{{ p.descricao }}</p>
          <div class="ponto-coords">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>
            {{ p.latitude }}, {{ p.longitude }}
          </div>
        </div>
      </div>
    </div>

    <ConfirmModal ref="confirmRef" />
  </div>
</template>

<script setup>
import { ref, inject, onMounted } from 'vue'
import api from '../services/api'
import ConfirmModal from '@/components/ConfirmModal.vue'

const toast = inject('toast')
const confirmRef = ref(null)

// Permissão: apenas Defesa Civil pode criar/editar/excluir pontos de risco
const isDefesaCivil = ref(false)

// --- Pontos de Risco ---
const expandedRio = ref(null)
const pontos = ref([])
const loadingPontos = ref(false)
const savingPonto = ref(false)
const pontoForm = ref({ id: null, latitude: '', longitude: '', descricao: '', nivel_risco: '' })

const togglePontos = async (rio) => {
  if (expandedRio.value === rio.id) {
    expandedRio.value = null
    pontos.value = []
    return
  }
  expandedRio.value = rio.id
  await loadPontos(rio.id)
}

const loadPontos = async (rioId) => {
  loadingPontos.value = true
  try {
    const res = await api.getPontosRisco(rioId)
    pontos.value = Array.isArray(res.data) ? res.data : res.data.results || []
  } catch (err) {
    toast?.error('Erro', 'Não foi possível carregar os pontos de risco.')
  } finally {
    loadingPontos.value = false
  }
}

const savePonto = async () => {
  if (!pontoForm.value.latitude || !pontoForm.value.longitude || !pontoForm.value.nivel_risco || !pontoForm.value.descricao) {
    toast?.warning('Campos obrigatórios', 'Preencha todos os campos do ponto de risco.')
    return
  }
  savingPonto.value = true
  try {
    const data = { ...pontoForm.value, nivel_risco: parseInt(pontoForm.value.nivel_risco) }
    if (pontoForm.value.id) {
      await api.updatePontoRisco(pontoForm.value.id, data)
      toast?.success('Ponto atualizado', 'O ponto de risco foi atualizado.')
    } else {
      await api.createPontoRisco(expandedRio.value, data)
      toast?.success('Ponto adicionado', 'Novo ponto de risco cadastrado.')
    }
    resetPonto()
    await loadPontos(expandedRio.value)
  } catch (err) {
    const msg = err.response?.data?.detail || err.response?.data?.descricao?.[0] || 'Erro ao salvar ponto.'
    toast?.error('Erro', msg)
  } finally {
    savingPonto.value = false
  }
}

const editPonto = (p) => {
  pontoForm.value = { ...p }
}

const resetPonto = () => {
  pontoForm.value = { id: null, latitude: '', longitude: '', descricao: '', nivel_risco: '' }
}

const removePonto = async (id) => {
  const confirmed = await confirmRef.value?.show({
    title: 'Excluir ponto de risco',
    message: 'Tem certeza que deseja excluir este ponto? Esta ação não pode ser desfeita.',
    confirmText: 'Sim, excluir',
    type: 'danger'
  })
  if (confirmed) {
    try {
      await api.deletePontoRisco(id)
      toast?.success('Excluído', 'Ponto de risco removido.')
      await loadPontos(expandedRio.value)
    } catch (err) {
      toast?.error('Erro', 'Não foi possível excluir o ponto.')
    }
  }
}

const getPontoClass = (nivel) => {
  if (nivel === 1) return 'ponto--low'
  if (nivel === 2) return 'ponto--medium'
  return 'ponto--high'
}

const rios = ref([])
const saving = ref(false)
const form = ref({ id: null, nome: '', cidade: '', estado: '', risco_inundacao: '' })
const estados = ref([])
const loadingEstados = ref(false)

const load = async () => {
  try {
    const res = await api.getRios()
    rios.value = Array.isArray(res.data) ? res.data : res.data.results || []
  } catch (err) {
    toast?.error('Erro ao carregar', 'Não foi possível carregar a lista de rios.')
  }
}

const save = async () => {
  if (!form.value.nome || !form.value.cidade || !form.value.estado || !form.value.risco_inundacao) {
    toast?.warning('Campos obrigatórios', 'Preencha todos os campos antes de salvar.')
    return
  }
  saving.value = true
  try {
    const data = { ...form.value }
    data.risco_inundacao = parseInt(data.risco_inundacao)
    if (form.value.id) {
      await api.updateRio(form.value.id, data)
      toast?.success('Rio atualizado', `"${form.value.nome}" foi atualizado com sucesso.`)
    } else {
      await api.createRio(data)
      toast?.success('Rio cadastrado', `"${form.value.nome}" foi adicionado ao monitoramento.`)
    }
    reset()
    load()
  } catch (err) {
    toast?.error('Erro ao salvar', 'Ocorreu um erro ao salvar os dados do rio.')
  } finally {
    saving.value = false
  }
}

const edit = (rio) => {
  form.value = { ...rio }
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const remove = async (id) => {
  const confirmed = await confirmRef.value?.show({
    title: 'Excluir rio',
    message: 'Tem certeza que deseja excluir este rio? Esta ação não pode ser desfeita.',
    confirmText: 'Sim, excluir',
    type: 'danger'
  })

  if (confirmed) {
    try {
      await api.deleteRio(id)
      toast?.success('Rio excluído', 'O rio foi removido do monitoramento.')
      load()
    } catch (err) {
      toast?.error('Erro ao excluir', 'Não foi possível excluir o rio.')
    }
  }
}

const reset = () => {
  form.value = { id: null, nome: '', cidade: '', estado: '', risco_inundacao: '' }
}

const getBadgeClass = (risco) => {
  if (risco === 1) return 'badge--low'
  if (risco === 2) return 'badge--medium'
  if (risco === 3 || risco === 4) return 'badge--high'
  return 'badge--low'
}

const getRiskLabel = (risco) => {
  const labels = { 1: 'Baixo', 2: 'Médio', 3: 'Alto', 4: 'Muito Alto' }
  return labels[risco] || 'Desconhecido'
}

onMounted(async () => {
  load()
  try {
    const res = await api.me()
    isDefesaCivil.value = !!res.data.is_defesa_civil
  } catch (e) {
    isDefesaCivil.value = false
  }
  // Buscar estados brasileiros via API IBGE
  loadingEstados.value = true
  try {
    const res = await fetch('https://servicodados.ibge.gov.br/api/v1/localidades/estados?orderBy=nome')
    const data = await res.json()
    estados.value = data.map(e => ({ sigla: e.sigla, nome: e.nome }))
  } catch {
    // Fallback manual se API falhar
    estados.value = [
      {sigla:'AC',nome:'Acre'},{sigla:'AL',nome:'Alagoas'},{sigla:'AP',nome:'Amapá'},
      {sigla:'AM',nome:'Amazonas'},{sigla:'BA',nome:'Bahia'},{sigla:'CE',nome:'Ceará'},
      {sigla:'DF',nome:'Distrito Federal'},{sigla:'ES',nome:'Espírito Santo'},
      {sigla:'GO',nome:'Goiás'},{sigla:'MA',nome:'Maranhão'},{sigla:'MT',nome:'Mato Grosso'},
      {sigla:'MS',nome:'Mato Grosso do Sul'},{sigla:'MG',nome:'Minas Gerais'},
      {sigla:'PA',nome:'Pará'},{sigla:'PB',nome:'Paraíba'},{sigla:'PR',nome:'Paraná'},
      {sigla:'PE',nome:'Pernambuco'},{sigla:'PI',nome:'Piauí'},{sigla:'RJ',nome:'Rio de Janeiro'},
      {sigla:'RN',nome:'Rio Grande do Norte'},{sigla:'RS',nome:'Rio Grande do Sul'},
      {sigla:'RO',nome:'Rondônia'},{sigla:'RR',nome:'Roraima'},{sigla:'SC',nome:'Santa Catarina'},
      {sigla:'SP',nome:'São Paulo'},{sigla:'SE',nome:'Sergipe'},{sigla:'TO',nome:'Tocantins'}
    ]
  } finally {
    loadingEstados.value = false
  }
})
</script>

<style scoped>
.rios { display: flex; flex-direction: column; gap: 24px; animation: fadeInUp 0.35s ease-out; }

.page-header { display: flex; align-items: flex-end; justify-content: space-between; flex-wrap: wrap; gap: 12px; }
.page-label { font-size: 0.68rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: var(--text-muted); margin-bottom: 4px; }
.page-title { font-size: 1.75rem; font-weight: 800; letter-spacing: -0.02em; }
.page-subtitle { color: var(--text-secondary); font-size: 0.875rem; margin-top: 4px; }
.page-header-right { display: flex; align-items: center; gap: 10px; }
.estacoes-count { display: flex; align-items: center; gap: 8px; padding: 8px 16px; background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius-md); font-size: 0.78rem; color: var(--text-secondary); font-weight: 500; }
.estacoes-count svg { color: var(--accent); }
.estacoes-num { font-size: 1.1rem; font-weight: 800; color: var(--text-primary); margin-right: 2px; }

/* Form Section Split */
.form-split {
  display: grid;
  grid-template-columns: 280px 1fr;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-xl);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
}

.form-split-left {
  background: var(--bg-elevated);
  padding: 32px 28px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.split-title { font-size: 1.3rem; font-weight: 800; line-height: 1.3; }
.split-desc { font-size: 0.8rem; color: var(--text-secondary); line-height: 1.6; }

.split-checks { display: flex; flex-direction: column; gap: 12px; margin-top: 4px; }
.split-check { display: flex; align-items: center; gap: 10px; font-size: 0.78rem; color: var(--text-secondary); }
.split-check-icon { width: 20px; height: 20px; border-radius: 50%; background: var(--accent-soft); color: var(--accent); display: flex; align-items: center; justify-content: center; flex-shrink: 0; }

.form-split-right {
  padding: 28px 32px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-right-title { font-size: 0.68rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: var(--text-muted); margin-bottom: 2px; }

.form-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 14px; }
.form-group { display: flex; flex-direction: column; gap: 5px; }
.form-group label { font-size: 0.72rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.06em; color: var(--text-muted); }

.input-wrapper { position: relative; }
.input-icon { position: absolute; left: 12px; top: 50%; transform: translateY(-50%); color: var(--text-muted); pointer-events: none; }
.input-wrapper input { padding-left: 38px; }
.select-wrapper select { width: 100%; padding: 10px 14px 10px 38px; border-radius: var(--radius-md); border: 1px solid var(--border); background: var(--bg-tertiary); color: var(--text-primary); font-size: 0.875rem; font-family: inherit; transition: border-color 0.2s; appearance: none; cursor: pointer; }
.select-wrapper select:focus { outline: none; border-color: var(--accent); box-shadow: 0 0 0 3px var(--accent-soft); }
.select-wrapper select:disabled { opacity: 0.5; cursor: not-allowed; }

.form-actions { display: flex; gap: 10px; }
.btn-primary { display: inline-flex; align-items: center; gap: 8px; background: var(--accent); border: 1px solid var(--accent-hover); color: white; padding: 10px 22px; border-radius: var(--radius-md); font-weight: 700; font-size: 0.82rem; letter-spacing: 0.04em; transition: all var(--transition-normal); text-transform: uppercase; }
.btn-primary:hover:not(:disabled) { background: var(--accent-hover); border-color: var(--accent-hover); box-shadow: var(--shadow-glow); transform: translateY(-1px); }
.btn-secondary { display: inline-flex; align-items: center; gap: 8px; background: transparent; color: var(--text-secondary); border: 1px solid var(--border); padding: 10px 18px; border-radius: var(--radius-md); font-weight: 600; font-size: 0.82rem; transition: all var(--transition-fast); }
.btn-secondary:hover:not(:disabled) { background: var(--bg-elevated); color: var(--text-primary); transform: none; }
.btn-sm { padding: 6px 14px; font-size: 0.78rem; }
.spinner { animation: spin 0.8s linear infinite; }

/* Table */
.table-section { background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius-xl); overflow: hidden; }
.table-header { display: flex; align-items: center; justify-content: space-between; padding: 18px 22px; border-bottom: 1px solid var(--border-light); }
.table-title { display: flex; align-items: center; gap: 10px; font-size: 0.95rem; font-weight: 700; }
.table-title svg { color: var(--accent); }
.table-count { font-size: 0.72rem; color: var(--text-muted); font-weight: 600; background: var(--bg-elevated); padding: 3px 10px; border-radius: var(--radius-full); }
.table-wrapper { overflow-x: auto; }
.td-id { font-family: var(--font-mono); font-size: 0.78rem; color: var(--text-muted); }
.td-name { display: flex; align-items: center; gap: 8px; font-weight: 600; }
.state-badge { display: inline-block; padding: 2px 8px; background: var(--bg-elevated); border-radius: var(--radius-full); font-size: 0.72rem; font-weight: 700; color: var(--text-secondary); letter-spacing: 0.04em; }
.td-actions { display: flex; gap: 6px; white-space: nowrap; }
.btn-action { display: inline-flex; align-items: center; justify-content: center; width: 30px; height: 30px; border-radius: var(--radius-sm); border: 1px solid var(--border); background: var(--bg-elevated); cursor: pointer; transition: all var(--transition-fast); }
.btn-action--pontos { color: var(--text-muted); }
.btn-action--pontos:hover { background: var(--accent-soft); border-color: var(--accent); color: var(--accent); transform: none; }
.btn-action--pontos.active { background: var(--accent-soft); border-color: var(--accent); color: var(--accent); }
.btn-action--edit { color: var(--accent); }
.btn-action--edit:hover { background: var(--accent-soft); border-color: var(--accent); transform: none; }
.btn-action--delete { color: var(--risk-high); }
.btn-action--delete:hover { background: var(--risk-high-bg); border-color: var(--risk-high); transform: none; }
.empty-state { text-align: center; padding: 48px 24px !important; }
.empty-content { display: flex; flex-direction: column; align-items: center; gap: 8px; color: var(--text-muted); }
.empty-content p { font-weight: 600; color: var(--text-secondary); }
.empty-content span { font-size: 0.82rem; }
.table-row-animated { animation: fadeInUp 0.3s ease-out both; }

/* Pontos Section */
.pontos-section { background: var(--bg-card); border: 1px solid var(--border-accent); border-radius: var(--radius-xl); overflow: hidden; animation: fadeInUp 0.3s ease-out; }
.pontos-header { display: flex; align-items: center; justify-content: space-between; padding: 18px 22px; border-bottom: 1px solid var(--border); }
.pontos-title { display: flex; align-items: center; gap: 10px; font-size: 0.95rem; font-weight: 700; }
.pontos-title svg { color: var(--accent); }
.ponto-form { padding: 20px 22px; border-bottom: 1px solid var(--border-light); background: var(--bg-secondary); }
.ponto-form-title { font-size: 0.82rem; font-weight: 700; color: var(--text-secondary); margin-bottom: 14px; text-transform: uppercase; letter-spacing: 0.06em; }
.ponto-form-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; margin-bottom: 14px; }
.form-group--wide { grid-column: 1 / -1; }
.ponto-aviso { display: flex; align-items: center; gap: 10px; padding: 12px 22px; background: var(--accent-soft); color: var(--accent); font-size: 0.82rem; border-bottom: 1px solid var(--border-light); }
.pontos-loading { padding: 20px 22px; color: var(--text-muted); font-size: 0.82rem; }
.pontos-empty { padding: 32px 22px; color: var(--text-muted); font-size: 0.85rem; text-align: center; }
.pontos-list { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 14px; padding: 20px 22px; }
.ponto-card { background: var(--bg-secondary); border: 1px solid var(--border); border-radius: var(--radius-lg); padding: 16px; border-left: 3px solid transparent; animation: fadeInUp 0.3s ease-out; }
.ponto-card.ponto--high { border-left-color: var(--risk-high); }
.ponto-card.ponto--medium { border-left-color: var(--risk-medium); }
.ponto-card.ponto--low { border-left-color: var(--risk-low); }
.ponto-card-top { display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px; }
.ponto-nivel { font-size: 0.72rem; font-weight: 700; padding: 3px 9px; border-radius: var(--radius-full); }
.ponto-nivel.ponto--high { background: var(--risk-high-bg); color: var(--risk-high); }
.ponto-nivel.ponto--medium { background: var(--risk-medium-bg); color: var(--risk-medium); }
.ponto-nivel.ponto--low { background: var(--risk-low-bg); color: var(--risk-low); }
.ponto-actions { display: flex; gap: 5px; }
.ponto-desc { font-size: 0.85rem; font-weight: 600; color: var(--text-primary); margin-bottom: 8px; }
.ponto-coords { display: flex; align-items: center; gap: 5px; font-size: 0.72rem; color: var(--text-muted); font-family: var(--font-mono); }

@media (max-width: 900px) { .form-split { grid-template-columns: 1fr; } .form-split-left { display: none; } }
@media (max-width: 768px) { .form-grid { grid-template-columns: 1fr; } .form-actions { flex-direction: column; } }


/* Page Header */
.page-header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
}

.page-title {
  font-size: 1.75rem;
  font-weight: 800;
  color: var(--text-primary);
  letter-spacing: -0.02em;
}

.page-subtitle {
  color: var(--text-secondary);
  font-size: 0.9rem;
  margin-top: 4px;
}

/* Form Section */
.form-section {
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: var(--radius-xl);
  padding: 36px 32px;
  position: relative;
  overflow: hidden;
  box-shadow: var(--shadow-sm);
  transition: transform var(--transition-normal), box-shadow var(--transition-normal);
}

.form-section:hover {
  box-shadow: var(--shadow-md);
}

.form-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: var(--accent-gradient);
}

</style>