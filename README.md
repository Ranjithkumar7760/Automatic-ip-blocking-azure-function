# Azure Malicious IP Blocking System

## 📋 Project Overview

This project implements an **automated security system** that monitors Azure App Service traffic and automatically blocks malicious IP addresses using threat intelligence from AbuseIPDB. The system runs as an Azure Function that executes every 30 minutes to analyze logs and update IP restrictions.

### 🎯 Key Features
- **Automated Monitoring**: Continuously monitors App Service HTTP logs
- **Threat Intelligence**: Integrates with AbuseIPDB for IP reputation checking
- **Auto-Blocking**: Automatically updates App Service IP restrictions
- **Scheduled Execution**: Runs every 30 minutes via timer trigger
- **Logging**: Comprehensive logging for monitoring and debugging

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   App Service   │───▶│  Log Analytics   │───▶│ Azure Function  │
│   (Target)      │    │   Workspace      │    │ (blockMalicious │
└─────────────────┘    └──────────────────┘    │     IPs)        │
                                               └─────────────────┘
                                                        │
                                               ┌─────────────────┐
                                               │   AbuseIPDB     │
                                               │      API        │
                                               └─────────────────┘
```

## 🛠️ Prerequisites

- Azure Subscription
- AbuseIPDB API Key (free tier available)
- Azure CLI or PowerShell (for deployment)
- Python 3.8+ (for local development)

---

# 🚀 Step-by-Step Azure Setup Guide

## Step 1: Create Resource Group

1. **Login to Azure Portal**: https://portal.azure.com
2. **Navigate to Resource Groups**:
   - Click "Resource groups" in the left menu
   - Click "+ Create"
3. **Configure Resource Group**:
   - **Subscription**: Select your subscription
   - **Resource group name**: `rg-malicious-ip-blocker`
   - **Region**: Choose your preferred region (e.g., East US)
   - Click "Review + create" → "Create"

## Step 2: Create Log Analytics Workspace

1. **Search for "Log Analytics"** in the Azure Portal search bar
2. **Click "Log Analytics workspaces"** → "+ Create"
3. **Configure Workspace**:
   - **Subscription**: Your subscription
   - **Resource group**: `rg-malicious-ip-blocker`
   - **Name**: `law-malicious-ip-blocker`
   - **Region**: Same as resource group
   - Click "Review + create" → "Create"
4. **Note the Workspace ID**:
   - After creation, go to the workspace
   - Navigate to "Settings" → "Agents management"
   - Copy the **Workspace ID** (save for later)

## Step 3: Create Target App Service

1. **Search for "App Services"** → Click "+ Create"
2. **Configure App Service**:
   - **Subscription**: Your subscription
   - **Resource group**: `rg-malicious-ip-blocker`
   - **Name**: `app-target-service` (must be globally unique)
   - **Runtime stack**: Choose your preferred (e.g., Python 3.9)
   - **Operating System**: Linux
   - **Region**: Same as resource group
   - **Pricing plan**: Choose appropriate tier
3. **Click "Review + create"** → "Create"

## Step 4: Enable App Service Logging

1. **Go to your App Service** → `app-target-service`
2. **Navigate to "Monitoring"** → "Diagnostic settings"
3. **Click "+ Add diagnostic setting"**:
   - **Name**: `AppServiceLogs`
   - **Categories**: Check "AppServiceHTTPLogs"
   - **Destination**: Check "Send to Log Analytics workspace"
   - **Subscription**: Your subscription
   - **Log Analytics workspace**: `law-malicious-ip-blocker`
   - Click "Save"

## Step 5: Create Storage Account (for Function App)

1. **Search for "Storage accounts"** → "+ Create"
2. **Configure Storage**:
   - **Subscription**: Your subscription
   - **Resource group**: `rg-malicious-ip-blocker`
   - **Name**: `stmaliciousipblocker` (lowercase, no special chars)
   - **Region**: Same as resource group
   - **Performance**: Standard
   - **Redundancy**: LRS (Locally redundant storage)
3. **Click "Review + create"** → "Create"

## Step 6: Create Function App

1. **Search for "Function App"** → "+ Create"
2. **Configure Function App**:
   - **Subscription**: Your subscription
   - **Resource group**: `rg-malicious-ip-blocker`
   - **Function App name**: `func-malicious-ip-blocker`
   - **Runtime stack**: Python
   - **Version**: 3.9
   - **Region**: Same as resource group
   - **Storage account**: `stmaliciousipblocker`
   - **Operating System**: Linux
   - **Plan type**: Consumption (Serverless)
3. **Click "Review + create"** → "Create"

## Step 7: Configure Function App Identity

1. **Go to Function App** → `func-malicious-ip-blocker`
2. **Navigate to "Settings"** → "Identity"
3. **System assigned tab**:
   - **Status**: On
   - Click "Save" → "Yes"
4. **Note the Object (principal) ID** (save for later)

## Step 8: Assign Required Permissions

### 8.1 Log Analytics Reader Permission
1. **Go to Log Analytics Workspace** → `law-malicious-ip-blocker`
2. **Navigate to "Access control (IAM)"** → "+ Add" → "Add role assignment"
3. **Configure Assignment**:
   - **Role**: Log Analytics Reader
   - **Assign access to**: Managed identity
   - **Members**: Select your Function App (`func-malicious-ip-blocker`)
   - Click "Review + assign"

### 8.2 App Service Contributor Permission
1. **Go to App Service** → `app-target-service`
2. **Navigate to "Access control (IAM)"** → "+ Add" → "Add role assignment"
3. **Configure Assignment**:
   - **Role**: Website Contributor
   - **Assign access to**: Managed identity
   - **Members**: Select your Function App (`func-malicious-ip-blocker`)
   - Click "Review + assign"

## Step 9: Get AbuseIPDB API Key

1. **Visit**: https://www.abuseipdb.com/
2. **Create Account** (free tier available)
3. **Navigate to**: Account → API
4. **Copy your API Key** (save for later)

## Step 10: Configure Function App Environment Variables

1. **Go to Function App** → `func-malicious-ip-blocker`
2. **Navigate to "Settings"** → "Configuration"
3. **Add Application Settings** (click "+ New application setting" for each):

| Name | Value | Description |
|------|-------|-------------|
| `WORKSPACE_ID` | `<your-workspace-id>` | From Step 2 |
| `SUBSCRIPTION_ID` | `<your-subscription-id>` | Your Azure subscription ID |
| `RESOURCE_GROUP` | `rg-malicious-ip-blocker` | Resource group name |
| `APP_SERVICE_NAME` | `app-target-service` | Target App Service name |
| `ABUSEIPDB_API_KEY` | `<your-api-key>` | From Step 9 |

4. **Click "Save"** after adding all variables

---

# 💻 Local Development Setup

## 1. Clone/Setup Project Structure

```bash
mkdir functionapp-root
cd functionapp-root
mkdir blockMaliciousIps
```

## 2. Install Azure Functions Core Tools

```bash
# Windows (using npm)
npm install -g azure-functions-core-tools@4 --unsafe-perm true

# Or using chocolatey
choco install azure-functions-core-tools
```

## 3. Create Virtual Environment

```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac
```

## 4. Install Dependencies

```bash
pip install -r requirements.txt
```

## 5. Local Configuration

Create `local.settings.json` in project root:

```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "WORKSPACE_ID": "<your-workspace-id>",
    "SUBSCRIPTION_ID": "<your-subscription-id>",
    "RESOURCE_GROUP": "rg-malicious-ip-blocker",
    "APP_SERVICE_NAME": "app-target-service",
    "ABUSEIPDB_API_KEY": "<your-api-key>"
  }
}
```

---

# 🚀 Deployment Guide

## Method 1: Azure Portal Deployment

1. **Go to Function App** → `func-malicious-ip-blocker`
2. **Navigate to "Deployment"** → "Deployment Center"
3. **Choose Source**: Local Git, GitHub, or ZIP deploy
4. **Upload your code** using chosen method

## Method 2: Azure CLI Deployment

```bash
# Login to Azure
az login

# Deploy function app
func azure functionapp publish func-malicious-ip-blocker
```

## Method 3: VS Code Deployment

1. **Install Azure Functions Extension**
2. **Open project in VS Code**
3. **Press F1** → "Azure Functions: Deploy to Function App"
4. **Select your Function App**

---

# 📊 Monitoring and Troubleshooting

## View Function Logs

1. **Go to Function App** → `func-malicious-ip-blocker`
2. **Navigate to "Functions"** → "blockMaliciousIps"
3. **Click "Monitor"** to view execution logs

## Check Application Insights

1. **Function App** → "Application Insights"
2. **View logs, metrics, and performance data**

## Common Issues

### Issue: Function not triggering
- **Check**: Timer trigger configuration in `function.json`
- **Verify**: Function App is running (not stopped)

### Issue: Permission errors
- **Verify**: Managed identity is enabled
- **Check**: Role assignments are correct
- **Ensure**: All required permissions are granted

### Issue: No logs found
- **Verify**: App Service diagnostic settings are configured
- **Check**: Log Analytics workspace connection
- **Ensure**: App Service is receiving traffic

---

# 🔧 Configuration Reference

## Environment Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `WORKSPACE_ID` | Yes | Log Analytics Workspace ID | `12345678-1234-1234-1234-123456789012` |
| `SUBSCRIPTION_ID` | Yes | Azure Subscription ID | `87654321-4321-4321-4321-210987654321` |
| `RESOURCE_GROUP` | Yes | Resource Group Name | `rg-malicious-ip-blocker` |
| `APP_SERVICE_NAME` | Yes | Target App Service Name | `app-target-service` |
| `ABUSEIPDB_API_KEY` | Yes | AbuseIPDB API Key | `your-api-key-here` |

## Timer Schedule Format

The function uses CRON expression: `0 */30 * * * *`
- Runs every 30 minutes
- Format: `{second} {minute} {hour} {day} {month} {day-of-week}`

## Customization Options

### Change execution frequency
Edit `function.json`:
```json
{
  "schedule": "0 0 */6 * * *"  // Every 6 hours
}
```

### Modify lookback period
Edit `__init__.py`:
```python
query = f"""
AppServiceHTTPLogs
| where TimeGenerated > ago(12h)  // Changed from 24h to 12h
| where isnotempty(CIp)
| summarize by CIp
"""
```

---

# 🛡️ Security Considerations

## Best Practices

1. **API Key Security**: Store AbuseIPDB API key in Azure Key Vault for production
2. **Least Privilege**: Function identity has minimal required permissions
3. **Network Security**: Consider VNet integration for enhanced security
4. **Monitoring**: Enable Application Insights for comprehensive monitoring

## Production Recommendations

1. **Use Azure Key Vault** for sensitive configuration
2. **Enable Application Insights** for detailed monitoring
3. **Set up alerts** for function failures
4. **Implement retry logic** for API calls
5. **Add rate limiting** for AbuseIPDB API calls

---

# 📈 Cost Optimization

## Estimated Monthly Costs

- **Function App (Consumption)**: ~$0-5 (based on executions)
- **Log Analytics**: ~$2-10 (based on data ingestion)
- **Storage Account**: ~$1-3 (minimal usage)
- **App Service**: Variable (based on chosen tier)

## Cost Reduction Tips

1. **Optimize query timespan** based on your needs
2. **Use consumption plan** for Function App
3. **Set log retention policies** in Log Analytics
4. **Monitor AbuseIPDB API usage** (free tier: 1000 requests/day)

---

# 🤝 Contributing

## Development Workflow

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/enhancement`
3. **Make changes and test locally**
4. **Commit changes**: `git commit -m "Add enhancement"`
5. **Push to branch**: `git push origin feature/enhancement`
6. **Create Pull Request**

## Testing

```bash
# Run function locally
func start

# Test with specific timer
func run blockMaliciousIps --content '{"isPastDue": false}'
```

---

# 📞 Support

For issues and questions:
1. **Check logs** in Application Insights
2. **Review configuration** settings
3. **Verify permissions** and role assignments
4. **Test API connectivity** to AbuseIPDB

---

**Project Status**: ✅ Production Ready  
**Last Updated**: 2024  
**Version**: 1.0.0