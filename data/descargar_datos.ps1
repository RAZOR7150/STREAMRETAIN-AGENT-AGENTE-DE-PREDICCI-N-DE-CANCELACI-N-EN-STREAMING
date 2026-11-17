# Descarga de soporte: no procesa filas ni entrena modelos.
# Requiere Kaggle CLI autenticado y reglas aceptadas en la web de la competencia.
$ErrorActionPreference = 'Stop'
$destinoDatos = Join-Path $PSScriptRoot 'kkbox-churn-prediction-challenge'
$archivoDatos = Join-Path $destinoDatos 'transactions.csv.7z'
$manifiesto = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'manifest.json') -Raw | ConvertFrom-Json
if (-not (Test-Path -LiteralPath $archivoDatos)) {
    if (-not (Get-Command kaggle -ErrorAction SilentlyContinue)) {
        throw 'Instala Kaggle CLI: python -m pip install kaggle. Autentica y acepta las reglas antes de descargar.'
    }
    New-Item -ItemType Directory -Force -Path $destinoDatos | Out-Null
    & kaggle competitions download -c kkbox-churn-prediction-challenge -f transactions.csv.7z -p $destinoDatos
    if ($LASTEXITCODE -ne 0) { throw 'Kaggle no pudo descargar. Revisa autenticacion, acceso y reglas; no compartas tus credenciales.' }
}
if (-not (Test-Path -LiteralPath $archivoDatos -PathType Leaf)) {
    throw 'No se encontro transactions.csv.7z. Revisa el formato entregado por Kaggle o descarga el archivo manualmente.'
}
if ((Get-Item -LiteralPath $archivoDatos).Length -ne $manifiesto.bytes) {
    throw 'El tamano difiere del archivo usado en el hito 2. No se borra ni se sobrescribe; revisar descarga/version.'
}
$huellaDatos = (Get-FileHash -LiteralPath $archivoDatos -Algorithm SHA256).Hash.ToLowerInvariant()
if ($huellaDatos -ne $manifiesto.sha256) {
    throw 'SHA-256 diferente de la referencia. Revisar integridad/version antes de reproducir.'
}
Write-Output 'Datos disponibles y SHA-256 coincidente. No se extrajo el CSV ni se procesaron filas.'
Write-Output $archivoDatos
