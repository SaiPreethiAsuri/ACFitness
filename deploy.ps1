# ------------------------------
# AC Fitness App Deployment Script
# ------------------------------
param (
    [string]$Strategy = ""
)

$localPort = 9090

# Mapping YAML file names to actual Kubernetes service names
$serviceMap = @{
    "blue-service.yaml"          = "acfitness-app-blue-service"
    "green-service.yaml"         = "acfitness-app-green-service"
    "canary-service.yaml"        = "acfitness-app-canary-service"
    "shadow-service.yaml"        = "acfitness-app-shadow-service"
    "rollingupdate-service.yaml" = "acfitness-app-rollingupdate-service"
    "stable-service.yaml"        = "acfitness-app-stable-service"
    "service.yaml"               = "fitness-app-service"
}

# Deployment definitions
$deployments = @(
    @{ name = "acfitness-app-blue"; yaml = "k8s/strategies/blue-green-deployment.yaml"; services = @("blue-service.yaml"); ports = @(9092) },
    @{ name = "acfitness-app-green"; yaml = "k8s/strategies/blue-green-deployment.yaml"; services = @("green-service.yaml"); ports = @(9093) },
    @{ name = "acfitness-app-stable"; yaml = "k8s/strategies/canary.yaml"; services = @("stable-service.yaml"); ports = @(9095) },
    @{ name = "acfitness-app-canary"; yaml = "k8s/strategies/canary.yaml"; services = @("canary-service.yaml"); ports = @(9091) },
    @{ name = "acfitness-app-shadow"; yaml = "k8s/strategies/shadow.yaml"; services = @("shadow-service.yaml"); ports = @(9094) },
    @{ name = "acfitness-app-rollingupdate"; yaml = "k8s/strategies/rolling-update.yaml"; services = @("rollingupdate-service.yaml"); ports = @(9097) }
)

# Check if Minikube is running
$minikubeStatus = & minikube status --format "{{.Host}}"
if ($minikubeStatus -ne "Running") {
    Write-Host "Minikube is not running. Please start Minikube first." -ForegroundColor Red
    exit 1
}

Write-Host "Minikube is running. Proceeding with deployment..." -ForegroundColor Cyan

# Configure Docker to use Minikube
Write-Host "Configuring Docker to use Minikube Docker environment..."
minikube docker-env --shell powershell | Invoke-Expression

# Build Docker image
Write-Host "Building Docker image: fitness-app:latest..." -ForegroundColor Yellow
docker build -t fitness-app:latest .

# Deploy base manifests
Write-Host "Deploying base Kubernetes resources..."
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

$ContinueAfterSwitch = $true
Write-Host "Selected Strategy: $Strategy" -ForegroundColor Magenta

switch ($Strategy.ToLower()) {
    "blue" {
        $deploymentFile = "k8s/strategies/blue.yaml"
        $serviceFile = "k8s/strategies/blue-service.yaml"
        $port = 9092
    }
    "green" {
        $deploymentFile = "k8s/strategies/green.yaml"
        $serviceFile = "k8s/strategies/green-service.yaml"
        $port = 9093
    }
    "canary" {
        $deploymentFile = "k8s/strategies/canary.yaml"
        $serviceFile = "k8s/strategies/canary-service.yaml"
        $port = 9091
    }
    "shadow" {
        $deploymentFile = "k8s/strategies/shadow.yaml"
        $serviceFile = "k8s/strategies/shadow-service.yaml"
        $port = 9094
    }
    "rollingupdate" {
        $deploymentFile = "k8s/strategies/rolling-update.yaml"
        $serviceFile = "k8s/strategies/rollingupdate-service.yaml"
        $port = 9097
    }
    "all" {
        Write-Host "Deploying all strategies..."
        foreach ($dep in $deployments) {

            kubectl apply -f $dep.yaml

            foreach ($svcFile in $dep.services) {
                kubectl apply -f k8s/strategies/$svcFile
            }

            Write-Host "Restarting deployment $($dep.name)..."
            kubectl rollout restart deployment $($dep.name)

            # ✅ Wait for deployment to be available
            Write-Host "Waiting for deployment $($dep.name) to become ready..."
            kubectl wait deployment/$($dep.name) --for=condition=available --timeout=50s
        }

        Start-Sleep -Seconds 5

        # Port forward for all strategies
        foreach ($dep in $deployments) {
            for ($i = 0; $i -lt $dep.services.Count; $i++) {

                $svcFile = $dep.services[$i]
                $svcName = $serviceMap[$svcFile]
                $port = $dep.ports[$i]

                if (-not $svcName) {
                    Write-Host "❌ No mapping found for $svcFile" -ForegroundColor Red
                    continue
                }

                Write-Host "Starting port-forward for service $svcName on port $port..."

                Start-Process powershell -ArgumentList @(
                    "-NoExit",
                    "-Command",
                    "kubectl port-forward svc/$svcName `"$port`:80`""
                )

                Start-Process "http://127.0.0.1:$port"
                Start-Sleep -Seconds 2
            }
        }

        $ContinueAfterSwitch = $false
    }
    default {
        $deploymentFile = "k8s/deployment.yaml"
        $serviceFile = "k8s/service.yaml"
        $port = $localPort
    }
}

# Handle normal strategy deploy
if ($ContinueAfterSwitch) {
    Write-Host "Deploying strategy: $Strategy using $deploymentFile..."
    kubectl apply -f $deploymentFile
    kubectl apply -f $serviceFile

    Write-Host "Restarting deployment..."
    kubectl rollout restart deployment acfitness-app

    # ✅ Wait for single-strategy deployment to be ready
    Write-Host "Waiting for deployment acfitness-app to become ready..."
    kubectl wait deployment/acfitness-app --for=condition=available --timeout=50s

    Start-Sleep -Seconds 3

    # Extract correct service name
    $fileName = Split-Path $serviceFile -Leaf
    $svcName = $serviceMap[$fileName]

    if (-not $svcName) {
        Write-Host "❌ No mapping found for $fileName" -ForegroundColor Red
        exit 1
    }

    Write-Host "Port-forwarding for service: $svcName"

    Start-Process powershell -ArgumentList @(
        "-NoExit",
        "-Command",
        "kubectl port-forward svc/$svcName `"$port`:80`""
    )

    Start-Process "http://127.0.0.1:$port"
}

Write-Host "Deployment script finished. Your app may take a few seconds to be ready." -ForegroundColor Green
