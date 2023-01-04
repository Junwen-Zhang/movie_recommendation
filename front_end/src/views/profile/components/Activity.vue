<template>
  <div class="user-activity">
    <div v-for="(comment,index) in responseBody.data.comments" :key="index" class="post">
      <div class="user-block">
        <img class="img-circle" :src="'https://wpimg.wallstcn.com/57ed425a-c71e-4201-9428-68760c0537c4.jpg'+avatarPrefix">
        <span class="username text-muted">{{ username }}</span>
        <span class="description">{{ movienamelist[index] + "   " +comment[2] }} </span>
      </div>
      <p>
        {{ comment[1] }}
      </p>
      <ul class="list-inline">
        <li>
          <span class="link-black text-sm">
            <i class="el-icon-share" />
            Share
          </span>
        </li>
        <li>
          <span class="link-black text-sm">
            <svg-icon icon-class="like" />
            Like
          </span>
        </li>
      </ul>
    </div>
    <div class="post">
      <div class="user-block">
        <img class="img-circle" :src="'https://wpimg.wallstcn.com/57ed425a-c71e-4201-9428-68760c0537c4.jpg'+avatarPrefix">
        <span class="username">{{ username }}</span>
        <span class="description">最近看过</span>
      </div>
      <div class="user-images">
        <el-carousel :interval="6000" type="card" height="220px">
          <el-carousel-item v-for="item in carouselImages" :key="item">
            <img :src="item+carouselPrefix" class="image">
          </el-carousel-item>
        </el-carousel>
      </div>
      <ul class="list-inline">
        <li><span class="link-black text-sm"><i class="el-icon-share" /> Share</span></li>
        <li>
          <span class="link-black text-sm">
            <svg-icon icon-class="like" /> Like</span>
        </li>
      </ul>
    </div>
  </div>
</template>

<script>
const avatarPrefix = '?imageView2/1/w/80/h/80'
const carouselPrefix = '?imageView2/2/h/440'
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
      carouselImages: [
        'https://wpimg.wallstcn.com/9679ffb0-9e0b-4451-9916-e21992218054.jpg',
        'https://wpimg.wallstcn.com/bcce3734-0837-4b9f-9261-351ef384f75a.jpg',
        'https://wpimg.wallstcn.com/d1d7b033-d75e-4cd6-ae39-fcd5f1c0a7c5.jpg',
        'https://wpimg.wallstcn.com/50530061-851b-4ca5-9dc5-2fead928a939.jpg'
      ],
      avatarPrefix,
      carouselPrefix
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
      axios.get('https://4244802384.wocp.fun/maingetcomments?uid=' + this.uid).then(
        Response => {
          console.log('请求成功了', Response.data)
          console.log('！！！！！！！！！！！', JSON.parse(localStorage.getItem('realusername')))
          console.log('！！！！！！！！！！！', JSON.parse(localStorage.getItem('realuserid')))
          this.responseBody = Response.data
          for (var i = 0; i < this.responseBody.data.comments.length; i++) {
            this.movieidlist.push(this.responseBody.data.comments[i][3])
          }
          console.log('打印movieidlist', this.movieidlist)
          for (i = 0; i < this.responseBody.data.comments.length; i++) {
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

<style lang="scss" scoped>
.user-activity {
  .user-block {

    .username,
    .description {
      display: block;
      margin-left: 50px;
      padding: 2px 0;
      white-space: pre-line
    }

    .username{
      font-size: 16px;
      color: #000;
    }

    :after {
      clear: both;
    }

    .img-circle {
      border-radius: 50%;
      width: 40px;
      height: 40px;
      float: left;
    }

    span {
      font-weight: 500;
      font-size: 12px;
    }
  }

  .post {
    font-size: 14px;
    border-bottom: 1px solid #d2d6de;
    margin-bottom: 15px;
    padding-bottom: 15px;
    color: #666;

    .image {
      width: 100%;
      height: 100%;

    }

    .user-images {
      padding-top: 20px;
    }
  }

  .list-inline {
    padding-left: 0;
    margin-left: -5px;
    list-style: none;

    li {
      display: inline-block;
      padding-right: 5px;
      padding-left: 5px;
      font-size: 13px;
    }

    .link-black {

      &:hover,
      &:focus {
        color: #999;
      }
    }
  }

}

.box-center {
  margin: 0 auto;
  display: table;
}

.text-muted {
  color: #777;
}
</style>
