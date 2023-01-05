<template>
  <div class="common-layout">
    <el-container>
      <el-aside width="200px">
        <el-image
          :src="movieUrl"
          :fit="fit"
        />
      </el-aside>
      <el-container>
        <div class="app-container">
          <el-header height="1px">
            {{ movieTitle }}
          </el-header>
        </div>
        <el-main>
          <el-col>
            <el-input v-model="textarea2" type="textarea" :autosize="{ minRows: 4, maxRows: 6}" placeholder="请输入影评" />
          </el-col>
        </el-main>
        <el-footer>
          <el-row :gutter="10">
            <el-col :span="6">
              <el-rate v-model="movieRating" show-text :texts="text" :colors="color" />
            </el-col>
            <el-col :span="5">
              <el-button type="primary" round @click="postComment">
                提交
              </el-button>
            </el-col>
            <el-col :span="4">
              <el-button round>
                取消
              </el-button>
            </el-col>
          </el-row>
        </el-footer>
      </el-container>
    </el-container>
    <el-table
      :data="commentList"
      style="width: 100%"
    >
      <el-table-column
        prop="date"
        label="日期"
        width="180"
      />
      <el-table-column
        prop="username"
        label="用户名"
        width="180"
      />
      <el-table-column
        prop="comment"
        label="影评内容"
      />
    </el-table>
  </div>
</template>

<script>

import axios from 'axios'

export default {
  data() {
    return {
      textarea2: '',
      movieTitle: '',
      movieId: 0,
      movieYear: 0,
      movieRating: 0,
      movieUrl: '',
      commentList: [],
      text: [1, 2, 3, 4, 5],
      color: ['#82a9e2', '#f7d83a', '#f70000']
    }
  },
  created() {
    console.log(this.$route.query.id)
    this.movieId = [this.$route.query.id]
    this.initInfo()
    this.initComment()
  },
  methods: {
    postComment() {
      var uid = JSON.parse(localStorage.getItem('realuserid'))
      axios.get('https://e42480v384.zicp.fun/mainaddcomments?uid=' + uid + '&movieid=' + this.movieId + '&content=' + this.textarea2).then(
        Response => {
          console.log('请求成功了', Response.data)
          this.$message('提交成功')
          location.reload()
          this.$router.go(0)
        },
        Error => {
          console.log('请求失败了', Response.message)
          this.$message('提交失败')
          this.moviename = Error.message
        }
      )
    },
    initInfo() {
      axios.get('https://e42480v384.zicp.fun/main/getmovieinfor?movieIdListStr=' + this.movieId).then(
        Response => {
          console.log('请求成功了', Response.data)
          this.responseBody = Response.data
          var result = this.responseBody.data.movies[0]
          console.log(result)
          res = ''
          for (var j = 0; j < result.length; j++) {
            if (result[j] === '\'' && result[j + 1] !== 's') { res += '\"' } else { res += result[j] }
          }
          var res = JSON.parse(res)
          console.log(res)
          this.movieTitle = res.Title
          this.movieRating = parseFloat(res.avg_rating).toFixed(2)
        },
        Error => {
          console.log('请求失败了', Response.message)
          this.moviename = Error.message
        }
      )
      axios.get('https://e42480v384.zicp.fun/main/getpic?movieId=' + this.movieId).then(
        Response => {
          console.log('请求成功了', Response.data)
          this.responseBody = Response.data
          this.movieUrl = this.responseBody.data.picture
          console.log('打印movieurl', this.responseBody.data.picture)
        },
        Error => {
          console.log('请求失败了', Response.message)
          this.moviename = Error.message
        }
      )
      axios.get('https://e42480v384.zicp.fun/maingetmvcomments?mvid=' + this.movieId).then(
        Response => {
          console.log('请求成功了', Response.data)
          this.responseBody = Response.data
          var result = this.responseBody.data.comments
          for (var j = 0; j < result.length; j++) {
            var temp = result[j]
            res = ''
            for (var i = 0; i < temp.length; i++) {
              if (temp[i] === '\'' && temp[i + 1] !== 's') { res += '\"' } else { res += temp[i] }
            }
            console.log(res)
            var res = JSON.parse(res)
            this.commentList.push(res)
          }
          console.log('commentlist', this.commentList)
        },
        Error => {
          console.log('请求失败了', Response.message)
          this.moviename = Error.message
        }
      )
    }
  }
}
</script>
