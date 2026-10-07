<#
  Publish the ready-to-run Qqsp 1.9.0 Simplified Chinese portable package
  to GitHub Releases, so players have a one-click download.

  用法：右键本文件 -> "使用 PowerShell 运行"
        加 -Force 可覆盖同名附件；加 -NoStore 不记住 token。
#>
[CmdletBinding()]
param(
    [switch]$Force,
    [switch]$NoStore
)

$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [Text.Encoding]::UTF8

$Owner  = 'YuFuDiao'
$Repo   = 'Qqsp-zh_CN'
$Api    = "https://api.github.com/repos/$Owner/$Repo"
$Branch = 'main'

# ---- the release we publish ----
$Tag      = 'v1.9.0-zh_CN'
$RelName  = 'Qqsp 1.9.0 汉化便携版'
$AssetName = 'Qqsp-1.9.0-win64-zh_CN.rar'
$AssetSha = '7f1d2d011187ae6268d3777ecd8268131d18ca4c7e575cf0827bd82f252e00f9'
# Prefer an asset stored next to this script (keeps the machine-specific path
# out of the published script); fall back to a local copy on F:.
$AssetCandidates = @(
    (Join-Path $PSScriptRoot $AssetName),
    (Join-Path $PSScriptRoot 'Qqsp-1.9.0-win64.rar'),
    'F:\Qqsp-1.9.0-win64.rar'
)

function Info($m) { Write-Host "[·] $m" -ForegroundColor Gray }
function Ok($m)   { Write-Host "[OK] $m" -ForegroundColor Green }
function Warn($m) { Write-Host "[!] $m" -ForegroundColor Yellow }
function Die($m)  { Write-Host "[x] $m" -ForegroundColor Red; Read-Host '按回车键退出'; exit 1 }

Write-Host ''
Write-Host '=== 发布 Qqsp 汉化便携版到 GitHub Releases ==='
Write-Host ''

# ---------- 1. the asset ----------
$AssetSrc = $AssetCandidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
if (-not $AssetSrc) {
    Die ("找不到附件。请把 {0} 放到本脚本同目录，或放到 F:\ 下。" -f $AssetName)
}
$bad = [regex]::Matches($AssetName, '[^A-Za-z0-9._-]')
if ($bad.Count -gt 0) { Die "附件名含非法字符: $AssetName" }
$len = (Get-Item -LiteralPath $AssetSrc).Length
$sha = (Get-FileHash -LiteralPath $AssetSrc -Algorithm SHA256).Hash.ToLower()
Info ("附件: {0}  {1:N1} MB" -f $AssetName, ($len / 1MB))
Info ("SHA256: {0}" -f $sha)
if ($sha -ne $AssetSha) {
    Warn "附件哈希与登记值不一致，可能被打包脚本改过："
    Warn ("  登记 {0}" -f $AssetSha)
    $ans = Read-Host '仍要继续吗？(y/N)'
    if ($ans -notmatch '^(y|Y)') { Die '已取消' }
} else {
    Ok '附件哈希校验通过'
}

# ---------- 2. token ----------
Add-Type -AssemblyName System.Security
$CredTarget = "GitHubRelease:$Owner/$Repo"
$sig = @'
using System;
using System.Runtime.InteropServices;
public class CredMan {
    [StructLayout(LayoutKind.Sequential, CharSet = CharSet.Unicode)]
    public struct CREDENTIAL {
        public uint Flags; public uint Type; public string TargetName; public string Comment;
        public System.Runtime.InteropServices.ComTypes.FILETIME LastWritten;
        public uint CredentialBlobSize; public IntPtr CredentialBlob;
        public uint Persist; public uint AttributeCount; public IntPtr Attributes;
        public string TargetAlias; public string UserName;
    }
    [DllImport("advapi32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
    public static extern bool CredReadW(string target, uint type, uint flags, out IntPtr credential);
    [DllImport("advapi32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
    public static extern bool CredWriteW(ref CREDENTIAL credential, uint flags);
    [DllImport("advapi32.dll", SetLastError = true)]
    public static extern void CredFree(IntPtr buffer);
    public static string ReadPassword(string target) {
        IntPtr p;
        if (!CredReadW(target, 1, 0, out p)) return null;
        try {
            CREDENTIAL c = (CREDENTIAL)Marshal.PtrToStructure(p, typeof(CREDENTIAL));
            if (c.CredentialBlob == IntPtr.Zero || c.CredentialBlobSize == 0) return null;
            return Marshal.PtrToStringUni(c.CredentialBlob, (int)(c.CredentialBlobSize / 2));
        } finally { CredFree(p); }
    }
    public static void WritePassword(string target, string user, string password) {
        CREDENTIAL c = new CREDENTIAL();
        c.Type = 1; c.TargetName = target; c.UserName = user; c.Persist = 2;
        c.CredentialBlob = Marshal.StringToCoTaskMemUni(password);
        c.CredentialBlobSize = (uint)(password.Length * 2);
        try { if (!CredWriteW(ref c, 0)) throw new System.ComponentModel.Win32Exception(Marshal.GetLastWin32Error()); }
        finally { Marshal.FreeCoTaskMem(c.CredentialBlob); }
    }
}
'@
if (-not ('CredMan' -as [type])) { Add-Type -TypeDefinition $sig -Language CSharp | Out-Null }

$token = $null
if (-not $NoStore) {
    $token = [CredMan]::ReadPassword($CredTarget)
    if ($token) { Ok '已从 Windows 凭据管理器读取上次保存的 token' }
}
while (-not $token) {
    Write-Host ''
    Warn '需要 GitHub Personal Access Token'
    Write-Host '    如果之前给 ETO-Girl-Life- 建过 token，可在该 token 的设置页把 Qqsp-zh_CN 也加进' -ForegroundColor Gray
    Write-Host '    Repository access，即可复用同一个 token；或新建一个：' -ForegroundColor Gray
    Write-Host '    https://github.com/settings/personal-access-tokens/new' -ForegroundColor Gray
    Write-Host '    类型 Fine-grained；Repository access 选 Qqsp-zh_CN' -ForegroundColor Gray
    Write-Host '    Permissions -> Repository permissions -> Contents 设为 Read and write' -ForegroundColor Gray
    $sec = Read-Host '粘贴 token（输入时不显示）' -AsSecureString
    $bstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($sec)
    try { $token = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($bstr) }
    finally { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr) }
    if (-not $token) { Warn '输入为空，请重试' }
}
if (-not $NoStore) {
    try { [CredMan]::WritePassword($CredTarget, $Owner, $token); Ok 'token 已保存到 Windows 凭据管理器' }
    catch { Warn "token 未能保存（不影响本次发布）: $($_.Exception.Message)" }
}

# ---------- 3. http client ----------
Add-Type -AssemblyName System.Net.Http
$handler = New-Object Net.Http.HttpClientHandler
$client  = New-Object Net.Http.HttpClient($handler)
$client.Timeout = [TimeSpan]::FromHours(1)
$client.DefaultRequestHeaders.UserAgent.ParseAdd('Qqsp-Release-Script')
$client.DefaultRequestHeaders.Authorization =
    New-Object Net.Http.Headers.AuthenticationHeaderValue('Bearer', $token)
$client.DefaultRequestHeaders.Accept.ParseAdd('application/vnd.github+json')
$client.DefaultRequestHeaders.Add('X-GitHub-Api-Version', '2022-11-28')

function ApiJson($method, $url, $bodyObj) {
    $req = New-Object Net.Http.HttpRequestMessage([Net.Http.HttpMethod]::$method, $url)
    if ($bodyObj) {
        $json = $bodyObj | ConvertTo-Json -Compress -Depth 5
        $req.Content = New-Object Net.Http.StringContent($json, [Text.Encoding]::UTF8, 'application/json')
    }
    $res = $client.SendAsync($req).GetAwaiter().GetResult()
    $txt = $res.Content.ReadAsStringAsync().GetAwaiter().GetResult()
    return [pscustomobject]@{ Code = [int]$res.StatusCode; Text = $txt }
}

# ---------- 4. verify token / repo ----------
$chk = ApiJson 'Get' "$Api" $null
if ($chk.Code -eq 401) { Die 'token 无效或已过期' }
if ($chk.Code -eq 404) { Die "仓库不可见或 token 没有 Qqsp-zh_CN 的权限: $Owner/$Repo" }
if ($chk.Code -ne 200) { Die "校验仓库失败 HTTP $($chk.Code): $($chk.Text)" }
Ok ("token 有效，仓库: {0}" -f ($chk.Text | ConvertFrom-Json).full_name)

# ---------- 5. release ----------
$rel = $null
$exist = ApiJson 'Get' "$Api/releases/tags/$Tag" $null
if ($exist.Code -eq 200) {
    $rel = $exist.Text | ConvertFrom-Json
    Info "release 已存在（id $($rel.id)）"
} else {
    $body = @"
解压后双击 `Qqsp.exe` 即可运行，**开箱即中文界面**，无需另外安装 Qt 运行库。

### 包内内容

| 文件 | 说明 |
|---|---|
| `Qqsp.exe` | 已汉化（窗口标题、菜单、选项、引擎错误提示均为中文） |
| `Qqsp.zh_CN.qm` | 简体中文语言包（414 条词条 / 37 个上下文） |
| `Qqsp.zh-CN.qm` | 连字符别名，防止界面回英文（见 README 第五节） |
| `Qqsp.exe.bak` | 原始未汉化版本，改名为 `Qqsp.exe` 覆盖即可还原 |
| `Qt5*.dll`、`plugins/` | Qt 运行库，随包提供 |
| `vc_redist.x64.exe` | Visual C++ 运行库安装程序（提示缺少 dll 时运行） |

### 汉化范围

主窗口全部菜单与工具栏、各面板标题、选项对话框全部条目、关于对话框、Qt 的文件选择 / 字体 / 颜色 / 消息框等标准对话框按钮，以及程序内部的引擎错误提示与窗口标题。

游戏剧情文本在 `.qsp` 游戏文件内部，不在此列 —— 那是另一个汉化工程。

### 校验

```
SHA256  7f1d2d011187ae6268d3777ecd8268131d18ca4c7e575cf0827bd82f252e00f9
```

包内 `Qqsp.exe` 的 SHA256 为 `390ce5d37ac793e10d43d70c6cad037a8e7587be7889dc95a64974e16cf7eb18`，
可由本仓库 `original/Qqsp.exe` 经 `tools/patch_exe2.py` 逐字节复现。

### 许可

汉化以 MIT 发布。上游 [ezsh/Qqsp](https://github.com/ezsh/Qqsp) 同为 MIT（Copyright © 2017-2018 Sonnix）。
"@
    $bodyObj = @{ tag_name = $Tag; target_commitish = $Branch; name = $RelName; body = $body; draft = $false; prerelease = $false; make_latest = 'true' }
    $mk = ApiJson 'Post' "$Api/releases" $bodyObj
    if ($mk.Code -eq 422 -and $mk.Text -match 'already_exists') {
        $rel = (ApiJson 'Get' "$Api/releases/tags/$Tag" $null).Text | ConvertFrom-Json
        Info 'tag 已存在，复用该 release'
    } elseif ($mk.Code -ne 201) {
        Die "创建 release 失败 HTTP $($mk.Code): $($mk.Text)"
    } else {
        $rel = $mk.Text | ConvertFrom-Json
        Ok "release 已创建: $($rel.html_url)"
    }
}

# ---------- 6. asset ----------
$already = @($rel.assets | Where-Object { $_.name -eq $AssetName })
if ($already.Count -gt 0 -and -not $Force) {
    Ok "附件已存在，跳过上传（要重传请加 -Force）: $AssetName"
} else {
    if ($already.Count -gt 0) {
        $del = ApiJson 'Delete' "$Api/releases/assets/$($already[0].id)" $null
        Info "已删除旧附件（HTTP $($del.Code)）"
    }
    Info ("上传 {0}（{1:N1} MB）..." -f $AssetName, ($len / 1MB))
    $fs = [IO.File]::OpenRead($AssetSrc)
    try {
        $content = New-Object Net.Http.StreamContent($fs)
        $content.Headers.ContentType = New-Object Net.Http.Headers.MediaTypeHeaderValue('application/octet-stream')
        $content.Headers.ContentLength = $len
        $upUri = "https://uploads.github.com/repos/$Owner/$Repo/releases/$($rel.id)/assets?name=$AssetName"
        $sw = [Diagnostics.Stopwatch]::StartNew()
        try {
            $resp  = $client.PostAsync($upUri, $content).GetAwaiter().GetResult()
            $upTxt = $resp.Content.ReadAsStringAsync().GetAwaiter().GetResult()
            $code  = [int]$resp.StatusCode
        } finally { $sw.Stop() }
    } finally { $fs.Dispose() }

    if ($code -eq 201) {
        $asset = $upTxt | ConvertFrom-Json
        Ok ("上传成功 {0:N1} MB，用时 {1:N1} 秒" -f ($len / 1MB), $sw.Elapsed.TotalSeconds)
        Info "下载地址: $($asset.browser_download_url)"
    } else {
        Die "上传失败 HTTP ${code}: $upTxt"
    }
}

# ---------- 7. summary ----------
Write-Host ''
Write-Host '=== 完成 ===' -ForegroundColor Cyan
Write-Host "Release 页面: https://github.com/$Owner/$Repo/releases/tag/$Tag" -ForegroundColor Cyan
Write-Host "全部 Releases: https://github.com/$Owner/$Repo/releases" -ForegroundColor Cyan
Write-Host ''
Read-Host '按回车键退出'
