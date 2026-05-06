const { defineConfig } = require('@vue/cli-service')

module.exports = defineConfig({
  transpileDependencies: true,
  
  // 开发服务器配置
  devServer: {
    port: 8080,
    host: 'localhost',
    open: true, // 自动打开浏览器
    proxy: {
      '/api': {
        target: 'http://localhost:8000', // 后端API地址
        changeOrigin: true,
        secure: false
      }
    }
  },
  
  // 生产环境配置
  publicPath: process.env.NODE_ENV === 'production' ? './' : '/',
  outputDir: 'dist',
  assetsDir: 'static',
  
  // 关闭eslint检查（避免开发时的警告）
  lintOnSave: false,
  
  // 关闭生产环境的source map
  productionSourceMap: false,
  
  // 配置webpack
  configureWebpack: {
    resolve: {
      alias: {
        '@': require('path').resolve(__dirname, 'src')
      }
    }
  },
  
  // CSS相关配置
  css: {
    // 是否使用css分离插件 ExtractTextPlugin
    extract: process.env.NODE_ENV === 'production',
    // 开启 CSS source maps
    sourceMap: false,
    // css预设器配置项
    loaderOptions: {}
  }
})