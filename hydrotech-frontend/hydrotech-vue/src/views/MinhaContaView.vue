<template>
  <div class="minha-conta">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">Minha Conta</h1>
        <p class="page-subtitle">Gerencie suas informacoes pessoais e credenciais de acesso</p>
      </div>
    </div>

    <!-- Profile Section -->
    <div class="profile-section">
      <div class="profile-card-header">
        <div class="profile-avatar" :style="{ background: avatarColor }">
          {{ initials }}
        </div>
        <div class="profile-summary">
          <h2>{{ name }}</h2>
          <span class="badge" :class="userData.is_defesa_civil ? 'badge--admin' : 'badge--user'">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
            {{ userData.is_defesa_civil ? 'Defesa Civil Admin' : 'Usuario Comum' }}
          </span>
        </div>
      </div>

      <div class="info-grid">
        <div class="info-group">
          <label>Nome Completo</label>
          <div class="info-value">
            <svg class="info-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
            <span>{{ name }}</span>
          </div>
        </div>

        <div class="info-group">
          <label>E-mail de Acesso</label>
          <div class="info-value">
            <svg class="info-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><rect width="20" height="16" x="2" y="4" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/></svg>
            <span>{{ email }}</span>
          </div>
        </div>

        <div class="info-group">
          <label>Data de Nascimento</label>
          <div class="info-value">
            <svg class="info-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><rect width="18" height="18" x="3" y="4" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
            <span>{{ formattedBirthDate }}</span>
          </div>
        </div>

        <div class="info-group">
          <label>Nivel de Permissao</label>
          <div class="info-value">
            <svg class="info-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><rect width="18" height="11" x="3" y="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
            <span>{{ userData.is_defesa_civil ? 'Administrador Geral' : 'Operador Padrao' }}</span>
          </div>
        </div>
      </div>

      <div class="profile-footer-tip">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>
        <span>Para alterar a sua senha ou atualizar os seus dados cadastrais, por favor entre em contato com o administrador do sistema.</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const userData = JSON.parse(localStorage.getItem('user_data') || '{}')

const name = computed(() => userData.nome || userData.name || 'Nao disponivel')
const email = computed(() => userData.email || 'Nao disponivel')

const formattedBirthDate = computed(() => {
  const dateStr = userData.data_nascimento || userData.birth_date
  if (!dateStr) return '—'
  const date = new Date(dateStr)
  return date.toLocaleDateString('pt-BR')
})

const initials = computed(() => {
  const n = name.value
  if (!n || n === 'Nao disponivel') return '?'
  const parts = n.trim().split(' ')
  if (parts.length >= 2) return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase()
  return parts[0][0].toUpperCase()
})

const avatarColors = [
  'linear-gradient(135deg, #667eea, #764ba2)',
  'linear-gradient(135deg, #f093fb, #f5576c)',
  'linear-gradient(135deg, #4facfe, #00f2fe)',
  'linear-gradient(135deg, #43e97b, #38f9d7)',
  'linear-gradient(135deg, #fa709a, #fee140)'
]

const avatarColor = computed(() => {
  const n = name.value
  let hash = 0
  for (let i = 0; i < n.length; i++) hash = n.charCodeAt(i) + ((hash << 5) - hash)
  return avatarColors[Math.abs(hash) % avatarColors.length]
})
</script>

<style scoped>
.minha-conta {
  display: flex;
  flex-direction: column;
  gap: 24px;
  animation: fadeInUp 0.4s ease-out;
}

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

/* Profile Section */
.profile-section {
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: var(--radius-xl);
  padding: 40px;
  position: relative;
  overflow: hidden;
  box-shadow: var(--shadow-sm);
  transition: box-shadow var(--transition-normal);
}

.profile-section:hover {
  box-shadow: var(--shadow-md);
}

.profile-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: var(--accent-gradient);
}

.profile-card-header {
  display: flex;
  align-items: center;
  gap: 24px;
  margin-bottom: 36px;
  padding-bottom: 24px;
  border-bottom: 1px solid var(--border-light);
}

.profile-avatar {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 80px;
  height: 80px;
  border-radius: var(--radius-full);
  color: white;
  font-size: 1.75rem;
  font-weight: 800;
  flex-shrink: 0;
  box-shadow: var(--shadow-sm);
}

.profile-summary {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.profile-summary h2 {
  font-size: 1.5rem;
  font-weight: 800;
  color: var(--text-primary);
  letter-spacing: -0.01em;
}

.badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  align-self: flex-start;
  padding: 4px 12px;
  border-radius: var(--radius-full);
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.02em;
}

.badge--admin {
  background: var(--accent-soft);
  color: var(--accent);
}

.badge--user {
  background: var(--bg-tertiary);
  color: var(--text-secondary);
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
  margin-bottom: 32px;
}

.info-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.info-group label {
  font-size: 0.8rem;
  font-weight: 700;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.info-value {
  display: flex;
  align-items: center;
  gap: 12px;
  background: var(--card-bg, var(--bg-tertiary));
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 14px 16px;
  color: var(--text-primary);
  font-size: 0.95rem;
  font-weight: 600;
}

.info-icon {
  color: var(--accent);
  flex-shrink: 0;
}

.profile-footer-tip {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-lg);
  padding: 16px 20px;
  color: var(--text-secondary);
  font-size: 0.85rem;
  line-height: 1.4;
}

.profile-footer-tip svg {
  color: var(--accent);
  flex-shrink: 0;
  margin-top: 2px;
}

/* Responsive */
@media (max-width: 768px) {
  .profile-card-header {
    flex-direction: column;
    text-align: center;
  }

  .profile-summary {
    align-items: center;
  }

  .info-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }
}
</style>
