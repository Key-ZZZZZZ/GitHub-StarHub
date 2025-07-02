module.exports = {
  transpileDependencies: [],
  // 开发服务器配置
  devServer: {
    port: 8080,
    proxy: {
      '/api': {
        target: 'http://localhost:5001',
        changeOrigin: true
      }
    }
  },
  // 生产环境配置
  productionSourceMap: false,
  // 公共路径配置
  publicPath: '/'
}