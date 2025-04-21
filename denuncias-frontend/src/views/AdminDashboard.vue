<template>
  <DashboardLayout>
    <h1 class="mb-4">Panel de Administrador</h1>
    <UserTable />
  </DashboardLayout>
</template>

<script setup>
import DashboardLayout from '@/layouts/DashboardLayout.vue'
import UserTable from '@/components/UserTable.vue'
</script>
