import { createRouter, createWebHistory } from 'vue-router';
import Home from '../views/Home.vue'
import Login from '../views/Login.vue'
import Order from '../views/Order.vue'
import Payment from '../views/Payment.vue'

const routes = [
    { path: '/', component: Home },
    { path: '/login', component: Login},
    { path: '/order', component: Order},
    { path: '/payment', component: Payment}
  ];
  
  const router = createRouter({
    history: createWebHistory(),
    routes
  });
  
  export default router;
