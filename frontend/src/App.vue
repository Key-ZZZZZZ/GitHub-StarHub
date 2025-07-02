<template>
  <div class="app-container">
    <el-container>
      <el-aside width="200px">
        <div class="sidebar-header">
          <h2>GitHub StarHub</h2>
        </div>
        <el-menu
          router
          default-active="/execution-records"
          class="sidebar-menu"
        >
          <el-menu-item index="/execution-records">
            <el-icon><Calendar /></el-icon>
            <span>执行记录</span>
          </el-menu-item>
          <el-menu-item index="/data-analysis">
            <el-icon><DataAnalysis /></el-icon>
            <span>数据分析</span>
          </el-menu-item>
          <el-menu-item index="/trending-projects">
            <el-icon><Star /></el-icon>
            <span>热门项目</span>
          </el-menu-item>
          <el-menu-item index="/settings">
            <el-icon><Setting /></el-icon>
            <span>系统设置</span>
          </el-menu-item>
        </el-menu>
      </el-aside>
      <el-container>
        <el-main>
          <router-view />
          <p class="footer-copyright">© 2023 GitHub StarHub. All rights reserved. Designed by Key.ZZZZZZ</p>
        </el-main>
        
      </el-container>
      
    </el-container>
    
  </div>
</template>

<script>
import { Calendar, DataAnalysis, Star, Setting } from '@element-plus/icons-vue'

export default {
  name: 'App',
  components: {
    Calendar,
    DataAnalysis,
    Star,
    Setting
  }
}
</script>

<style>
.app-container {
  height: 100vh;
  width: 100%;
}

.sidebar-header {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #409EFF;
  border-bottom: 1px solid #e6e6e6;
}

.sidebar-menu {
  height: calc(100vh - 60px);
}

.el-aside {
  background-color: #f5f7fa;
  border-right: 1px solid #e6e6e6;
  overflow-y: hidden;
}

.el-container {
  height: 100%;
}

.el-main {
  padding: 20px;
  background-color: #f5f7fa;
  overflow-y: auto; /* 允许垂直滚动 */
  /* height: calc(100vh - 60px); 减去顶部导航栏的高度，如果存在的话 */
  display: flex;
  flex-direction: column;
  padding-top: 0px;
}

.footer-copyright {
  margin-top: auto; /* 将版权信息推到底部 */
  padding-top: 20px;
  text-align: center;
  color: #909399;
  font-size: 14px;
}

body {
  margin: 0;
  padding: 0;
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', Arial, sans-serif;
}
</style>