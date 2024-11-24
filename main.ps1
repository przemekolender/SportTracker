& {
    Write-Output "Switching to correct branch...`n"
    git checkout main
    Write-Output "`nFinished switching to correct branch`n`n"

    Write-Output "Pulling code...`n"
    git pull origin main
    Write-Output "`nFinished pulling code`n`n"

    Write-Output "Activating enviorement...`n"
    .\sporttracker_env\Scripts\Activate.ps1
    Write-Output "`nFinished activating enviorement`n`n"

    Write-Output "Running python code...`n"
    python main.py
    Write-Output "`nFinished running python code`n`n"

    Write-Output "Adding new files to git...`n"
    git add files
    Write-Output "`nFinished adding new files to git`n`n"

    Write-Output "Commit and push to GitHub...`n"
    $date = Get-Date -Format "dd/MM/yyyy HH:mm"
    git commit -m "Update files, $date"
    git push origin main
    Write-Output "`nFinished Commit and push to GitHub`n`n"
} 2>&1 | Tee-Object -FilePath log.txt