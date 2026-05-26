<template>
  <div class="minha-conta-page">
    <div class="page-header">
      <div class="page-header-left">
        <p class="page-label">Minha Conta</p>
        <h1 class="page-title">Dados do Usuário</h1>
      </div>
    </div>

    <div class="account-card">
      <p><strong>Nome:</strong> {{ userData.name || 'Não disponível' }}</p>
      <p><strong>Email:</strong> {{ userData.email || 'Não disponível' }}</p>
      <p><strong>Defesa Civil:</strong> {{ userData.is_defesa_civil ? 'Sim' : 'Não' }}</p>
    </div>

    <div class="account-help">
      <p>Aqui você pode acessar seus dados e navegar para o dashboard se for usuário Defesa Civil.</p>
    </div>
  </div>
</template>

<script setup>
const userData = JSON.parse(localStorage.getItem('user_data') || '{}')
</script>
