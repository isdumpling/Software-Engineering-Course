import Vue from 'vue'
import VueRouter from 'vue-router'
import store from '../store'

import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import ForgotPassword from '../views/ForgotPassword.vue'
import ResetPassword from '../views/ResetPassword.vue'
import Home from '../views/Home.vue'
import Chat from '../views/Chat.vue'
import History from '../views/History.vue'

import AdminLayout from '../views/admin/AdminLayout.vue'
import AdminDashboard from '../views/admin/AdminDashboard.vue'
import AdminCourses from '../views/admin/AdminCourses.vue'
import AdminRetrievalTest from '../views/admin/AdminRetrievalTest.vue'
import AdminSystem from '../views/admin/AdminSystem.vue'

Vue.use(VueRouter)

const routes = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { requiresGuest: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: Register,
    meta: { requiresGuest: true }
  },
  {
    path: '/forgot-password',
    name: 'ForgotPassword',
    component: ForgotPassword,
    meta: { requiresGuest: true }
  },
  {
    path: '/reset-password',
    name: 'ResetPassword',
    component: ResetPassword,
    meta: { requiresGuest: true }
  },
  {
    path: '/home',
    name: 'Home',
    component: Home,
    meta: { requiresAuth: true }
  },
  {
    path: '/chat/:courseId',
    name: 'Chat',
    component: Chat,
    meta: { requiresAuth: true },
    props: true
  },
  {
    path: '/history',
    name: 'History',
    component: History,
    meta: { requiresAuth: true }
  },
  {
    path: '/admin',
    component: AdminLayout,
    meta: { requiresAuth: true, requiresAdmin: true },
    redirect: '/admin/dashboard',
    children: [
      { path: 'dashboard', name: 'AdminDashboard', component: AdminDashboard },
      { path: 'courses', name: 'AdminCourses', component: AdminCourses },
      { path: 'retrieval-test', name: 'AdminRetrievalTest', component: AdminRetrievalTest },
      { path: 'system', name: 'AdminSystem', component: AdminSystem }
    ]
  }
]

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
})

router.beforeEach((to, from, next) => {
  const isLoggedIn = store.getters.isLoggedIn
  const isAdmin = store.getters.isAdmin

  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (!isLoggedIn) {
      next('/login')
      return
    }
  }

  if (to.matched.some(record => record.meta.requiresAdmin)) {
    if (!isAdmin) {
      next('/home')
      return
    }
  }

  if (to.matched.some(record => record.meta.requiresGuest)) {
    if (isLoggedIn) {
      next('/home')
      return
    }
  }

  next()
})

export default router