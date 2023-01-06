<template>
  <div class="block">
    <el-timeline>
      <el-timeline-item v-for="(rating,index) in responseBody.data.movies" :key="index" :timestamp="datelist[index]" placement="top">
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
      axios.get('https://e42480v384.zicp.fun/maingetratings?uid=' + this.uid).then(
        Response => {
          console.log('请求成功了打分', Response.data.data.movies)
          this.responseBody = Response.data
          for (var i = 0; i < this.responseBody.data.movies.length; i++) {
            var str1 = Response.data.data.movies[i]
            str1 = str1.replaceAll('\'', '\"')
            var j1 = JSON.parse(str1)
            console.log('j1', j1)
            this.movieidlist.push(j1['movieId'])
            this.starlist.push(j1['rating'])
            this.datelist.push(j1['timestamp'])
          }
          for (i = 0; i < this.responseBody.data.movies.length; i++) {
            axios.get('https://e42480v384.zicp.fun/maingetmoviename?movieid=' + parseInt(this.movieidlist[i])).then(
              Response => {
                console.log('请求成功了8888', Response.data)
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
