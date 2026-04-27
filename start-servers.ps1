# Kill all node and python processes
Get-Process -Name node -ErrorAction SilentlyContinue | Stop-Process -Force
Get-Process -Name python -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 2

# Start backend
$backendJob = Start-Job -ScriptBlock {
    Set-Location "C:\Users\sidev\Desktop\GTM\backend"
    python -m uvicorn main:app --host 0.0.0.0 --port 8000
}

# Start frontend
$frontendJob = Start-Job -ScriptBlock {
    Set-Location "C:\Users\sidev\Desktop\GTM\frontend"
    npm run dev
}

Write-Host "Servers starting..."
Write-Host "Backend: http://localhost:8000"
Write-Host "Frontend: http://localhost:3000"