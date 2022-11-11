import {createRouter, createWebHistory, RouteRecordRaw} from 'vue-router'
import Home from '../views/Home.vue'
import Tensorflow from '../views/Tensorflow.vue'
import Tfx from '../views/Tfx.vue'

const routes: Array<RouteRecordRaw> = [
    {
        path: '/',
        name: 'Home',
        component: Home,
        children: [
            {
                path: '',
                name: 'tensorflow',
                component: Tensorflow
            },
            {
                path: '/tfx',
                name: 'tfx',
                component: Tfx
            }
        ]
    }
]

const router = createRouter({
    history: createWebHistory(process.env.BASE_URL),
    routes
})

export default router
