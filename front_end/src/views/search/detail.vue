<template>
  <div class="common-layout">
    <el-container>
      <el-aside width="200px">
        <el-image style="width: 200px; height: 320px" :src="url" :fit="cover" />
      </el-aside>
      <el-container>
        <div class="app-container">
          <el-header height="1px">
            电影标题
          </el-header>
        </div>
        <el-main>
          <el-col>
            <div class="app-container">
              movie introduction here
            </div>
            <el-input v-model="textarea2" type="textarea" :autosize="{ minRows: 4, maxRows: 6}" placeholder="请输入影评" />
          </el-col>
        </el-main>
        <el-footer>
          <el-row :gutter="10">
            <el-col :span="6">
              <el-rate v-model="value" show-text :texts="text" allow-half :colors="color" />
            </el-col>
            <el-col :span="5">
              <el-button type="primary" round>
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
  </div>
</template>

<script>
export default {
  data() {
    return {
      url: 'https://shadow.elemecdn.com/app/element/hamburger.9cf7b091-55e9-11e9-a976-7f4d0b07eef6.png',
      text: [1, 2, 3, 4, 5],
      color: ['#82a9e2', '#f7d83a', '#f70000']
    }
  }
}
</script>
