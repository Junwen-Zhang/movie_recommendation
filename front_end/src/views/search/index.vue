<template>
  <div class="app-container">
    <el-form ref="form" :model="form" label-width="120px">
      <el-form-item label="电影名">
        <el-input v-model="form.name" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="onSubmit">查找</el-button>
        <el-button @click="onCancel">取消</el-button>
      </el-form-item>
    </el-form>
    <el-table
      :data="movieList"
      style="width: 100%"
    >
      <el-table-column
        prop="Title"
        label="电影标题"
        width="180"
      />
      <el-table-column
        prop="movieId"
        label="电影id"
        width="180"
      >
        <template slot-scope="scope">
          <router-link :to="{path: '/nested/detail', query: { id: scope.row.movieId }}">
            <a
              href="#"
              target="_blank"
              class="buttonText"
              style="color: blue;"
            >
              {{ scope.row.movieId }}
            </a>
          </router-link>
        </template>
      </el-table-column>
      <el-table-column
        prop="Release Year"
        label="发行年份"
      />
    </el-table>
  </div>
</template>

<script>
import axios from 'axios'
export default {
  data() {
    return {
      form: {
        name: ''
      },
      movieList: [
        { 'Title': 'toy story',
          'movieId': '1',
          'Release Year': 'year'
        }
      ]
    }
  },
  methods: {
    onSubmit() {
      console.log(this.form.name)
      axios.get('https://e42480v384.zicp.fun/main/searchmovie?name=' + this.form.name).then(
        Response => {
          console.log('查找成功了', Response.data)
          this.responseBody = Response.data
          var result = this.responseBody.data.number
          for (var j = 0; j < result.length; j++) {
            var temp = result[j]
            res = ''
            for (var i = 0; i < temp.length; i++) {
              if (temp[i] === '\'' && temp[i + 1] !== 's') { res += '\"' } else { res += temp[i] }
            }
            console.log(res)
            var res = JSON.parse(res)
            this.movieList.push(res)
          }
          this.$message('查找成功')
        },
        Error => {
          console.log('查找失败了', Response.message)
          this.$message('查找失败')
          this.moviename = Error.message
        }
      )
    },
    onCancel() {
      this.$message({
        message: '取消!',
        type: 'warning'
      })
    }
  }
}
</script>

<style scoped>
.line{
  text-align: center;
}
</style>
