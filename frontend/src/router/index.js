import { createRouter, createWebHistory } from 'vue-router';
import Home from '../views/Home.vue';
import Login from '../views/Login.vue';
import Order from '../views/Order.vue';
import Payment from '../views/Payment.vue';
import Menu from '../views/Menu.vue';
import GroupOrder from '../views/GroupOrder.vue';
import Success from '@/views/Success.vue';
import SplitPayment from '@/views/SplitPayment.vue';

const routes = [
  { path: '/', component: Home },
  { path: '/login', component: Login },
  { path: '/order', component: Order },
  { path: '/payment', component: Payment },
  { path: '/menu/:id', component: Menu, props: true },
  { path: '/group-order/join/:cartId', component: GroupOrder },
  { path: '/success', component: Success },
  { path: '/splitpayments', component: SplitPayment },

];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;
