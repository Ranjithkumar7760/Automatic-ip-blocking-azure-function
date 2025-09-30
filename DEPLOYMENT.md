# 🚀 Deployment Guide - Azure Malicious IP Blocker

## Quick Deployment Checklist

- [ ] Azure resources created
- [ ] Environment variables configured
- [ ] Permissions assigned
- [ ] Code deployed
- [ ] Function tested

---

## 📋 Pre-Deployment Verification

### 1. Verify Azure Resources

```bash
# Check if resources exist
az group show --name rg-malicious-ip-blocker
az functionapp show --name func-malicious-ip-blocker --resource-group rg-malicious-ip-blocker
az webapp show --name app-target-service --resource-group rg-malicious-ip-blocker
```

### 2. Verify Environment Variables

```bash
# Check Function App configuration
az functionapp config appsettings list --name func-malicious-ip-blocker --resource-group rg-malicious-ip-blocker
```

Required variables:
- `WORKSPACE_ID`
- `SUBSCRIPTION_ID`
- `RESOURCE_GROUP`
- `APP_SERVICE_NAME`
- `ABUSEIPDB_API_KEY`

---

## 🔧 Deployment Methods

### Method 1: Azure CLI (Recommended)

```bash
# 1. Login to Azure
az login

# 2. Set default subscription
az account set --subscription "<your-subscription-id>"

# 3. Navigate to project directory
cd functionapp-root

# 4. Deploy function
func azure functionapp publish func-malicious-ip-blocker --python
```

### Method 2: ZIP Deployment

```bash
# 1. Create deployment package
zip -r deployment.zip . -x "*.git*" "*__pycache__*" "*.venv*"

# 2. Deploy via Azure CLI
az functionapp deployment source config-zip \
  --resource-group rg-malicious-ip-blocker \
  --name func-malicious-ip-blocker \
  --src deployment.zip
```

### Method 3: GitHub Actions (CI/CD)

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy Azure Function

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Setup Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Deploy to Azure Functions
      uses: Azure/functions-action@v1
      with:
        app-name: func-malicious-ip-blocker
        package: .
        publish-profile: ${{ secrets.AZURE_FUNCTIONAPP_PUBLISH_PROFILE }}
```

---

## ✅ Post-Deployment Testing

### 1. Manual Function Trigger

```bash
# Trigger function manually
az functionapp function invoke \
  --resource-group rg-malicious-ip-blocker \
  --name func-malicious-ip-blocker \
  --function-name blockMaliciousIps
```

### 2. Check Function Logs

```bash
# View recent logs
az functionapp log tail \
  --resource-group rg-malicious-ip-blocker \
  --name func-malicious-ip-blocker
```

### 3. Verify Timer Trigger

1. **Azure Portal** → Function App → Functions → blockMaliciousIps
2. **Monitor tab** → Check execution history
3. **Verify** function runs every 30 minutes

### 4. Test IP Blocking

```bash
# Check current IP restrictions
az webapp config access-restriction list \
  --resource-group rg-malicious-ip-blocker \
  --name app-target-service
```

---

## 🔍 Troubleshooting Deployment Issues

### Issue: Function deployment fails

**Solution:**
```bash
# Check function app status
az functionapp show --name func-malicious-ip-blocker --resource-group rg-malicious-ip-blocker --query "state"

# Restart if needed
az functionapp restart --name func-malicious-ip-blocker --resource-group rg-malicious-ip-blocker
```

### Issue: Permission denied errors

**Solution:**
```bash
# Verify managed identity
az functionapp identity show --name func-malicious-ip-blocker --resource-group rg-malicious-ip-blocker

# Check role assignments
az role assignment list --assignee <function-app-principal-id>
```

### Issue: Environment variables not set

**Solution:**
```bash
# Set missing variables
az functionapp config appsettings set \
  --name func-malicious-ip-blocker \
  --resource-group rg-malicious-ip-blocker \
  --settings "WORKSPACE_ID=<your-workspace-id>"
```

---

## 📊 Monitoring Setup

### 1. Enable Application Insights

```bash
# Create Application Insights
az monitor app-insights component create \
  --app func-malicious-ip-blocker-insights \
  --location eastus \
  --resource-group rg-malicious-ip-blocker

# Link to Function App
az functionapp config appsettings set \
  --name func-malicious-ip-blocker \
  --resource-group rg-malicious-ip-blocker \
  --settings "APPINSIGHTS_INSTRUMENTATIONKEY=<instrumentation-key>"
```

### 2. Set up Alerts

```bash
# Create alert for function failures
az monitor metrics alert create \
  --name "Function Failures" \
  --resource-group rg-malicious-ip-blocker \
  --scopes "/subscriptions/<subscription-id>/resourceGroups/rg-malicious-ip-blocker/providers/Microsoft.Web/sites/func-malicious-ip-blocker" \
  --condition "count FunctionExecutionCount < 1" \
  --window-size 1h \
  --evaluation-frequency 15m
```

---

## 🔄 Update Deployment

### Rolling Updates

```bash
# 1. Test locally first
func start

# 2. Deploy updated version
func azure functionapp publish func-malicious-ip-blocker --python

# 3. Verify deployment
az functionapp function show \
  --resource-group rg-malicious-ip-blocker \
  --name func-malicious-ip-blocker \
  --function-name blockMaliciousIps
```

### Rollback Strategy

```bash
# 1. List deployment history
az functionapp deployment list-publishing-profiles \
  --name func-malicious-ip-blocker \
  --resource-group rg-malicious-ip-blocker

# 2. Rollback to previous version (if using slots)
az functionapp deployment slot swap \
  --resource-group rg-malicious-ip-blocker \
  --name func-malicious-ip-blocker \
  --slot staging \
  --target-slot production
```

---

## 🛡️ Production Deployment Best Practices

### 1. Use Deployment Slots

```bash
# Create staging slot
az functionapp deployment slot create \
  --name func-malicious-ip-blocker \
  --resource-group rg-malicious-ip-blocker \
  --slot staging

# Deploy to staging first
func azure functionapp publish func-malicious-ip-blocker --slot staging

# Test staging, then swap
az functionapp deployment slot swap \
  --resource-group rg-malicious-ip-blocker \
  --name func-malicious-ip-blocker \
  --slot staging \
  --target-slot production
```

### 2. Environment-Specific Configuration

```bash
# Production settings
az functionapp config appsettings set \
  --name func-malicious-ip-blocker \
  --resource-group rg-malicious-ip-blocker \
  --slot-settings "ENVIRONMENT=production"
```

### 3. Health Checks

```bash
# Add health check endpoint
az functionapp config set \
  --name func-malicious-ip-blocker \
  --resource-group rg-malicious-ip-blocker \
  --generic-configurations '{"healthCheckPath": "/api/health"}'
```

---

## 📈 Performance Optimization

### 1. Function App Settings

```bash
# Optimize for performance
az functionapp config appsettings set \
  --name func-malicious-ip-blocker \
  --resource-group rg-malicious-ip-blocker \
  --settings \
    "FUNCTIONS_WORKER_PROCESS_COUNT=4" \
    "PYTHON_THREADPOOL_THREAD_COUNT=8"
```

### 2. Connection Pooling

Add to `requirements.txt`:
```
requests[security]>=2.28.0
urllib3>=1.26.0
```

### 3. Caching Strategy

Consider implementing Redis cache for frequently checked IPs:

```bash
# Create Redis cache
az redis create \
  --name cache-malicious-ip-blocker \
  --resource-group rg-malicious-ip-blocker \
  --location eastus \
  --sku Basic \
  --vm-size c0
```

---

## 🔐 Security Hardening

### 1. Network Security

```bash
# Enable VNet integration
az functionapp vnet-integration add \
  --name func-malicious-ip-blocker \
  --resource-group rg-malicious-ip-blocker \
  --vnet MyVNet \
  --subnet MySubnet
```

### 2. Key Vault Integration

```bash
# Create Key Vault
az keyvault create \
  --name kv-malicious-ip-blocker \
  --resource-group rg-malicious-ip-blocker \
  --location eastus

# Store API key
az keyvault secret set \
  --vault-name kv-malicious-ip-blocker \
  --name "AbuseIPDB-API-Key" \
  --value "<your-api-key>"

# Update function app to use Key Vault reference
az functionapp config appsettings set \
  --name func-malicious-ip-blocker \
  --resource-group rg-malicious-ip-blocker \
  --settings "ABUSEIPDB_API_KEY=@Microsoft.KeyVault(VaultName=kv-malicious-ip-blocker;SecretName=AbuseIPDB-API-Key)"
```

---

## 📋 Deployment Checklist

### Pre-Deployment
- [ ] All Azure resources created
- [ ] Environment variables configured
- [ ] Permissions assigned correctly
- [ ] AbuseIPDB API key obtained
- [ ] Local testing completed

### Deployment
- [ ] Code deployed successfully
- [ ] Function app started
- [ ] Timer trigger configured
- [ ] Logs accessible

### Post-Deployment
- [ ] Manual function execution tested
- [ ] Automatic timer execution verified
- [ ] IP blocking functionality tested
- [ ] Monitoring and alerts configured
- [ ] Documentation updated

### Production Readiness
- [ ] Application Insights enabled
- [ ] Health checks implemented
- [ ] Backup and recovery plan
- [ ] Security review completed
- [ ] Performance testing done

---

**Deployment Status**: Ready for Production 🚀