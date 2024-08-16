Write-Host "Switching to correct branch..."
git checkout prod
Write-Host "Done"

Write-Host "Pulling code..."
git pull origin prod
Write-Host "Done"

Write-Host "Activating enviorement..."
.\sporttracker_env\Scripts\Activate.ps1
Write-Host "Done"

Write-Host "Running python code..."
python main.py
Write-Host "Done"

Write-Host "Adding new files to git..."
git add files
Write-Host "Done"

Write-Host "Commit and push to GitHub..."
$date = Get-Date -Format "dd/MM/yyyy HH:mm"
git commit -m "Update files, $date"
git push origin prod
Write-Host "Done"


