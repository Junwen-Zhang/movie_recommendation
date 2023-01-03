import { login, logout, getInfo,register} from '@/api/user'
import { getToken, setToken, removeToken } from '@/utils/auth'
import router, { resetRouter } from '@/router'


const state = {
  token: getToken(),
  name: '',
  avatar: '',
  introduction: '',
  roles: []
}

const mutations = {
  SET_TOKEN: (state, token) => {
    state.token = token
  },
  SET_INTRODUCTION: (state, introduction) => {
    state.introduction = introduction
  },
  SET_NAME: (state, name) => {
    state.name = name
  },
  SET_AVATAR: (state, avatar) => {
    state.avatar = avatar
  },
  SET_ROLES: (state, roles) => {
    state.roles = roles
  }
}

const actions = {
  // user login
  login({ commit }, userInfo) {
    const { username, password } = userInfo
    return new Promise((resolve, reject) => {
      console.log('login function before1')
      login({ username: username.trim(), password: password }).then(response => {
        console.log("response")
        console.log(response)
        const { data } = response
        console.log("data")
        console.log(data)
        // console.log(response.data)
        console.log(1)
        commit('SET_TOKEN', response.data)
        console.log(2)
        setToken(response.data)
        console.log(3)
        resolve()
      }).catch(error => {
        reject(error)
      })
    })
  },

  register({ commit }, userInfo) {
    const { username, password } = userInfo
    return new Promise((resolve, reject) => {
      console.log('store/module/user.js register function before')
      register({ username: username.trim(), password: password }).then(response => {
        console.log("register response")
        console.log(response)
        const { data } = response
        commit('SET_TOKEN', response.data)
        setToken(response.data)
        resolve()
      }).catch(error => {
        reject(error)
      })
    })
  },

  // get user info
  getInfo({ commit, state }) {
    return new Promise((resolve, reject) => {
      console.log("module/user.js middle")
      console.log(state.token)
      getInfo(state.token).then(response => {
        console.log('module/user.js after')
        console.log(response)
        const { data } = response
        console.log("getInfo response")
        console.log("data: ",data)
        console.log(data['token'])
        // data=data['token']
        // console.log(data)
        console.log(typeof(data['token']))
        console.log(JSON.parse(data['token']))
        console.log(typeof(JSON.parse(data['token'])))
        var data2=JSON.parse(data['token'])
        console.log("test some values")
        console.log(data2.roles)
        // console.log(typeof(data.token))
        // const uid=data.substring(data.find('uid'),-2)
        // console.log(uid)

        if (!data) {
          reject('Verification failed, please Login again.')
        }

        // const { roles, name, avatar, introduction } = data

        // roles must be a non-empty array
        // if (!roles || roles.length <= 0) {
        //   reject('getInfo: roles must be a non-null array!')
        // }

        commit('SET_ROLES', data2.roles)
        commit('SET_NAME', data2.name)
        commit('SET_AVATAR', data2.uid)
        commit('SET_INTRODUCTION', data2.success)
        console.log("4 cimi")
        resolve(data2)
        console.log("5")
      }).catch(error => {
        reject(error)
      })
    })
  },

  // user logout
  logout({ commit, state, dispatch }) {
    return new Promise((resolve, reject) => {
      logout(state.token).then(() => {
        commit('SET_TOKEN', '')
        commit('SET_ROLES', [])
        removeToken()
        resetRouter()

        // reset visited views and cached views
        // to fixed https://github.com/PanJiaChen/vue-element-admin/issues/2485
        dispatch('tagsView/delAllViews', null, { root: true })

        resolve()
      }).catch(error => {
        reject(error)
      })
    })
  },

  // remove token
  resetToken({ commit }) {
    return new Promise(resolve => {
      commit('SET_TOKEN', '')
      commit('SET_ROLES', [])
      removeToken()
      resolve()
    })
  },

  // dynamically modify permissions
  async changeRoles({ commit, dispatch }, role) {
    const token = role + '-token'

    commit('SET_TOKEN', token)
    setToken(token)

    const { roles } = await dispatch('getInfo')

    resetRouter()

    // generate accessible routes map based on roles
    const accessRoutes = await dispatch('permission/generateRoutes', roles, { root: true })
    // dynamically add accessible routes
    router.addRoutes(accessRoutes)

    // reset visited views and cached views
    dispatch('tagsView/delAllViews', null, { root: true })
  }
}

export default {
  namespaced: true,
  state,
  mutations,
  actions
}
