# 百炼API密钥自动配置脚本（PowerShell）
# 用于Windows系统永久配置DASHSCOPE_API_KEY环境变量

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "百炼API密钥配置脚本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 设置API密钥
$API_KEY = "sk-88bf1bd605544d208c7338cb1989ab3e"

Write-Host "正在配置API密钥: $API_KEY" -ForegroundColor Yellow
Write-Host ""

# 永久配置到用户环境变量
[Environment]::SetEnvironmentVariable("DASHSCOPE_API_KEY", $API_KEY, "User")

Write-Host "========================================" -ForegroundColor Green
Write-Host "配置完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

Write-Host "API密钥已永久配置到用户环境变量" -ForegroundColor Green
Write-Host ""

Write-Host "重要提示：" -ForegroundColor Yellow
Write-Host "1. 请重启终端或VS Code使配置生效" -ForegroundColor White
Write-Host "2. 可以使用以下命令验证配置：" -ForegroundColor White
Write-Host "   echo `$env:DASHSCOPE_API_KEY" -ForegroundColor Cyan
Write-Host ""

Write-Host "3. 测试API连接：" -ForegroundColor White
Write-Host "   python test_api_connection.py" -ForegroundColor Cyan
Write-Host ""

Write-Host "配置的API密钥：" -ForegroundColor Yellow
Write-Host $API_KEY -ForegroundColor Green
Write-Host ""

Write-Host "配置的API密钥：" -ForegroundColor White
Write-Host $API_KEY -ForegroundColor Green
Write-Host ""

# 验证配置
Write-Host "正在验证配置..." -ForegroundColor Yellow
$CURRENT_KEY = [Environment]::GetEnvironmentVariable("DASHSCOPE_API_KEY", "User")
if ($CURRENT_KEY -eq $API_KEY) {
    Write-Host "✅ 验证成功！环境变量已正确配置" -ForegroundColor Green
} else {
    Write-Host "❌ 验证失败！请手动检查" -ForegroundColor Red
}

Write-Host ""
Write-Host "按任意键退出..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
