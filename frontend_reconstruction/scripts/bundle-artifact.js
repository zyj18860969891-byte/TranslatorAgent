#!/usr/bin/env node

const fs = require('fs')
const path = require('path')
const { execSync } = require('child_process')

console.log('🚀 开始打包前端应用...')

// 检查dist目录是否存在
const distDir = path.join(__dirname, '..', 'dist')
if (!fs.existsSync(distDir)) {
  console.log('📦 构建应用...')
  execSync('npm run build', { stdio: 'inherit' })
}

// 读取构建后的HTML文件
const htmlFile = path.join(distDir, 'index.html')
if (!fs.existsSync(htmlFile)) {
  console.error('❌ 找不到构建后的HTML文件')
  process.exit(1)
}

let htmlContent = fs.readFileSync(htmlFile, 'utf-8')

// 内联CSS和JS（简化版本）
// 在实际项目中，可以使用更复杂的打包工具

const bundleDir = path.join(__dirname, '..', 'bundle')
if (!fs.existsSync(bundleDir)) {
  fs.mkdirSync(bundleDir, { recursive: true })
}

const bundleFile = path.join(bundleDir, 'bundle.html')
fs.writeFileSync(bundleFile, htmlContent)

console.log('✅ 打包完成!')
console.log(f'📁 Bundle文件: {bundleFile}')
console.log('💡 提示: 将此文件作为Artifact发送给用户')