<template>
  <div class="infinite-list-wrapper" style="overflow:auto">
    <ul
      v-infinite-scroll="load"
      class="list"
      style="overflow:auto"
      infinite-scroll-disabled="disabled"
    >
      <li v-for="i in questcnt" :key="i" class="infinite-list-item">
        <el-row v-for="j in 2" :key="j" type="flex">
          <el-col v-for="k in 5" :key="k" :span="5" :offset="k>1? 1:0">
            <el-card shadow="hover" :body-style="{ padding: '0px'}">
              <img
                src="https://shadow.elemecdn.com/app/element/hamburger.9cf7b091-55e9-11e9-a976-7f4d0b07eef6.png"
                class="image"
              >
              <div style="padding: 14px;">
                <span class="title"> {{ movieTitleList[i*10+j*5+k-16] }}</span>
                <div class="bottom clearfix">
                  <el-rate
                    v-model="movieRateList[i*10+j*5+k-16]"
                    disabled
                    show-score
                  />
                  <el-button type="text" class="button" @click="goDetail">详情</el-button>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </li>
    </ul>
    <p v-if="loading">加载中...</p>
    <p v-if="noMore">没有更多了</p>
  </div>
</template>

<style>

  .button {
    padding: 0;
    float: right;
  }

  .title{
    font-size: 16px;
    color: #000;
  }

  .image {
    width: 100%;
    display: block;
  }

  .el-card-define {
  min-height: 100%;
  height: 100%;
  min-width: 100%;
  height: 150%;
  }
  .el-card-define >>> .el-card__body {
    height: 100%;
  }

  .clearfix:before,

  .clearfix:after {
    display: table;
    content: "";
  }

  .clearfix:after {
    clear: both
  }

  .list li {
    list-style-type: none;
  }
</style>

<script>

import axios from 'axios'

export default {
  data() {
    return {
      count: 1,
      loading: false,
      movieidlist: [],
      movieTitleList: [],
      movieRateList: [],
      questcnt: 0
    }
  },
  computed: {
    noMore() {
      return this.count >= 10
    },
    disabled() {
      return this.loading || this.noMore
    }
  },
  created() {
    this.initMovie()
    this.requestHttpParseGson()
  },
  methods: {
    load() {
      this.loading = true
      setTimeout(() => {
        this.count += 1
        this.requestHttpParseGson()
        this.loading = false
      }, 4000)
    },
    initMovie() {
      this.uid = JSON.parse(localStorage.getItem('realuserid'))
    },
    goDetail() {

    },
    requestHttpParseGson() {
      axios.get('https://e42480v384.zicp.fun/recmv/recbytrend?uid=' + this.uid).then(
        Response => {
          console.log('请求成功了', Response.data)
          this.responseBody = Response.data
          for (var i = 0; i < 10; i++) {
            this.movieidlist.push(this.responseBody.data.movie_list[i])
          }
          console.log('打印movieidlist', this.movieidlist)
          axios.get('https://e42480v384.zicp.fun/main/getmovieinfor?movieIdListStr=' + this.movieidlist).then(
            Response => {
              console.log('请求成功了', Response.data)
              this.responseBody = Response.data
              for (var i = 0; i < 10; i++) {
                var result = this.responseBody.data.movies[i + this.questcnt * 10]
                res = ''
                for (var j = 0; j < result.length; j++) {
                  if (result[j] === '\'' && result[j + 1] !== 's') { res += '\"' } else { res += result[j] }
                }
                console.log(res)
                var res = JSON.parse(res)
                this.movieTitleList.push(res.Title)
                this.movieRateList.push(parseFloat(res.avg_rating).toFixed(2))
              }
              this.questcnt++
              console.log('打印movieTitleList', this.movieTitleList)
            },
            Error => {
              console.log('请求失败了', Response.message)
              this.moviename = Error.message
            }
          )
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
