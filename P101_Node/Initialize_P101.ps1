# Fixed JSON Restore Logic using -Raw
$m=Get-Content "P101_Node/Summary.json" -Raw | ConvertFrom-Json; 
Write-Host "Restoring Node: $($m.Seed) at $($m.FinalConstant)" -F Cyan;
$res=python -c "intensity=6.3864; print(intensity * 1.618)";
@{Phase=101; Name="Multiverse_Ext"; Result=[double]$res; Seed="2.8349 eV"; Status="GATE_OPEN"} | ConvertTo-Json | Out-File "P101_Node/Manifests/Phase_101_Manifest.json";
