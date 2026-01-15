# SafeSurface 仓库拆分自动化脚本
# 使用方法: .\scripts\split-repos.ps1 -GithubUsername "YOUR_USERNAME"

param(
    [Parameter(Mandatory=$true)]
    [string]$GithubUsername,
    
    [Parameter(Mandatory=$false)]
    [string]$WorkDir = "e:/code",
    
    [Parameter(Mandatory=$false)]
    [switch]$DryRun = $false
)

$ErrorActionPreference = "Stop"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "SafeSurface 仓库拆分工具" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# 配置
$MainRepo = "SafeSurface"
$BackendRepo = "SafeSurface-Backend"
$WebRepo = "SafeSurface-Web"

$MainPath = Join-Path $WorkDir $MainRepo
$BackendPath = Join-Path $WorkDir "${BackendRepo}-temp"
$WebPath = Join-Path $WorkDir "${WebRepo}-temp"

Write-Host "配置信息:" -ForegroundColor Yellow
Write-Host "  GitHub 用户名: $GithubUsername" -ForegroundColor Gray
Write-Host "  工作目录: $WorkDir" -ForegroundColor Gray
Write-Host "  主仓库: $MainPath" -ForegroundColor Gray
Write-Host "  后端临时目录: $BackendPath" -ForegroundColor Gray
Write-Host "  前端临时目录: $WebPath" -ForegroundColor Gray
Write-Host ""

if ($DryRun) {
    Write-Host "⚠️  DRY RUN 模式 - 不会执行实际操作" -ForegroundColor Yellow
    Write-Host ""
}

# 确认继续
Write-Host "⚠️  警告: 此操作将:" -ForegroundColor Red
Write-Host "  1. 创建新的临时目录" -ForegroundColor Red
Write-Host "  2. 复制代码到新仓库" -ForegroundColor Red
Write-Host "  3. 初始化新的 Git 仓库" -ForegroundColor Red
Write-Host ""
$confirm = Read-Host "是否继续? (yes/no)"
if ($confirm -ne "yes") {
    Write-Host "操作已取消" -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "开始处理..." -ForegroundColor Green
Write-Host ""

# ==================== 步骤 1: 创建后端仓库 ====================
Write-Host "[1/3] 创建后端仓库..." -ForegroundColor Cyan

if (Test-Path $BackendPath) {
    Write-Host "  ⚠️  目录已存在: $BackendPath" -ForegroundColor Yellow
    $overwrite = Read-Host "  是否覆盖? (yes/no)"
    if ($overwrite -eq "yes" -and -not $DryRun) {
        Remove-Item $BackendPath -Recurse -Force
        Write-Host "  ✓ 已删除旧目录" -ForegroundColor Green
    } else {
        Write-Host "  跳过后端仓库创建" -ForegroundColor Yellow
        $BackendSkipped = $true
    }
}

if (-not $BackendSkipped -and -not $DryRun) {
    # 创建目录
    New-Item -ItemType Directory -Path $BackendPath -Force | Out-Null
    Write-Host "  ✓ 创建目录: $BackendPath" -ForegroundColor Green
    
    # 复制文件
    $SourceBackend = Join-Path $MainPath "apps\backend"
    Copy-Item -Path "$SourceBackend\*" -Destination $BackendPath -Recurse -Force
    Write-Host "  ✓ 复制文件从: $SourceBackend" -ForegroundColor Green
    
    # 初始化 Git
    Push-Location $BackendPath
    git init | Out-Null
    git add . | Out-Null
    git commit -m "feat: initial commit for SafeSurface backend" | Out-Null
    git branch -M main | Out-Null
    Write-Host "  ✓ Git 仓库已初始化" -ForegroundColor Green
    
    # 添加远程仓库
    $BackendRemoteUrl = "https://github.com/$GithubUsername/$BackendRepo.git"
    git remote add origin $BackendRemoteUrl 2>$null
    Write-Host "  ✓ 远程仓库已添加: $BackendRemoteUrl" -ForegroundColor Green
    Write-Host "  ℹ️  准备好后执行: cd $BackendPath && git push -u origin main" -ForegroundColor Cyan
    Pop-Location
}

Write-Host ""

# ==================== 步骤 2: 创建前端仓库 ====================
Write-Host "[2/3] 创建前端仓库..." -ForegroundColor Cyan

if (Test-Path $WebPath) {
    Write-Host "  ⚠️  目录已存在: $WebPath" -ForegroundColor Yellow
    $overwrite = Read-Host "  是否覆盖? (yes/no)"
    if ($overwrite -eq "yes" -and -not $DryRun) {
        Remove-Item $WebPath -Recurse -Force
        Write-Host "  ✓ 已删除旧目录" -ForegroundColor Green
    } else {
        Write-Host "  跳过前端仓库创建" -ForegroundColor Yellow
        $WebSkipped = $true
    }
}

if (-not $WebSkipped -and -not $DryRun) {
    # 创建目录
    New-Item -ItemType Directory -Path $WebPath -Force | Out-Null
    Write-Host "  ✓ 创建目录: $WebPath" -ForegroundColor Green
    
    # 复制文件
    $SourceWeb = Join-Path $MainPath "apps\web"
    Copy-Item -Path "$SourceWeb\*" -Destination $WebPath -Recurse -Force
    Write-Host "  ✓ 复制文件从: $SourceWeb" -ForegroundColor Green
    
    # 初始化 Git
    Push-Location $WebPath
    git init | Out-Null
    git add . | Out-Null
    git commit -m "feat: initial commit for SafeSurface frontend" | Out-Null
    git branch -M main | Out-Null
    Write-Host "  ✓ Git 仓库已初始化" -ForegroundColor Green
    
    # 添加远程仓库
    $WebRemoteUrl = "https://github.com/$GithubUsername/$WebRepo.git"
    git remote add origin $WebRemoteUrl 2>$null
    Write-Host "  ✓ 远程仓库已添加: $WebRemoteUrl" -ForegroundColor Green
    Write-Host "  ℹ️  准备好后执行: cd $WebPath && git push -u origin main" -ForegroundColor Cyan
    Pop-Location
}

Write-Host ""

# ==================== 步骤 3: 更新主仓库 ====================
Write-Host "[3/3] 准备主仓库更新命令..." -ForegroundColor Cyan
Write-Host "  ℹ️  请在推送子仓库后执行以下命令:" -ForegroundColor Cyan
Write-Host ""
Write-Host "  cd $MainPath" -ForegroundColor White
Write-Host "  # 备份" -ForegroundColor Gray
Write-Host "  git add ." -ForegroundColor White
Write-Host "  git commit -m 'chore: backup before split'" -ForegroundColor White
Write-Host ""
Write-Host "  # 删除旧的 apps 目录" -ForegroundColor Gray
Write-Host "  git rm -rf apps/backend apps/web" -ForegroundColor White
Write-Host "  git commit -m 'refactor: remove apps directories before adding submodules'" -ForegroundColor White
Write-Host ""
Write-Host "  # 添加子模块" -ForegroundColor Gray
Write-Host "  git submodule add https://github.com/$GithubUsername/$BackendRepo.git apps/backend" -ForegroundColor White
Write-Host "  git submodule add https://github.com/$GithubUsername/$WebRepo.git apps/web" -ForegroundColor White
Write-Host ""
Write-Host "  # 提交并推送" -ForegroundColor Gray
Write-Host "  git add ." -ForegroundColor White
Write-Host "  git commit -m 'refactor: migrate to multi-repo architecture with git submodules'" -ForegroundColor White
Write-Host "  git push" -ForegroundColor White
Write-Host ""

# ==================== 总结 ====================
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "处理完成!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "下一步操作:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. 在 GitHub 上创建以下空仓库(不要初始化任何文件):" -ForegroundColor White
Write-Host "   - https://github.com/$GithubUsername/$BackendRepo" -ForegroundColor Gray
Write-Host "   - https://github.com/$GithubUsername/$WebRepo" -ForegroundColor Gray
Write-Host ""
Write-Host "2. 推送后端仓库:" -ForegroundColor White
Write-Host "   cd $BackendPath" -ForegroundColor Gray
Write-Host "   git push -u origin main" -ForegroundColor Gray
Write-Host ""
Write-Host "3. 推送前端仓库:" -ForegroundColor White
Write-Host "   cd $WebPath" -ForegroundColor Gray
Write-Host "   git push -u origin main" -ForegroundColor Gray
Write-Host ""
Write-Host "4. 更新主仓库(使用上面显示的命令)" -ForegroundColor White
Write-Host ""
Write-Host "5. 其他开发者克隆时:" -ForegroundColor White
Write-Host "   git clone --recursive https://github.com/$GithubUsername/$MainRepo.git" -ForegroundColor Gray
Write-Host ""
Write-Host "详细文档: $MainPath\SPLIT_GUIDE.md" -ForegroundColor Cyan
Write-Host ""
