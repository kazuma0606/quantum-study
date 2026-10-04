# フォルダ内の HTML（tools/render_all_figs.py の出力）を、Edge のヘッドレスモードで PNG にする。
#
# 実行（PowerShell）:
#   powershell -ExecutionPolicy Bypass -File tools/screenshot_html.ps1 出力フォルダ [幅] [高さ]
# 既定の大きさは 1000x560。plotly の図は CDN から読み込むので、ネットワーク接続が必要。

param(
    [Parameter(Mandatory = $true)][string]$Folder,
    [int]$Width = 1000,
    [int]$Height = 560
)

$edge = "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
if (-not (Test-Path $edge)) { throw "Edge が見つかりません: $edge" }
$dir = (Resolve-Path $Folder).Path
Get-ChildItem (Join-Path $dir "*.html") | ForEach-Object {
    $png = Join-Path $dir ($_.BaseName + ".png")
    $url = "file:///" + ($_.FullName -replace '\\', '/')
    Start-Process -FilePath $edge -Wait -NoNewWindow -ArgumentList @(
        "--headless=new", "--disable-gpu", "--window-size=$Width,$Height",
        "--virtual-time-budget=8000", "--screenshot=`"$png`"", "`"$url`""
    ) 2>$null
    Write-Output "保存: $png"
}
