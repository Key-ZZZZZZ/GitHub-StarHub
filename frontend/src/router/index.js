import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/execution-records'
  },
  {
    path: '/execution-records',
    name: 'ExecutionRecords',
    component: () => import('../views/ExecutionRecords.vue')
  },
  {
    path: '/data-analysis',
    name: 'DataAnalysis',
    component: () => import('../views/DataAnalysis.vue')
  },
  {
    path: '/trending-projects',
    name: 'TrendingProjects',
    component: () => import('../views/TrendingProjects.vue')
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('../views/Settings.vue')
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router