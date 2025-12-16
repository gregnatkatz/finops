"""
Azure client wrapper for Cost Management and Advisor APIs.
Uses service principal authentication.
Supports both environment variables and dynamic credential injection.
"""
import os
from datetime import datetime, timedelta
from typing import Optional
from azure.identity import ClientSecretCredential
from azure.mgmt.costmanagement import CostManagementClient
from azure.mgmt.advisor import AdvisorManagementClient
from azure.mgmt.consumption import ConsumptionManagementClient
from azure.mgmt.resource import ResourceManagementClient


class AzureClientManager:
    """Manages Azure SDK client connections."""
    
    def __init__(self, tenant_id: str = None, client_id: str = None, 
                 client_secret: str = None, subscription_id: str = None):
        # Use provided credentials or fall back to environment variables
        self.tenant_id = tenant_id or os.getenv("AZURE_TENANT_ID")
        self.client_id = client_id or os.getenv("AZURE_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("AZURE_CLIENT_SECRET")
        self.subscription_id = subscription_id or os.getenv("AZURE_SUBSCRIPTION_ID")
        
        if not all([self.tenant_id, self.client_id, self.client_secret, self.subscription_id]):
            raise ValueError("Missing required Azure credentials")
        
        self._credential = None
        self._cost_client = None
        self._advisor_client = None
        self._consumption_client = None
        self._resource_client = None
    
    @property
    def credential(self) -> ClientSecretCredential:
        if self._credential is None:
            self._credential = ClientSecretCredential(
                tenant_id=self.tenant_id,
                client_id=self.client_id,
                client_secret=self.client_secret
            )
        return self._credential
    
    @property
    def cost_client(self) -> CostManagementClient:
        if self._cost_client is None:
            self._cost_client = CostManagementClient(
                credential=self.credential,
                subscription_id=self.subscription_id
            )
        return self._cost_client
    
    @property
    def advisor_client(self) -> AdvisorManagementClient:
        if self._advisor_client is None:
            self._advisor_client = AdvisorManagementClient(
                credential=self.credential,
                subscription_id=self.subscription_id
            )
        return self._advisor_client
    
    @property
    def consumption_client(self) -> ConsumptionManagementClient:
        if self._consumption_client is None:
            self._consumption_client = ConsumptionManagementClient(
                credential=self.credential,
                subscription_id=self.subscription_id
            )
        return self._consumption_client
    
    @property
    def resource_client(self) -> ResourceManagementClient:
        if self._resource_client is None:
            self._resource_client = ResourceManagementClient(
                credential=self.credential,
                subscription_id=self.subscription_id
            )
        return self._resource_client
    
    def list_resources(self) -> dict:
        """List all resources in the subscription and categorize them with details."""
        # Extended categories for better FinOps visibility
        categories = {
            "compute": {"count": 0, "resources": []},
            "databases": {"count": 0, "resources": []},
            "storage": {"count": 0, "resources": []},
            "containers": {"count": 0, "resources": []},
            "app_services": {"count": 0, "resources": []},
            "networking": {"count": 0, "resources": []},
            "analytics": {"count": 0, "resources": []},
            "ai_ml": {"count": 0, "resources": []},
            "security": {"count": 0, "resources": []},
            "other": {"count": 0, "resources": []},
        }
        
        result = {
            "categories": categories,
            "total": 0,
            "permission_error": False
        }
        
        try:
            print(f"[list_resources] Listing resources for subscription: {self.subscription_id}")
            resources = list(self.resource_client.resources.list())
            print(f"[list_resources] Found {len(resources)} resources")
            
            for resource in resources:
                resource_type = resource.type.lower() if resource.type else ""
                resource_info = {
                    "name": resource.name,
                    "type": resource.type,
                    "location": resource.location,
                    "resource_group": resource.id.split("/")[4] if resource.id and len(resource.id.split("/")) > 4 else ""
                }
                
                # Categorize by resource type
                if any(t in resource_type for t in ["virtualmachines", "vmss", "availabilitysets"]):
                    categories["compute"]["count"] += 1
                    categories["compute"]["resources"].append(resource_info)
                elif any(t in resource_type for t in ["sql", "cosmosdb", "documentdb", "postgresql", "mysql", "mariadb", "redis"]):
                    categories["databases"]["count"] += 1
                    categories["databases"]["resources"].append(resource_info)
                elif any(t in resource_type for t in ["storageaccounts", "disks", "snapshots", "blob"]):
                    categories["storage"]["count"] += 1
                    categories["storage"]["resources"].append(resource_info)
                elif any(t in resource_type for t in ["kubernetes", "containerservice", "containerinstance", "containerregistry", "containerapps"]):
                    categories["containers"]["count"] += 1
                    categories["containers"]["resources"].append(resource_info)
                elif any(t in resource_type for t in ["sites", "serverfarms", "functions", "logicapps", "staticsite"]):
                    categories["app_services"]["count"] += 1
                    categories["app_services"]["resources"].append(resource_info)
                elif any(t in resource_type for t in ["network", "virtualnetwork", "publicip", "loadbalancer", "applicationgateway", "firewall", "dns", "frontdoor", "cdn"]):
                    categories["networking"]["count"] += 1
                    categories["networking"]["resources"].append(resource_info)
                elif any(t in resource_type for t in ["synapse", "databricks", "datafactory", "eventhub", "streamanalytics", "hdinsight"]):
                    categories["analytics"]["count"] += 1
                    categories["analytics"]["resources"].append(resource_info)
                elif any(t in resource_type for t in ["cognitiveservices", "machinelearning", "openai", "search"]):
                    categories["ai_ml"]["count"] += 1
                    categories["ai_ml"]["resources"].append(resource_info)
                elif any(t in resource_type for t in ["keyvault", "managedidentity", "security"]):
                    categories["security"]["count"] += 1
                    categories["security"]["resources"].append(resource_info)
                else:
                    categories["other"]["count"] += 1
                    categories["other"]["resources"].append(resource_info)
            
            result["total"] = len(resources)
            
        except Exception as e:
            print(f"[list_resources] Error listing resources: {type(e).__name__}: {e}")
            result["permission_error"] = True
            result["error_message"] = str(e)
        
        return result


# Singleton instance
_azure_manager: Optional[AzureClientManager] = None

def get_azure_manager() -> AzureClientManager:
    global _azure_manager
    if _azure_manager is None:
        _azure_manager = AzureClientManager()
    return _azure_manager
