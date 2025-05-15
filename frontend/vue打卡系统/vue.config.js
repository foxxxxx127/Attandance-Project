const { defineConfig } = require('@vue/cli-service')
module.exports = defineConfig({
  transpileDependencies: true
})
module.exports = {
  devServer: {
    proxy: {
      '/employee': {
        target: 'http://127.0.0.1:5000', // Flask 后端地址
        changeOrigin: true,
        pathRewrite: { '^/employee': '/employee' }
      }
    }
  }
}