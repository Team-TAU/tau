import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router';
import store from '../store/index';
import Login from '../components/views/Login.vue';
import DashboardBase from '../components/DashboardBase.vue';
import Dashboard from '../components/views/Dashboard.vue';
import ChatBots from '../components/views/ChatBots.vue';

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    redirect: '/dashboard',
  },
  {
    path: '/login',
    component: Login,
    meta: { reqUnauth: true },
  },
  {
    path: '/dashboard',
    component: DashboardBase,
    meta: { reqAuth: true },
    children: [
      {
        path: '',
        name: 'Dashboard',
        component: Dashboard,
      },
      {
        path: 'config',
        name: 'Config',
        // route level code-splitting
        // this generates a separate chunk (about.[hash].js) for this route
        // which is lazy-loaded when the route is visited.
        component: () =>
          import(
            /* webpackChunkName: "about" */ '../components/views/Config.vue'
          ),
      },
      {
        path: 'streamers',
        name: 'Streamers',
        component: () => import('../components/views/Streamers.vue'),
      },
      {
        path: 'chat-bots',
        name: 'Chat Bots',
        component: () => import('../components/views/ChatBots.vue'),
      },
      {
        path: 'user',
        name: 'User',
        component: () => import('../components/views/User.vue'),
      },
      {
        path: 'webhook-monitor',
        name: 'WebhookMonitor',
        component: () => import('../components/views/WebhookMonitor.vue'),
      },
    ],
  },
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
});

router.beforeEach(function (to, from, next) {
  if (to.meta.reqAuth && !store.getters['auth/isAuthenticated']) {
    next('/login');
  } else if (to.meta.reqUnauth && store.getters['auth/isAuthenticated']) {
    next('/');
  } else {
    next();
  }
});

export default router;
