"""
Service for fetching RI/SP recommendations from Azure Advisor and Consumption APIs.
"""
from datetime import datetime
from typing import Dict, List, Any, Optional
from .azure_client import AzureClientManager


class RecommendationService:
    """Fetches reservation and savings plan recommendations from Azure."""
    
    def __init__(self, tenant_id: str = None, client_id: str = None,
                 client_secret: str = None, subscription_id: str = None):
        self.azure = AzureClientManager(tenant_id, client_id, client_secret, subscription_id)
        self.scope = f"/subscriptions/{self.azure.subscription_id}"
    
    def get_reservation_recommendations(self) -> List[Dict[str, Any]]:
        """
        Get VM Reserved Instance recommendations from Azure Consumption API.
        Returns recommendations with potential savings.
        """
        recommendations = []
        
        try:
            # Get reservation recommendations
            result = self.azure.consumption_client.reservation_recommendations.list(
                scope=self.scope,
                filter="properties/scope eq 'Shared'"
            )
            
            for rec in result:
                # Extract properties based on recommendation type
                props = rec.as_dict()
                
                recommendations.append({
                    "id": props.get("id", ""),
                    "name": props.get("name", ""),
                    "sku": props.get("sku_properties", {}).get("name", "Unknown"),
                    "location": props.get("location", ""),
                    "term": props.get("term", "P1Y"),  # P1Y = 1 year, P3Y = 3 years
                    "look_back_period": props.get("look_back_period", "Last30Days"),
                    "recommended_quantity": props.get("recommended_quantity", 0),
                    "cost_with_no_ri": round(props.get("cost_with_no_reserved_instances", 0), 2),
                    "cost_with_ri": round(props.get("total_cost_with_reserved_instances", 0), 2),
                    "net_savings": round(props.get("net_savings", 0), 2),
                    "savings_percent": self._calculate_savings_percent(
                        props.get("cost_with_no_reserved_instances", 0),
                        props.get("total_cost_with_reserved_instances", 0)
                    ),
                    "first_usage_date": props.get("first_usage_date", ""),
                    "scope": props.get("scope", "Shared"),
                    "resource_type": props.get("resource_type", "VirtualMachines"),
                    "recommendation_type": "RI",
                    "fetched_at": datetime.utcnow().isoformat()
                })
        
        except Exception as e:
            print(f"Error fetching reservation recommendations: {e}")
        
        return recommendations
    
    def get_savings_plan_recommendations(self) -> List[Dict[str, Any]]:
        """
        Get Savings Plan recommendations from Azure Consumption API.
        
        Savings Plans offer flexible discounts across VM families/regions,
        unlike RIs which are locked to specific SKU/region combinations.
        
        Uses the benefit_recommendations endpoint which returns both
        Savings Plan and potentially newer benefit types.
        """
        recommendations = []
        
        try:
            # The benefit_recommendations API requires the scope parameter
            # For subscription-level: /subscriptions/{subscription-id}
            result = self.azure.consumption_client.benefit_recommendations.list(
                scope=self.scope
            )
            
            for rec in result:
                props = rec.as_dict()
                
                # Filter for Savings Plan recommendations only
                kind = props.get("kind", "")
                if kind and "SavingsPlan" not in kind:
                    continue
                
                # Extract usage and cost properties
                usage = props.get("usage", {})
                properties = props.get("properties", {})
                
                # Get term - Savings Plans support P1Y (1 year) or P3Y (3 years)
                term = properties.get("term", "P1Y")
                term_display = "1-Year" if term == "P1Y" else "3-Year" if term == "P3Y" else term
                
                # Get lookback period used for recommendation
                look_back = properties.get("look_back_period", "Last30Days")
                
                # Cost calculations
                cost_without_benefit = properties.get("cost_without_benefit", 0)
                total_cost = properties.get("total_cost", 0)
                savings_amount = cost_without_benefit - total_cost
                
                # Commitment details
                commitment = properties.get("commitment", {})
                commitment_amount = commitment.get("amount", 0)
                commitment_currency = commitment.get("currency_code", "USD")
                commitment_grain = commitment.get("grain", "Hourly")
                
                # Scope recommendation (Single, Shared, or specific resource group)
                scope_rec = properties.get("scope", "Shared")
                
                recommendations.append({
                    "id": props.get("id", ""),
                    "name": props.get("name", ""),
                    "kind": kind,
                    "recommendation_type": "SP",
                    "term": term,
                    "term_display": term_display,
                    "look_back_period": look_back,
                    
                    # Cost analysis
                    "cost_without_sp": round(cost_without_benefit, 2),
                    "cost_with_sp": round(total_cost, 2),
                    "net_savings": round(savings_amount, 2),
                    "savings_percent": self._calculate_savings_percent(
                        cost_without_benefit, total_cost
                    ),
                    
                    # Commitment details
                    "hourly_commitment": round(commitment_amount, 4),
                    "commitment_currency": commitment_currency,
                    "commitment_grain": commitment_grain,
                    
                    # Monthly equivalent (for easier comparison)
                    "monthly_commitment": round(commitment_amount * 730, 2),
                    
                    # Coverage
                    "scope": scope_rec,
                    "benefit_type": "SavingsPlan",
                    
                    # Usage pattern info
                    "usage_grain": usage.get("grain", ""),
                    "first_consumption_date": usage.get("first_consumption_date", ""),
                    "last_consumption_date": usage.get("last_consumption_date", ""),
                    
                    # Metadata
                    "fetched_at": datetime.utcnow().isoformat()
                })
        
        except AttributeError as e:
            # benefit_recommendations may not be available in older SDK versions
            print(f"Savings Plan API not available (SDK version issue): {e}")
            print("Falling back to Advisor-based SP recommendations...")
            return self._get_sp_from_advisor()
        
        except Exception as e:
            print(f"Error fetching savings plan recommendations: {e}")
        
        return recommendations
    
    def _get_sp_from_advisor(self) -> List[Dict[str, Any]]:
        """
        Fallback: Get Savings Plan recommendations from Azure Advisor.
        
        Advisor includes SP recommendations in the Cost category with
        recommendation_type_id containing 'SavingsPlan'.
        """
        recommendations = []
        
        try:
            result = self.azure.advisor_client.recommendations.list()
            
            for rec in result:
                props = rec.as_dict()
                
                # Filter for Cost category only
                if props.get("category") != "Cost":
                    continue
                
                # Check if this is a Savings Plan recommendation
                rec_type_id = props.get("recommendation_type_id", "")
                short_desc = props.get("short_description", {}).get("solution", "").lower()
                
                if "savingsplan" not in rec_type_id.lower() and "savings plan" not in short_desc:
                    continue
                
                extended = props.get("extended_properties", {})
                
                recommendations.append({
                    "id": props.get("id", ""),
                    "name": props.get("name", ""),
                    "recommendation_type": "SP",
                    "source": "Advisor",
                    "impact": props.get("impact", ""),
                    "short_description": props.get("short_description", {}).get("solution", ""),
                    "description": props.get("short_description", {}).get("problem", ""),
                    "annual_savings": self._parse_savings(extended.get("annualSavingsAmount", "0")),
                    "savings_currency": extended.get("savingsCurrency", "USD"),
                    "term": extended.get("term", "P1Y"),
                    "look_back_period": extended.get("lookbackPeriod", "Last30Days"),
                    "resource_id": props.get("resource_metadata", {}).get("resource_id", ""),
                    "last_updated": props.get("last_updated", ""),
                    "fetched_at": datetime.utcnow().isoformat()
                })
        
        except Exception as e:
            print(f"Error fetching SP recommendations from Advisor: {e}")
        
        return recommendations

    def get_advisor_cost_recommendations(self) -> List[Dict[str, Any]]:
        """
        Get cost optimization recommendations from Azure Advisor.
        Includes RI recommendations and other cost savings.
        """
        recommendations = []
        
        try:
            # Get all recommendations, filter to Cost category
            result = self.azure.advisor_client.recommendations.list()
            
            for rec in result:
                props = rec.as_dict()
                
                # Only include Cost category recommendations
                if props.get("category") != "Cost":
                    continue
                
                # Parse extended properties for savings info
                extended = props.get("extended_properties", {})
                
                recommendations.append({
                    "id": props.get("id", ""),
                    "name": props.get("name", ""),
                    "category": props.get("category", ""),
                    "impact": props.get("impact", ""),  # High, Medium, Low
                    "impacted_field": props.get("impacted_field", ""),
                    "impacted_value": props.get("impacted_value", ""),
                    "short_description": props.get("short_description", {}).get("solution", ""),
                    "description": props.get("short_description", {}).get("problem", ""),
                    "recommendation_type_id": props.get("recommendation_type_id", ""),
                    "annual_savings": self._parse_savings(extended.get("annualSavingsAmount", "0")),
                    "savings_currency": extended.get("savingsCurrency", "USD"),
                    "region": extended.get("region", ""),
                    "sku": extended.get("currentSku", ""),
                    "target_sku": extended.get("targetSku", ""),
                    "resource_id": props.get("resource_metadata", {}).get("resource_id", ""),
                    "last_updated": props.get("last_updated", ""),
                    "fetched_at": datetime.utcnow().isoformat()
                })
        
        except Exception as e:
            print(f"Error fetching advisor recommendations: {e}")
        
        return recommendations
    
    def get_all_recommendations(self) -> Dict[str, Any]:
        """
        Get combined RI, SP, and Advisor recommendations with summary stats.
        
        UPDATED: Now includes Savings Plan recommendations.
        """
        ri_recs = self.get_reservation_recommendations()
        sp_recs = self.get_savings_plan_recommendations()
        advisor_recs = self.get_advisor_cost_recommendations()
        
        # Filter out SP recommendations from advisor if we got them from Consumption API
        # to avoid duplicates
        if sp_recs:
            advisor_recs = [
                r for r in advisor_recs 
                if "savings plan" not in r.get("short_description", "").lower()
            ]
        
        # Calculate totals
        ri_savings = sum(r.get("net_savings", 0) for r in ri_recs)
        sp_savings = sum(r.get("net_savings", 0) for r in sp_recs)
        advisor_savings = sum(r.get("annual_savings", 0) for r in advisor_recs)
        
        return {
            "reservation_recommendations": ri_recs,
            "savings_plan_recommendations": sp_recs,
            "advisor_recommendations": advisor_recs,
            "summary": {
                "total_ri_recommendations": len(ri_recs),
                "total_sp_recommendations": len(sp_recs),
                "total_advisor_recommendations": len(advisor_recs),
                "potential_ri_savings": round(ri_savings, 2),
                "potential_sp_savings": round(sp_savings, 2),
                "potential_advisor_savings": round(advisor_savings, 2),
                "total_potential_savings": round(ri_savings + sp_savings + advisor_savings, 2),
                "currency": "USD",
                "last_updated": datetime.utcnow().isoformat()
            }
        }
    
    def get_total_savings(self) -> float:
        """
        Get total potential savings from all recommendations.
        """
        try:
            all_recs = self.get_all_recommendations()
            return all_recs.get("summary", {}).get("total_potential_savings", 0)
        except Exception as e:
            print(f"Error getting total savings: {e}")
            return 0.0
    
    def get_ri_coverage(self) -> Dict[str, Any]:
        """
        Get current RI coverage percentage.
        """
        try:
            # This requires the Consumption API reservation summaries
            # Simplified version - in production, use reservation_summaries endpoint
            return {
                "coverage_percent": 4.0,  # Placeholder - will enhance
                "target_percent": 25.0,
                "note": "Full coverage calculation requires additional API setup",
                "last_updated": datetime.utcnow().isoformat()
            }
        except Exception as e:
            print(f"Error calculating RI coverage: {e}")
            return {"coverage_percent": 0, "error": str(e)}
    
    def _calculate_savings_percent(self, cost_without: float, cost_with: float) -> float:
        """Calculate savings percentage."""
        if cost_without <= 0:
            return 0.0
        savings = ((cost_without - cost_with) / cost_without) * 100
        return round(savings, 1)
    
    def _parse_savings(self, value: str) -> float:
        """Parse savings amount from string."""
        try:
            return float(value.replace(",", "").replace("$", ""))
        except (ValueError, AttributeError):
            return 0.0
