# 🏗️ Azure Resources Setup Guide

## Complete Step-by-Step Azure Portal Setup

This guide walks you through creating all required Azure resources manually using the Azure Portal.

---

## 🎯 Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    Azure Subscription                          │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Resource Group                             │   │
│  │  rg-malicious-ip-blocker                               │   │
│  │                                                         │   │
│  │  ┌─────────────────┐  ┌─────────────────┐             │   │
│  │  │ Log Analytics   │  │   App Service   │             │   │
│  │  │   Workspace     │◄─┤   (Target)      │             │   │
│  │  │                 │  │                 │             │   │
│  │  └─────────────────┘  └─────────────────┘             │   │
│  │           ▲                                            │   │
│  │           │                                            │   │
│  │  ┌─────────────────┐  ┌─────────────────┐             │   │
│  │  │ Azure Function  │  │ Storage Account │             │   │
│  │  │     App         │──┤                 │             │   │
│  │  │                 │  │                 │             │   │
│  │  └─────────────────┘  └─────────────────┘             │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────────────┐
                    │   AbuseIPDB     │
                    │      API        │
                    └─────────────────┘
```

---

## 📋 Prerequisites

- **Azure Account**: Active Azure subscription
- **Permissions**: Contributor access to subscription
- **AbuseIPDB Account**: Free account at https://www.abuseipdb.com
- **Browser**: Modern web browser for Azure Portal

---

# 🚀 Step 1: Create Resource Group

## 1.1 Navigate to Resource Groups

1. **Open Azure Portal**: https://portal.azure.com
2. **Sign in** with your Azure account
3. **Click "Resource groups"** in the left navigation menu
   - If not visible, click "All services" and search for "Resource groups"

## 1.2 Create New Resource Group

1. **Click "+ Create"** button at the top
2. **Fill in the details**:
   - **Subscription**: Select your Azure subscription
   - **Resource group name**: `rg-malicious-ip-blocker`
   - **Region**: `East US` (or your preferred region)

3. **Click "Review + create"**
4. **Click "Create"** after validation passes

## 1.3 Verification

- **Wait for deployment** to complete (usually 10-30 seconds)
- **Click "Go to resource group"**
- **Verify** the resource group is created successfully

---

# 🚀 Step 2: Create Log Analytics Workspace

## 2.1 Navigate to Log Analytics

1. **In Azure Portal**, click the search bar at the top
2. **Type "Log Analytics"** and select "Log Analytics workspaces"
3. **Click "+ Create"**

## 2.2 Configure Workspace

1. **Basics tab**:
   - **Subscription**: Your Azure subscription
   - **Resource group**: `rg-malicious-ip-blocker`
   - **Name**: `law-malicious-ip-blocker`
   - **Region**: `East US` (same as resource group)

2. **Pricing tier**: Leave as default (Pay-as-you-go)

3. **Click "Review + create"**
4. **Click "Create"**

## 2.3 Get Workspace ID

1. **Wait for deployment** to complete
2. **Click "Go to resource"**
3. **Navigate to "Settings"** → **"Agents management"**
4. **Copy the "Workspace ID"** (format: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx)
5. **Save this ID** - you'll need it later

---

# 🚀 Step 3: Create Target App Service

## 3.1 Navigate to App Services

1. **In Azure Portal**, search for **"App Services"**
2. **Click "App Services"**
3. **Click "+ Create"**

## 3.2 Configure App Service

1. **Basics tab**:
   - **Subscription**: Your Azure subscription
   - **Resource group**: `rg-malicious-ip-blocker`
   - **Name**: `app-target-service-[random]` (must be globally unique)
   - **Publish**: Code
   - **Runtime stack**: Python 3.9
   - **Operating System**: Linux
   - **Region**: `East US`

2. **App Service Plan**:
   - **Linux Plan**: Create new
   - **Name**: `asp-malicious-ip-blocker`
   - **Pricing tier**: `Basic B1` (or Free F1 for testing)

3. **Click "Review + create"**
4. **Click "Create"**

## 3.3 Enable Diagnostic Settings

1. **Wait for deployment** and **go to resource**
2. **Navigate to "Monitoring"** → **"Diagnostic settings"**
3. **Click "+ Add diagnostic setting"**
4. **Configure**:
   - **Diagnostic setting name**: `AppServiceLogs`
   - **Categories**: Check **"AppServiceHTTPLogs"**
   - **Destination details**: Check **"Send to Log Analytics workspace"**
   - **Subscription**: Your subscription
   - **Log Analytics workspace**: `law-malicious-ip-blocker`
5. **Click "Save"**

---

# 🚀 Step 4: Create Storage Account

## 4.1 Navigate to Storage Accounts

1. **Search for "Storage accounts"** in Azure Portal
2. **Click "Storage accounts"**
3. **Click "+ Create"**

## 4.2 Configure Storage Account

1. **Basics tab**:
   - **Subscription**: Your Azure subscription
   - **Resource group**: `rg-malicious-ip-blocker`
   - **Storage account name**: `stmaliciousipblocker[random]` (lowercase, no special chars)
   - **Region**: `East US`
   - **Performance**: Standard
   - **Redundancy**: Locally-redundant storage (LRS)

2. **Advanced tab**: Leave defaults
3. **Networking tab**: Leave defaults
4. **Data protection tab**: Leave defaults
5. **Encryption tab**: Leave defaults
6. **Tags tab**: Optional

7. **Click "Review + create"**
8. **Click "Create"**

---

# 🚀 Step 5: Create Function App

## 5.1 Navigate to Function App

1. **Search for "Function App"** in Azure Portal
2. **Click "Function App"**
3. **Click "+ Create"**

## 5.2 Configure Function App

1. **Basics tab**:
   - **Subscription**: Your Azure subscription
   - **Resource group**: `rg-malicious-ip-blocker`
   - **Function App name**: `func-malicious-ip-blocker-[random]`
   - **Publish**: Code
   - **Runtime stack**: Python
   - **Version**: 3.9
   - **Region**: `East US`

2. **Hosting tab**:
   - **Storage account**: Select `stmaliciousipblocker[random]`
   - **Operating system**: Linux
   - **Plan type**: Consumption (Serverless)

3. **Monitoring tab**:
   - **Enable Application Insights**: Yes
   - **Application Insights**: Create new
   - **Name**: `appi-malicious-ip-blocker`

4. **Click "Review + create"**
5. **Click "Create"**

---

# 🚀 Step 6: Configure Managed Identity

## 6.1 Enable System Assigned Identity

1. **Go to Function App** → `func-malicious-ip-blocker-[random]`
2. **Navigate to "Settings"** → **"Identity"**
3. **System assigned tab**:
   - **Status**: Toggle to **"On"**
   - **Click "Save"**
   - **Click "Yes"** to confirm

4. **Copy the "Object (principal) ID"** - save for later

---

# 🚀 Step 7: Assign Permissions

## 7.1 Log Analytics Reader Permission

1. **Go to Log Analytics Workspace** → `law-malicious-ip-blocker`
2. **Navigate to "Access control (IAM)"**
3. **Click "+ Add"** → **"Add role assignment"**
4. **Role tab**:
   - **Role**: Search and select **"Log Analytics Reader"**
   - **Click "Next"**
5. **Members tab**:
   - **Assign access to**: Managed identity
   - **Click "+ Select members"**
   - **Managed identity**: Function App
   - **Select**: `func-malicious-ip-blocker-[random]`
   - **Click "Select"**
6. **Click "Review + assign"**
7. **Click "Review + assign"** again

## 7.2 Website Contributor Permission

1. **Go to App Service** → `app-target-service-[random]`
2. **Navigate to "Access control (IAM)"**
3. **Click "+ Add"** → **"Add role assignment"**
4. **Role tab**:
   - **Role**: Search and select **"Website Contributor"**
   - **Click "Next"**
5. **Members tab**:
   - **Assign access to**: Managed identity
   - **Click "+ Select members"**
   - **Managed identity**: Function App
   - **Select**: `func-malicious-ip-blocker-[random]`
   - **Click "Select"**
6. **Click "Review + assign"**
7. **Click "Review + assign"** again

---

# 🚀 Step 8: Get AbuseIPDB API Key

## 8.1 Create AbuseIPDB Account

1. **Visit**: https://www.abuseipdb.com/
2. **Click "Register"** (top right)
3. **Fill in registration form**:
   - Email address
   - Username
   - Password
   - Complete captcha
4. **Click "Register"**
5. **Verify email** (check your inbox)

## 8.2 Get API Key

1. **Login to AbuseIPDB**
2. **Click your username** (top right) → **"API"**
3. **Copy your API Key** (format: your-api-key-here)
4. **Save this key** - you'll need it for configuration

---

# 🚀 Step 9: Configure Environment Variables

## 9.1 Get Required Values

Before configuring, collect these values:

| Variable | Where to Find | Example |
|----------|---------------|---------|
| `WORKSPACE_ID` | Log Analytics → Agents management | `12345678-1234-1234-1234-123456789012` |
| `SUBSCRIPTION_ID` | Portal → Subscriptions | `87654321-4321-4321-4321-210987654321` |
| `RESOURCE_GROUP` | Resource group name | `rg-malicious-ip-blocker` |
| `APP_SERVICE_NAME` | App Service name | `app-target-service-[random]` |
| `ABUSEIPDB_API_KEY` | AbuseIPDB account | `your-api-key-here` |

## 9.2 Configure Function App Settings

1. **Go to Function App** → `func-malicious-ip-blocker-[random]`
2. **Navigate to "Settings"** → **"Configuration"**
3. **Application settings tab**
4. **For each variable, click "+ New application setting"**:

### Setting 1: WORKSPACE_ID
- **Name**: `WORKSPACE_ID`
- **Value**: `<your-workspace-id-from-step-2>`
- **Click "OK"**

### Setting 2: SUBSCRIPTION_ID
- **Name**: `SUBSCRIPTION_ID`
- **Value**: `<your-subscription-id>`
- **Click "OK"**

### Setting 3: RESOURCE_GROUP
- **Name**: `RESOURCE_GROUP`
- **Value**: `rg-malicious-ip-blocker`
- **Click "OK"**

### Setting 4: APP_SERVICE_NAME
- **Name**: `APP_SERVICE_NAME`
- **Value**: `<your-app-service-name>`
- **Click "OK"**

### Setting 5: ABUSEIPDB_API_KEY
- **Name**: `ABUSEIPDB_API_KEY`
- **Value**: `<your-abuseipdb-api-key>`
- **Click "OK"**

5. **Click "Save"** at the top
6. **Click "Continue"** to confirm restart

---

# 🚀 Step 10: Verification Checklist

## 10.1 Resource Verification

- [ ] **Resource Group**: `rg-malicious-ip-blocker` created
- [ ] **Log Analytics**: `law-malicious-ip-blocker` created and workspace ID noted
- [ ] **App Service**: `app-target-service-[random]` created with diagnostic settings
- [ ] **Storage Account**: `stmaliciousipblocker[random]` created
- [ ] **Function App**: `func-malicious-ip-blocker-[random]` created

## 10.2 Configuration Verification

- [ ] **Managed Identity**: Enabled on Function App
- [ ] **Permissions**: Log Analytics Reader assigned
- [ ] **Permissions**: Website Contributor assigned
- [ ] **Environment Variables**: All 5 variables configured
- [ ] **AbuseIPDB**: API key obtained and configured

## 10.3 Test Connectivity

### Test Log Analytics Access
1. **Go to Function App** → **"Console"** (under Development Tools)
2. **Run**: `az account show` (should show your subscription)

### Test App Service Access
1. **Go to App Service** → **"Access control (IAM)"**
2. **Verify** Function App identity has Website Contributor role

---

# 🚀 Step 11: Generate Test Traffic (Optional)

## 11.1 Create Simple Test App

1. **Go to App Service** → `app-target-service-[random]`
2. **Navigate to "Development Tools"** → **"App Service Editor"**
3. **Create file**: `app.py`

```python
from flask import Flask, request
import logging

app = Flask(__name__)

@app.route('/')
def home():
    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
    app.logger.info(f"Request from IP: {client_ip}")
    return f"Hello from {client_ip}!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
```

4. **Create file**: `requirements.txt`
```
Flask==2.3.3
```

5. **Save files** and **restart App Service**

## 11.2 Generate Traffic

1. **Visit your App Service URL** multiple times
2. **Wait 5-10 minutes** for logs to appear
3. **Check logs** in Log Analytics:
   - Go to Log Analytics Workspace
   - Navigate to "Logs"
   - Run query:
   ```kusto
   AppServiceHTTPLogs
   | where TimeGenerated > ago(1h)
   | project TimeGenerated, CIp, CsMethod, CsUriStem
   ```

---

# 🎯 Next Steps

After completing this setup:

1. **Deploy the Function Code** (see DEPLOYMENT.md)
2. **Test the Function** manually
3. **Monitor execution** logs
4. **Verify IP blocking** functionality

---

# 🔧 Troubleshooting Common Issues

## Issue: Can't find resources in portal
**Solution**: Ensure you're in the correct subscription and region

## Issue: Permission denied errors
**Solution**: Verify managed identity is enabled and roles are assigned correctly

## Issue: Function app won't start
**Solution**: Check all environment variables are set correctly

## Issue: No logs in Log Analytics
**Solution**: Verify diagnostic settings are configured and App Service is receiving traffic

---

# 💰 Cost Estimation

## Monthly Cost Breakdown (East US region)

| Resource | Tier | Estimated Cost |
|----------|------|----------------|
| Function App | Consumption | $0-5 |
| App Service | Basic B1 | $13.14 |
| Storage Account | Standard LRS | $1-3 |
| Log Analytics | Pay-as-you-go | $2-10 |
| **Total** | | **~$16-31/month** |

## Cost Optimization Tips

1. **Use Free tier** App Service for testing
2. **Set log retention** policies in Log Analytics
3. **Monitor Function executions** to avoid overuse
4. **Use consumption plan** for Function App

---

**Setup Status**: ✅ Ready for Code Deployment

**Next**: Follow the [DEPLOYMENT.md](DEPLOYMENT.md) guide to deploy your function code.