import request from '@/utils/request'

export function login(data) {
  return request({
    url: '/login',
    method: 'get',
    params: data,
    baseURL: 'https://4244802384.wocp.fun/main' // 直接通过覆盖的方式
  })
}

export function register(data) {
  console.log('api/user.js register function before')
  return request({
    url: '/register',
    method: 'get',
    params: data,
    baseURL: 'https://4244802384.wocp.fun/main' // 直接通过覆盖的方式
  })
}

// export function login(data) {
//   return request({
//     url: '/vue-element-admin/user/login',
//     method: 'post',
//     data
//   })
// }

export function getInfo(token) {
  console.log('api/user.js token')
  console.log(token)
  return request({
    url: '/vue-element-admin/user/info',
    method: 'get',
    params: { token }
  })
}

export function logout() {
  return request({
    url: '/vue-element-admin/user/logout',
    method: 'post'
  })
}
