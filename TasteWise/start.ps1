# 🍜 TasteWise - 食谱推荐系统 (PowerShell 启动脚本)

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "   🍜 TasteWise - 食谱推荐系统" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# 检查 Python
try {
    $pythonVersion = python --version
    Write-Host "[✅] $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "[❌] 未检测到 Python，请先安装 Python 3.10+" -ForegroundColor Red
    Write-Host "     下载地址：https://www.python.org/downloads/" -ForegroundColor Red
    Read-Host "按回车键退出"
    exit 1
}

# 检查/创建虚拟环境
if (-not (Test-Path ".venv\Scripts\Activate.ps1")) {
    Write-Host "[📦] 正在创建虚拟环境..." -ForegroundColor Yellow
    python -m venv .venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[❌] 虚拟环境创建失败" -ForegroundColor Red
        Read-Host "按回车键退出"
        exit 1
    }
}

# 激活虚拟环境
.\.venv\Scripts\Activate.ps1

# 检查依赖
$dep = pip show streamlit 2>$null
if (-not $dep) {
    Write-Host "[📥] 正在安装依赖（首次运行需要几分钟）..." -ForegroundColor Yellow
    pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[❌] 依赖安装失败" -ForegroundColor Red
        Read-Host "按回车键退出"
        exit 1
    }
}

Write-Host "[✅] 环境就绪，正在启动 TasteWise..." -ForegroundColor Green
Write-Host ""
Write-Host "[💡] 浏览器将自动打开 http://localhost:8501" -ForegroundColor Cyan
Write-Host "[🛑] 按 Ctrl+C 即可停止应用" -ForegroundColor Yellow
Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan

streamlit run app.py
