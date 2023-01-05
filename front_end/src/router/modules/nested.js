/** When your routing table is too long, you can split it into small modules **/

import Layout from '@/layout'

const nestedRouter = {
  path: '/nested',
  component: Layout,
  redirect: '/nested/menu1/menu1-1',
  name: 'Nested',
  meta: {
    title: '推荐影片',
    icon: 'nested'
  },
  children: [
    {
      path: 'menu1',
      component: () => import('@/views/nested/menu1/index'), // Parent router-view
      name: 'Menu1',
      meta: { title: '标签推荐' }
    },
    {
      path: 'menu2',
      name: 'Menu2',
      component: () => import('@/views/nested/menu2/index'),
      meta: { title: '高分推荐' }
    },
    {
      path: 'menu3',
      name: 'Menu3',
      component: () => import('@/views/nested/menu3/index'),
      meta: { title: '热门推荐' }
    },
    {
      path: 'menu4',
      name: 'Menu4',
      component: () => import('@/views/nested/menu4/index'),
      meta: { title: '流派推荐' }
    },
    {
      path: 'detail',
      name: 'detail',
      component: () => import('@/views/nested/detail'),
      meta: { title: '详情页面' },
      hidden: true
    }
  ]
}

export default nestedRouter
