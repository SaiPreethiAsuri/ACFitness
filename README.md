# ACEest Fitness & Gym – DevOps CI/CD Pipeline Project

This repository contains the complete CI/CD implementation for the ACEest Fitness & Gym application as part of the MTech DevOps assignment.  
It demonstrates a full end-to-end DevOps workflow including version control, automated testing, CI pipeline, containerization, static code analysis, and Kubernetes deployment.

---

## 🚀 Project Overview

ACEest Fitness & Gym is a Flask-based fitness tracking application developed incrementally through multiple versions:

- `ACEest_Fitness.py`  
- `ACEest_Fitness-V1.1.py`  
- `ACEest_Fitness-V1.2.py`  
- `ACEest_Fitness-V1.2.1.py`  
- `ACEest_Fitness-V1.2.2.py`  
- `ACEest_Fitness-V1.2.3.py`  
- `ACEest_Fitness-V1.3.py`

This repository contains the **final stable application source code**, along with the CI/CD automation files and deployment artifacts.

---

# ✅ Features Implemented

### ✅ **Flask Application**
- User Info Management (Name, Age, Gender, Height, Weight)
- Workout logging (Warm-up, Workout, Cool-down)
- Calorie calculation using MET values
- Weekly summary view
- Progress visualization (Charts)
- PDF export (with ReportLab fallback)

---

# ✅ **DevOps Tools Used**

| Category | Tool |
|---------|------|
| Version Control | Git + GitHub |
| CI Server | Jenkins |
| Build Automation | Jenkins Pipeline + Shell |
| Unit Testing | Pytest |
| Code Quality | SonarQube |
| Containerization | Docker (or Podman) |
| Image Registry | Docker Hub |
| Deployment | Minikube (Kubernetes) |
| Deployment Strategies | Blue-Green, Canary, Rolling Update, Shadow, A/B Testing |

---
**CI/CD Pipeline Architecture**

### ✅ **1. Continuous Integration (Handled by Jenkins)**

Jenkins automates:

- Source code pull from GitHub  
- Pytest execution  
- SonarQube static analysis  
- Docker image build  
- Docker image tagging  
- Docker image push to Docker Hub  

Every commit triggers a new CI pipeline run.

### ✅ **2. Continuous Delivery (Handled manually on Minikube)**

Deployment is done via Minikube using the deploy.ps1 file which contains all the scripts for deployment in local minikube
Prerequisites: The minikube and docker desktop should be started

Open Powershell in administrator mode and run the comand in the project directory ./deploy.ps1
By default , it runs the service deployment 
To mention the strategy the command should be modified --> ./deploy.ps1 -Strategy <Strategy Name>
To deploy all the strategies --> ./deploy.ps1 -Strategy all


Since Jenkins does not have access to the local Minikube cluster, **CD is intentionally executed locally**

---

# ✅ **Pipeline Workflow**

