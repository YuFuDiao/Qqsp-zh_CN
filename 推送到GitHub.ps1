<#
  推送 Qqsp 汉化到 GitHub —— 首次上传 / 后续更新通用
  脚本放在仓库根目录，自动用文件所在目录作为仓库目录。
  用法: 右键本文件 -> "使用 PowerShell 运行"
#>

$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [Text.Encoding]::UTF8

function Info($m) { Write-Host "[·] $m" -ForegroundColor Gray }
function Ok($m)   { Write-Host "[OK] $m" -ForegroundColor Green }
function Warn($m) { Write-Host "[!] $m" -ForegroundColor Yellow }

Write-Host ''
Write-Host '=== Qqsp 汉化 —— 推送到 GitHub ==='
Write-Host ''

# $PSScriptRoot is empty when this file is invoked through -Command, so fall back.
$repo = $PSScriptRoot
if ([string]::IsNullOrEmpty($repo)) { $repo = (Get-Location).Path }
Set-Location -LiteralPath $repo
Info "仓库目录: $repo"

if (-not (Test-Path -LiteralPath (Join-Path $repo '.git'))) {
    Warn '当前目录不是 git 仓库（找不到 .git），请把本脚本放在仓库根目录再运行。'
    Read-Host '按回车键退出'; exit 1
}
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Warn 'git 不在 PATH 中，请先安装 Git for Windows。'
    Read-Host '按回车键退出'; exit 1
}

# ---------- 1. 把新改动提交上去 ----------
$dirty = @(git status --porcelain)
if ($dirty.Count -gt 0) {
    Warn "检测到 $($dirty.Count) 项未提交改动，全部提交："
    git add -A
    $staged = @(git diff --cached --name-only)
    if ($staged.Count -eq 0) {
        Info '没有需要提交的内容，跳过。'
    } else {
        $msg = 'update: ' + (Get-Date -Format 'yyyy-MM-dd HH:mm')
        git commit -q -m $msg
        Ok "已提交 $($staged.Count) 个文件（$msg）"
    }
} else {
    Ok '工作区干净，无需新提交。'
}

# ---------- 2. 确认远程 ----------
$url = git remote get-url origin
Ok "远程 origin = $url"

# ---------- 3. 推送 ----------
Info '先取回远程状态 ...'
cmd.exe /c "git fetch origin 2>&1" | Out-Null
$lr = @(cmd.exe /c "git rev-list --left-right --count origin/main...main 2>nul")
if ($lr.Count -ge 1 -and $lr[0] -match '^\s*(\d+)\s+\d+\s*$' -and [int]$Matches[1] -gt 0) {
    Warn "远程比本地新（落后 $($Matches[1]) 个提交），已中止推送。"
    Write-Host '    先执行： git pull --rebase origin main   然后重跑本脚本' -ForegroundColor Yellow
    Read-Host '按回车键退出'; exit 1
}

Info '推送到 origin/main ...'
cmd.exe /c "git push -u origin main"

if ($LASTEXITCODE -ne 0) {
    Warn '推送失败。常见原因与对策：'
    Write-Host '    - 仓库还没在 GitHub 上创建：先到 https://github.com/new 建一个同名空仓库' -ForegroundColor Yellow
    Write-Host '      （不要勾选 Add README / .gitignore / license，保持完全空白）' -ForegroundColor Yellow
    Write-Host '    - 需要登录：会弹出 Git Credential Manager 窗口，选 Sign in with your browser' -ForegroundColor Yellow
    Write-Host '    - 若提示 schannel / SSL 错误，先执行下面这行再重跑：' -ForegroundColor Yellow
    Write-Host '        git config --local http.sslBackend openssl' -ForegroundColor Yellow
    Read-Host '按回车键退出'; exit 1
}

Ok '推送成功。'
git log --oneline -3
Write-Host ''
Write-Host "在线查看: $($url -replace '\.git$','')" -ForegroundColor Cyan
Write-Host ''
Read-Host '按回车键退出'
