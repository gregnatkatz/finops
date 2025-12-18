"""
RI Reallocation Service

Analyzes existing Reserved Instances against active SaaS evaluations
to identify reallocation opportunities.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, date, timedelta
import logging

logger = logging.getLogger(__name__)


class ReallocationService:
    """
    Analyzes existing RIs and recommends reallocations when workloads
    are being evaluated for modernization or SaaS migration.
    """
    
    def __init__(self, azure_client=None, intelligence_service=None):
        self.azure_client = azure_client
        self.intelligence_service = intelligence_service
    
    def analyze_reallocation_opportunities(self, demo_mode: bool = False) -> Dict[str, Any]:
        """
        Main analysis: Cross-reference existing RIs with SaaS evaluations
        and new RI/SP recommendations to find reallocation opportunities.
        """
        if demo_mode:
            return self._get_demo_reallocation_opportunities()
        
        # Get current data from Azure
        existing_ris = self._get_existing_reservations()
        evaluations = self._get_active_evaluations()
        new_recommendations = self._get_new_recommendations()
        workloads = self._get_workloads()
        
        opportunities = []
        
        for ri in existing_ris:
            # Check if this RI is associated with a workload under evaluation
            affected_evaluation = self._find_affecting_evaluation(ri, evaluations, workloads)
            
            if affected_evaluation:
                # Find potential reallocation targets
                reallocation_targets = self._find_reallocation_targets(ri, new_recommendations, existing_ris)
                
                opportunity = {
                    "existing_ri": {
                        "id": ri.get("id"),
                        "name": ri.get("name"),
                        "sku": ri.get("sku"),
                        "location": ri.get("location"),
                        "monthly_cost": ri.get("monthly_cost", 0),
                        "utilization_percent": ri.get("utilization_percent", 0),
                        "expiry_date": ri.get("expiry_date"),
                        "remaining_term_months": self._calculate_remaining_months(ri.get("expiry_date")),
                    },
                    "at_risk_reason": {
                        "evaluation_id": affected_evaluation.get("id"),
                        "evaluation_name": affected_evaluation.get("name"),
                        "vendor": affected_evaluation.get("vendor"),
                        "adoption_probability": affected_evaluation.get("adoption_probability_pct", 0),
                        "decision_date": affected_evaluation.get("decision_date"),
                        "workload_name": affected_evaluation.get("workload_name", "Unknown"),
                    },
                    "risk_level": self._calculate_risk_level(ri, affected_evaluation),
                    "reallocation_options": reallocation_targets,
                    "recommended_action": self._determine_recommended_action(ri, affected_evaluation, reallocation_targets),
                    "potential_savings_at_risk": self._calculate_savings_at_risk(ri, affected_evaluation),
                }
                
                opportunities.append(opportunity)
        
        # Summary
        summary = {
            "total_existing_ris": len(existing_ris),
            "ris_at_risk": len(opportunities),
            "total_monthly_value_at_risk": sum(o["existing_ri"]["monthly_cost"] for o in opportunities),
            "reallocatable_count": sum(1 for o in opportunities if o["reallocation_options"]),
            "opportunities": opportunities,
        }
        
        return summary
    
    def _get_existing_reservations(self) -> List[Dict[str, Any]]:
        """Get existing reservations from Azure or return empty list."""
        if self.azure_client:
            try:
                return self.azure_client.get_existing_reservations()
            except Exception as e:
                logger.warning(f"Could not get existing reservations: {e}")
        return []
    
    def _get_active_evaluations(self) -> List[Dict[str, Any]]:
        """Get active SaaS evaluations."""
        if self.intelligence_service:
            try:
                return self.intelligence_service.get_active_evaluations()
            except Exception as e:
                logger.warning(f"Could not get active evaluations: {e}")
        return []
    
    def _get_new_recommendations(self) -> List[Dict[str, Any]]:
        """Get new RI/SP recommendations."""
        if self.azure_client:
            try:
                return self.azure_client.get_reservation_recommendations()
            except Exception as e:
                logger.warning(f"Could not get recommendations: {e}")
        return []
    
    def _get_workloads(self) -> List[Dict[str, Any]]:
        """Get workloads from intelligence service."""
        if self.intelligence_service:
            try:
                return self.intelligence_service.get_workloads()
            except Exception as e:
                logger.warning(f"Could not get workloads: {e}")
        return []
    
    def _find_affecting_evaluation(
        self, 
        ri: Dict[str, Any], 
        evaluations: List[Dict[str, Any]], 
        workloads: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """
        Check if an RI is associated with a workload that has an active SaaS evaluation.
        """
        # Match RI to workload based on resource patterns, tags, or resource groups
        ri_workload = self._match_ri_to_workload(ri, workloads)
        
        if not ri_workload:
            return None
        
        # Check if this workload has active evaluations with hold_commitments=True
        for evaluation in evaluations:
            if (evaluation.get("workload_id") == ri_workload.get("id") 
                and evaluation.get("hold_commitments", False)
                and evaluation.get("status") in ["evaluating", "poc"]):
                
                # Add workload name for context
                evaluation["workload_name"] = ri_workload.get("name")
                return evaluation
        
        return None
    
    def _match_ri_to_workload(self, ri: Dict[str, Any], workloads: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Match an RI to a workload based on scope, tags, or naming patterns."""
        ri_scope = ri.get("applied_scopes", [])
        ri_name = ri.get("name", "").lower()
        ri_sku = ri.get("sku", "").lower()
        
        for workload in workloads:
            # Check resource group patterns
            patterns = workload.get("resource_group_patterns", [])
            for pattern in patterns:
                pattern_clean = pattern.replace("*", "").lower()
                if pattern_clean in ri_name or any(pattern_clean in scope.lower() for scope in ri_scope):
                    return workload
            
            # Check by workload name in RI name
            workload_name_parts = workload.get("name", "").lower().split()
            if any(part in ri_name for part in workload_name_parts if len(part) > 3):
                return workload
        
        return None
    
    def _find_reallocation_targets(
        self, 
        ri: Dict[str, Any], 
        new_recommendations: List[Dict[str, Any]],
        existing_ris: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Find potential targets for RI reallocation.
        Look for:
        1. New recommendations for same SKU family in different scope
        2. Underutilized resources that could benefit from this RI
        3. Approved recommendations waiting for capacity
        """
        targets = []
        ri_sku_family = self._get_sku_family(ri.get("sku", ""))
        ri_location = ri.get("location", "")
        
        for rec in new_recommendations:
            rec_sku_family = self._get_sku_family(rec.get("sku", ""))
            
            # Same SKU family, compatible location
            if rec_sku_family == ri_sku_family:
                # Check if this recommendation doesn't already have RI coverage
                if not self._has_existing_coverage(rec, existing_ris):
                    targets.append({
                        "type": "new_recommendation",
                        "recommendation_id": rec.get("id"),
                        "resource_name": rec.get("name"),
                        "sku": rec.get("sku"),
                        "location": rec.get("region"),
                        "monthly_cost": rec.get("monthly_cost", 0),
                        "compatibility": "full" if rec.get("region") == ri_location else "partial",
                        "compatibility_note": "Same region" if rec.get("region") == ri_location else "Different region - exchange may have restrictions",
                    })
        
        return targets[:5]  # Return top 5 targets
    
    def _get_sku_family(self, sku: str) -> str:
        """Extract SKU family from full SKU name (e.g., Standard_D16s_v5 -> D_v5)."""
        if not sku:
            return ""
        
        # Common patterns
        sku_upper = sku.upper()
        
        # VM SKUs: Standard_D16s_v5 -> D_v5
        if "STANDARD_" in sku_upper:
            parts = sku_upper.replace("STANDARD_", "").split("_")
            if len(parts) >= 2:
                # Extract letter family and version
                family = ''.join(c for c in parts[0] if c.isalpha())
                version = parts[-1] if parts[-1].startswith("V") else ""
                return f"{family}_{version}" if version else family
        
        # SQL SKUs: GP_Gen5_8 -> GP_Gen5
        if "GP_" in sku_upper or "BC_" in sku_upper:
            parts = sku_upper.split("_")
            return "_".join(parts[:2]) if len(parts) >= 2 else sku_upper
        
        return sku_upper
    
    def _has_existing_coverage(self, recommendation: Dict[str, Any], existing_ris: List[Dict[str, Any]]) -> bool:
        """Check if a recommendation already has RI coverage."""
        rec_sku = recommendation.get("sku", "")
        rec_location = recommendation.get("region", "")
        
        for ri in existing_ris:
            if ri.get("sku") == rec_sku and ri.get("location") == rec_location:
                if ri.get("utilization_percent", 0) < 80:  # Has spare capacity
                    return True
        
        return False
    
    def _calculate_risk_level(self, ri: Dict[str, Any], evaluation: Dict[str, Any]) -> str:
        """Calculate risk level for the RI based on evaluation probability and timeline."""
        adoption_prob = evaluation.get("adoption_probability_pct", 0)
        
        if adoption_prob >= 70:
            return "high"
        elif adoption_prob >= 50:
            return "medium"
        else:
            return "low"
    
    def _determine_recommended_action(
        self, 
        ri: Dict[str, Any], 
        evaluation: Dict[str, Any],
        reallocation_targets: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Determine the recommended action for this at-risk RI."""
        adoption_prob = evaluation.get("adoption_probability_pct", 0)
        remaining_months = self._calculate_remaining_months(ri.get("expiry_date"))
        has_targets = len(reallocation_targets) > 0
        
        if adoption_prob >= 70 and has_targets:
            return {
                "action": "reallocate_now",
                "reason": f"High adoption probability ({adoption_prob}%) - reallocate to {reallocation_targets[0]['resource_name']} before migration",
                "urgency": "high",
            }
        elif adoption_prob >= 70 and not has_targets:
            return {
                "action": "exchange_or_refund",
                "reason": f"High adoption probability ({adoption_prob}%) but no compatible reallocation targets - consider Azure RI exchange or refund",
                "urgency": "high",
            }
        elif adoption_prob >= 50 and remaining_months > 12:
            return {
                "action": "monitor_and_prepare",
                "reason": f"Medium risk ({adoption_prob}%) with {remaining_months} months remaining - prepare reallocation plan pending evaluation outcome",
                "urgency": "medium",
            }
        else:
            return {
                "action": "wait_for_decision",
                "reason": f"Lower risk ({adoption_prob}%) - wait for evaluation decision on {evaluation.get('decision_date')}",
                "urgency": "low",
            }
    
    def _calculate_remaining_months(self, expiry_date_str: Optional[str]) -> int:
        """Calculate remaining months until RI expiry."""
        if not expiry_date_str:
            return 0
        
        try:
            expiry_date = datetime.fromisoformat(expiry_date_str.replace("Z", "+00:00")).date()
            today = date.today()
            delta = expiry_date - today
            return max(0, delta.days // 30)
        except:
            return 0
    
    def _calculate_savings_at_risk(self, ri: Dict[str, Any], evaluation: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate potential savings at risk if workload migrates."""
        monthly_cost = ri.get("monthly_cost", 0)
        remaining_months = self._calculate_remaining_months(ri.get("expiry_date"))
        adoption_prob = evaluation.get("adoption_probability_pct", 0) / 100
        
        total_remaining_value = monthly_cost * remaining_months
        expected_loss = total_remaining_value * adoption_prob
        
        return {
            "monthly_ri_cost": monthly_cost,
            "remaining_months": remaining_months,
            "total_remaining_value": round(total_remaining_value, 2),
            "expected_loss_weighted": round(expected_loss, 2),
            "adoption_probability_used": adoption_prob,
        }
    
    def _get_demo_reallocation_opportunities(self) -> Dict[str, Any]:
        """Demo data for reallocation opportunities."""
        return {
            "total_existing_ris": 12,
            "ris_at_risk": 2,
            "total_monthly_value_at_risk": 13446,
            "reallocatable_count": 1,
            "opportunities": [
                {
                    "existing_ri": {
                        "id": "/providers/Microsoft.Capacity/reservationOrders/order-001/reservations/ri-sql-pfd",
                        "name": "ri-sql-patient-front-door",
                        "sku": "GP_Gen5_8",
                        "location": "eastus",
                        "monthly_cost": 3718,
                        "utilization_percent": 82,
                        "expiry_date": "2027-06-15",
                        "remaining_term_months": 18,
                    },
                    "at_risk_reason": {
                        "evaluation_id": 1,
                        "evaluation_name": "PatientRUs App",
                        "vendor": "PatientRUs Inc.",
                        "adoption_probability": 70,
                        "decision_date": "2026-02-08",
                        "workload_name": "Patient Front Door",
                    },
                    "risk_level": "high",
                    "reallocation_options": [
                        {
                            "type": "new_recommendation",
                            "recommendation_id": "ri-rec-006",
                            "resource_name": "Billing System SQL Database",
                            "sku": "GP_Gen5_8",
                            "location": "eastus",
                            "monthly_cost": 4200,
                            "compatibility": "full",
                            "compatibility_note": "Same SKU and region - direct exchange possible",
                        }
                    ],
                    "recommended_action": {
                        "action": "reallocate_now",
                        "reason": "High adoption probability (70%) - reallocate to Billing System SQL Database before migration",
                        "urgency": "high",
                    },
                    "potential_savings_at_risk": {
                        "monthly_ri_cost": 3718,
                        "remaining_months": 18,
                        "total_remaining_value": 66924,
                        "expected_loss_weighted": 46847,
                        "adoption_probability_used": 0.7,
                    },
                },
                {
                    "existing_ri": {
                        "id": "/providers/Microsoft.Capacity/reservationOrders/order-003/reservations/ri-synapse",
                        "name": "ri-synapse-analytics",
                        "sku": "DW1000c",
                        "location": "eastus2",
                        "monthly_cost": 9728,
                        "utilization_percent": 68,
                        "expiry_date": "2026-04-20",
                        "remaining_term_months": 4,
                    },
                    "at_risk_reason": {
                        "evaluation_id": 2,
                        "evaluation_name": "Snowflake Enterprise",
                        "vendor": "Snowflake Inc.",
                        "adoption_probability": 65,
                        "decision_date": "2026-03-15",
                        "workload_name": "Data Analytics Platform",
                    },
                    "risk_level": "medium",
                    "reallocation_options": [],
                    "recommended_action": {
                        "action": "wait_for_decision",
                        "reason": "Only 4 months remaining on RI - let it expire naturally after evaluation decision",
                        "urgency": "low",
                    },
                    "potential_savings_at_risk": {
                        "monthly_ri_cost": 9728,
                        "remaining_months": 4,
                        "total_remaining_value": 38912,
                        "expected_loss_weighted": 25293,
                        "adoption_probability_used": 0.65,
                    },
                },
            ],
        }


# Singleton
reallocation_service = None

def get_reallocation_service(azure_client=None, intelligence_service=None):
    global reallocation_service
    if reallocation_service is None:
        reallocation_service = ReallocationService(azure_client, intelligence_service)
    return reallocation_service
