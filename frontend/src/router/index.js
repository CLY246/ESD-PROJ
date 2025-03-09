import { createRouter, createWebHistory } from 'vue-router';
import Home from '../views/Home.vue'
import Login from '../views/Login.vue'
import Order from '../views/Order.vue'
import Payment from '../views/Payment.vue'
import Menu from '../views/Menu.vue'

const routes = [
    { path: '/', component: Home },
    { path: '/login', component: Login},
    { path: '/order', component: Order},
    { path: '/payment', component: Payment},
    { path: '/menu/:id', component: Menu,props: true},

  ];
  
  const router = createRouter({
    history: createWebHistory(),
    routes
  });
  
  export default router;
