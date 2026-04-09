# ==== CONEXIÓN ================================================================
Disconnect-MgGraph -ErrorAction SilentlyContinue | Out-Null
Connect-MgGraph -TenantId "terrauniversalis.onmicrosoft.com" -Scopes "Sites.ReadWrite.All","Files.ReadWrite.All","User.Read" | Out-Null

$hostname = "terrauniversalis.sharepoint.com"
$rootSite = Invoke-MgGraphRequest -Method GET -Uri "https://graph.microsoft.com/v1.0/sites/$hostname"
$rootSiteId = $rootSite.id

function Normalize([string]$s){ $s=$s.ToLowerInvariant(); $s=$s.Normalize([Text.NormalizationForm]::FormD) -replace '\p{Mn}',''; ($s -replace '[^a-z0-9]+',' ').Trim() }
function ScoreMatch([string]$name,[string[]]$need){ $n=Normalize $name; $best=0; foreach($t in $need){ $m=0; foreach($w in (Normalize $t).Split()){ if($n -like "*$w*"){ $m++ } }; if($m -gt $best){$best=$m} }; $best }

$sites = @([pscustomobject]@{ id=$rootSiteId; webUrl=$rootSite.webUrl; displayName=$rootSite.displayName })
$subs  = Invoke-MgGraphRequest -Method GET -Uri "https://graph.microsoft.com/v1.0/sites/$rootSiteId/sites?`$select=id,webUrl,displayName&`$top=200"
if ($subs.value){ $sites += $subs.value }

$allLists=@()
foreach($s in $sites){
  $ls = Invoke-MgGraphRequest -Method GET -Uri "https://graph.microsoft.com/v1.0/sites/$($s.id)/lists?`$select=id,displayName,webUrl&`$top=500"
  foreach($l in $ls.value){ $allLists += [pscustomobject]@{ siteId=$s.id; siteUrl=$s.webUrl; listId=$l.id; listName=$l.displayName; listUrl=$l.webUrl } }
}

$targets=@{
  infraestructura          = @("infraestructura","audio","equipos","hardware")
  identitamosmappings      = @("identitamosmappings","identita","mappings","mapeos","mapping")
  normateca_template_blank = @("normateca_template_blank","normateca","normativa","template")
  systemas                 = @("systemas","sistemas","systems")
}
$resolved=@{}
foreach($k in $targets.Keys){
  $cand = $allLists | Sort-Object @{Expression={ ScoreMatch $_.listName $targets[$k] } ; Descending=$true } | Select-Object -First 1
  if($cand){ $resolved[$k]=$cand }
}

$infraSiteId = $resolved['infraestructura'].siteId
$infraListId = $resolved['infraestructura'].listId
$mapsSiteId  = $resolved['identitamosmappings'].siteId
$mapsListId  = $resolved['identitamosmappings'].listId

function Ensure-TextColumn {
  param([string]$SiteId,[string]$ListId,[string]$Name)
  $cols = Invoke-MgGraphRequest -Method GET -Uri "https://graph.microsoft.com/v1.0/sites/$SiteId/lists/$ListId/columns?`$select=name"
  if ($cols.value.name -icontains $Name) { return }
  $body = @{ name=$Name; text=@{ allowMultipleLines=$false } } | ConvertTo-Json
  Invoke-MgGraphRequest -Method POST -Uri "https://graph.microsoft.com/v1.0/sites/$SiteId/lists/$ListId/columns" -Body $body -ContentType 'application/json' | Out-Null
}
function Ensure-Lookup {
  param([string]$TargetSiteId,[string]$TargetListId,[string]$LookupName,[string]$SourceListId,[string]$SourceColumnName)
  $cols = Invoke-MgGraphRequest -Method GET -Uri "https://graph.microsoft.com/v1.0/sites/$TargetSiteId/lists/$TargetListId/columns?`$select=name"
  if ($cols.value.name -icontains $LookupName) { return }
  $body = @{ name=$LookupName; lookup=@{ listId=$SourceListId; columnName=$SourceColumnName; allowMultipleValues=$false } } | ConvertTo-Json
  Invoke-MgGraphRequest -Method POST -Uri "https://graph.microsoft.com/v1.0/sites/$TargetSiteId/lists/$TargetListId/columns" -Body $body -ContentType 'application/json' | Out-Null
}

Ensure-TextColumn -SiteId $mapsSiteId -ListId $mapsListId -Name "Equipment_ID"
Ensure-TextColumn -SiteId $mapsSiteId -ListId $mapsListId -Name "ColorHex"
Ensure-TextColumn -SiteId $mapsSiteId -ListId $mapsListId -Name "PaginaLayer"
Ensure-TextColumn -SiteId $mapsSiteId -ListId $mapsListId -Name "Zona"
Ensure-TextColumn -SiteId $mapsSiteId -ListId $mapsListId -Name "AppObjetivo"
Ensure-TextColumn -SiteId $mapsSiteId -ListId $mapsListId -Name "MappingHash"
Ensure-Lookup     -TargetSiteId $mapsSiteId -TargetListId $mapsListId -LookupName "InfraRef" -SourceListId $infraListId -SourceColumnName "Equipment_ID"

[pscustomobject]@{
  RootSiteId               = $rootSiteId
  Infraestructura_List     = $resolved['infraestructura']
  IdentitamosMappings_List = $resolved['identitamosmappings']
} | Format-List
