import { createRouter, createWebHashHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import RegistrationPage from '../views/RegistrationPage.vue'
import LoginPage from '@/views/LoginPage.vue'
import CreateCampaign from '@/views/CreateCampaign.vue'
import EditCampiagn from '@/views/EditCampiagn.vue'
import MyCampaigns from '@/views/MyCampaigns.vue'

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView
  },
  {
    path: '/register',
    name: 'registration',
    component: RegistrationPage
  },
  {
    path: '/login',
    name: 'login',
    component: LoginPage
  },
  {
    path: '/about',
    name: 'about',
    // route level code-splitting
    // this generates a separate chunk (about.[hash].js) for this route
    // which is lazy-loaded when the route is visited.
    component: () => import(/* webpackChunkName: "about" */ '../views/AboutView.vue')
  },
  {
    path: '/create-campaign',
    name: 'createcampaign',
    component: CreateCampaign
  },
  {
    path: '/edit-campaign/:id',
    name: 'editcampaign',
    component: EditCampiagn
  },
  {
    path: '/my-campaigns',
    name: 'mycampaigns',
    component: MyCampaigns
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

export default router
