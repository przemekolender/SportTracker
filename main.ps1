$ErrorActionPreference="Stop"

Remove-Item log.txt
New-Item log.txt

try{
    & {
        Write-Output "Switching to correct branch $(Get-Date -Format "dd.MM.yyyy HH:mm:ss")`n"
        git checkout main
    
        Write-Output "Pulling code $(Get-Date -Format "dd.MM.yyyy HH:mm:ss")`n"
        git pull origin main
    
        Write-Output "Activating enviorement $(Get-Date -Format "dd.MM.yyyy HH:mm:ss")`n"
        .\sporttracker_env\Scripts\Activate.ps1
    
        Write-Output "Running python code $(Get-Date -Format "dd.MM.yyyy HH:mm:ss")`n"
        python -u main.py 
        if ($LASTEXITCODE -ne 0) { throw "There was an error in Python code`n$out" }
    
        Write-Output "Adding new files to git $(Get-Date -Format "dd.MM.yyyy HH:mm:ss")`n"
        #git add files
    
        Write-Output "Commit and push to GitHub $(Get-Date -Format "dd.MM.yyyy HH:mm:ss")`n"
        $date = Get-Date -Format "dd.MM.yyyy HH:mm"
        #git commit -m "Update files, $date"
        #git push origin main
    
        Write-Output "Script finished with success $(Get-Date -Format "dd.MM.yyyy HH:mm:ss")`n"
    
     } | Tee-Object -FilePath log.txt
}
catch {
    $_ | Tee-Object -FilePath log.txt -Append
}

