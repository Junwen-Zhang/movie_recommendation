<template>
  <div class="block">
    <el-timeline>
      <el-timeline-item v-for="(rating,index) in responseBody.data.movies" :key="index" :timestamp="rating[3]" placement="top">
        <el-card>
          <h4>{{ movienamelist[index] }}</h4>
          <p v-if="starlist[index] == 1">★☆☆☆☆</p>
          <p v-else-if="starlist[index] == 2">★★☆☆☆</p>
          <p v-else-if="starlist[index] == 3">★★★☆☆</p>
          <p v-else-if="starlist[index] == 4">★★★★☆</p>
          <p v-else>★★★★★</p>
        </el-card>
      </el-timeline-item>
    </el-timeline>
  </div>
</template>

<script>
import axios from 'axios'
export default {
  data() {
    return {
      uid: '',
      username: '',
      responseBody: null,
      moviename: '',
      movienamelist: [],
      movieidlist: [],
      starlist: [],
      datelist: []
    }
  },
  created() {
    this.initUser()
    this.requestHttpParseGson()
  },
  methods: {
    initUser() {
      this.uid = JSON.parse(localStorage.getItem('realuserid'))
      this.username = JSON.parse(localStorage.getItem('realusername'))
    },
    requestHttpParseGson() {
      axios.get('https://4244802384.wocp.fun/maingetratings?uid=' + this.uid).then(
        Response => {
          console.log('请求成功了', Response.data)
          this.responseBody = Response.data
          for (var i = 0; i < this.responseBody.data.movies.length; i++) {
            this.movieidlist.push(this.responseBody.data.movies[i][1])
            this.starlist.push(this.responseBody.data.movies[i][2])
            this.datelist.push(this.responseBody.data.movies[i][3])
          }
          for (i = 0; i < this.responseBody.data.movies.length; i++) {
            axios.get('https://4244802384.wocp.fun/maingetmoviename?movieid=' + this.movieidlist[i]).then(
              Response => {
                console.log('请求成功了', Response.data)
                this.moviename = Response.data.data.movies
                this.movienamelist.push(this.moviename)
              },
              Error => {
                console.log('请求失败了', Response.message)
                this.moviename = Error.message
              }
            )
          }
          console.log('打印movienamelist', this.movienamelist)
        },
        Error => {
          console.log('请求失败了', Response.message)
          this.responseBody = Error.message
        }
      )
    }
  }
}
</script>
