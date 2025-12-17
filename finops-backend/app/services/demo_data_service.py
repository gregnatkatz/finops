"""
Demo Data Service for FinOps AI Command Center

Provides realistic sample data for dashboard demonstration.
Scenario: ContosoHealth - 89-hospital healthcare system with $824.2K/month Azure spend.

File: finops-backend/app/services/demo_data_service.py

Usage:
    from app.services.demo_data_service import demo_data_service
    
    if demo_mode_enabled:
        return demo_data_service.get_cost_summary()
"""

from datetime import datetime, date, timedelta
from typing import Dict, List, Any, Optional
import random
import math


class DemoDataService:
    """
    Provides realistic demo data for the FinOps dashboard.
    
    Demo scenario: ContosoHealth
    - 89-hospital healthcare system
    - $824.2K/month Azure spend
    - $100K/month savings opportunity
    - 3 active SaaS evaluations affecting RI/SP decisions
    """
    
    def __init__(self):
        self.base_date = date.today()
        self._seed_random()
    
    def _seed_random(self):
        """Seed random for consistent demo data within same day."""
        random.seed(self.base_date.toordinal())
    
    # =========================================================================
    # COST DATA
    # =========================================================================
    
    def get_cost_summary(self) -> Dict[str, Any]:
        """
        Monthly cost summary.
        Target: ~$824.2K spend with ~$100K savings opportunity.
        """
        return {
            "monthly_cost": 824200,
            "monthly_cost_formatted": "$824.2K",
            "daily_rate": 27473,
            "daily_rate_formatted": "$27.5K",
            "monthly_savings": 100000,
            "monthly_savings_formatted": "$100K",
            "currency": "USD",
            "period": {
                "start": self.base_date.replace(day=1).isoformat(),
                "end": self.base_date.isoformat()
            },
            "trend": {
                "vs_last_month": 2.3,
                "vs_last_month_direction": "up",
                "vs_last_quarter": -1.8,
                "vs_last_quarter_direction": "down"
            },
            "forecast": {
                "end_of_month": 845000,
                "confidence": 85
            }
        }
    
    def get_daily_costs(self, days: int = 30) -> List[Dict[str, Any]]:
        """
        Daily cost breakdown for trend charts.
        Includes realistic variation patterns.
        """
        costs = []
        base_daily = 27473  # ~$824.2K / 30 days
        
        for i in range(days):
            day = self.base_date - timedelta(days=days - i - 1)
            
            # Base variation
            variation = math.sin(i * 0.3) * 0.05 + random.uniform(-0.03, 0.03)
            daily_cost = base_daily * (1 + variation)
            
            # Weekends are lower (less dev/test activity)
            if day.weekday() >= 5:
                daily_cost *= 0.82
            
            # Month-end batch processing spike
            if day.day >= 28:
                daily_cost *= 1.15
            
            costs.append({
                "date": day.isoformat(),
                "cost": round(daily_cost, 2),
                "compute": round(daily_cost * 0.45, 2),
                "storage": round(daily_cost * 0.18, 2),
                "database": round(daily_cost * 0.25, 2),
                "networking": round(daily_cost * 0.08, 2),
                "other": round(daily_cost * 0.04, 2)
            })
        
        return costs
    
    def get_cost_by_service(self) -> List[Dict[str, Any]]:
        """Cost breakdown by Azure service category."""
        return [
            {
                "service": "Virtual Machines",
                "cost": 370066,
                "cost_formatted": "$370.1K",
                "percent": 44.9,
                "trend": 1.2,
                "trend_direction": "up",
                "icon": "server"
            },
            {
                "service": "SQL Database",
                "cost": 173082,
                "cost_formatted": "$173.1K",
                "percent": 21.0,
                "trend": -2.1,
                "trend_direction": "down",
                "icon": "database"
            },
            {
                "service": "Azure Kubernetes Service",
                "cost": 123630,
                "cost_formatted": "$123.6K",
                "percent": 15.0,
                "trend": 5.3,
                "trend_direction": "up",
                "icon": "kubernetes"
            },
            {
                "service": "Storage Accounts",
                "cost": 74178,
                "cost_formatted": "$74.2K",
                "percent": 9.0,
                "trend": 0.8,
                "trend_direction": "up",
                "icon": "storage"
            },
            {
                "service": "Azure Synapse",
                "cost": 49452,
                "cost_formatted": "$49.5K",
                "percent": 6.0,
                "trend": 12.4,
                "trend_direction": "up",
                "icon": "analytics"
            },
            {
                "service": "Other",
                "cost": 33792,
                "cost_formatted": "$33.8K",
                "percent": 4.1,
                "trend": -0.5,
                "trend_direction": "down",
                "icon": "misc"
            }
        ]
    
    def get_cost_by_resource_group(self) -> List[Dict[str, Any]]:
        """Cost breakdown by resource group."""
        return [
            {"resource_group": "rg-epic-prod", "cost": 145200, "workload": "Epic Integration"},
            {"resource_group": "rg-pacs-prod", "cost": 98500, "workload": "PACS Imaging"},
            {"resource_group": "rg-analytics-prod", "cost": 78400, "workload": "Data Analytics Platform"},
            {"resource_group": "rg-pfd-prod", "cost": 68500, "workload": "Patient Front Door"},
            {"resource_group": "rg-ml-training", "cost": 52600, "workload": "ML Training Pipeline"},
            {"resource_group": "rg-shared-services", "cost": 48200, "workload": "Shared Infrastructure"},
            {"resource_group": "rg-asr-dr", "cost": 38900, "workload": "ASR Disaster Recovery"},
            {"resource_group": "rg-dev-test", "cost": 35150, "workload": "Development/Test"},
            {"resource_group": "rg-network-hub", "cost": 18500, "workload": "Network Hub"},
            {"resource_group": "rg-security", "cost": 14500, "workload": "Security Services"}
        ]
    
    # =========================================================================
    # RI/SP COVERAGE
    # =========================================================================
    
    def get_coverage_summary(self) -> Dict[str, Any]:
        """
        Current RI/SP coverage metrics.
        Shows gap between current (30%) and target (45%) coverage.
        """
        return {
            "ri_coverage_percent": 18,
            "sp_coverage_percent": 12,
            "combined_coverage_percent": 30,
            "target_coverage_percent": 45,
            "coverage_gap_percent": 15,
            "potential_additional_savings": 100000,
            "current_commitment_savings": 58200,
            "total_compute_spend": 493320,
            "covered_compute_spend": 147996,
            "uncovered_compute_spend": 345324,
            "active_reservations": 18,
            "active_savings_plans": 5,
            "expiring_soon": 3,  # Within 90 days
            "utilization": {
                "ri_utilization_percent": 94,
                "sp_utilization_percent": 88
            }
        }
    
    # =========================================================================
    # RI/SP RECOMMENDATIONS - THE KEY DEMO DATA
    # =========================================================================
    
    def get_recommendations(self) -> Dict[str, Any]:
        """
        RI/SP recommendations with AI-driven analysis.
        
        Key demo scenarios:
        1. HOLD recommendations due to SaaS evaluations
        2. APPROVE recommendations for stable workloads
        3. MODIFY recommendations suggesting SP over RI
        """
        return {
            "reservation_recommendations": [
                # HOLD - PatientRUs evaluation affecting SQL
                {
                    "id": "ri-rec-001",
                    "name": "SQL Server Enterprise - East US",
                    "resource_type": "Microsoft.Sql/servers",
                    "resource_type_display": "SQL Database",
                    "sku": "GP_Gen5_8",
                    "sku_display": "General Purpose Gen5, 8 vCores",
                    "region": "eastus",
                    "region_display": "East US",
                    "recommendation_type": "RI",
                    "term": "P3Y",
                    "term_display": "3-Year",
                    "quantity": 1,
                    "monthly_cost_current": 8450,
                    "monthly_cost_with_ri": 3718,
                    "net_savings_monthly": 4732,
                    "net_savings_annual": 56784,
                    "savings_percent": 56,
                    "break_even_months": 8,
                    "upfront_cost": 0,
                    "workload": {
                        "id": 1,
                        "name": "Patient Front Door",
                        "status": "evaluating",
                        "criticality": "mission-critical",
                        "owner": "Jennifer Martinez"
                    },
                    "usage_pattern": {
                        "avg_utilization": 78,
                        "peak_utilization": 95,
                        "stability_score": 82,
                        "days_analyzed": 90
                    },
                    "intelligence": {
                        "action": "hold",
                        "action_display": "On Hold",
                        "reason": "Active SaaS evaluation: PatientRUs App has 70% adoption probability. If adopted, this SQL workload will migrate to SaaS. Decision expected Feb 2026.",
                        "source": "saas_evaluation",
                        "risk_score": 7.2,
                        "risk_level": "high",
                        "confidence": 85,
                        "evaluation": {
                            "id": 1,
                            "name": "PatientRUs App",
                            "vendor": "PatientRUs Inc.",
                            "adoption_probability": 70,
                            "decision_date": "2026-02-08",
                            "poc_success_score": 78
                        },
                        "alternative_recommendation": "Consider 1-Year term if commitment needed before evaluation completes"
                    },
                    "created_at": (self.base_date - timedelta(days=5)).isoformat(),
                    "azure_recommendation_id": "azure-adv-rec-001"
                },
                
                # APPROVE - Stable Epic workload
                {
                    "id": "ri-rec-002",
                    "name": "D16s_v5 Virtual Machines - Central US",
                    "resource_type": "Microsoft.Compute/virtualMachines",
                    "resource_type_display": "Virtual Machines",
                    "sku": "Standard_D16s_v5",
                    "sku_display": "D16s v5 (16 vCPU, 64 GB)",
                    "region": "centralus",
                    "region_display": "Central US",
                    "recommendation_type": "RI",
                    "term": "P3Y",
                    "term_display": "3-Year",
                    "quantity": 8,
                    "monthly_cost_current": 12800,
                    "monthly_cost_with_ri": 5632,
                    "net_savings_monthly": 7168,
                    "net_savings_annual": 86016,
                    "savings_percent": 56,
                    "break_even_months": 7,
                    "upfront_cost": 0,
                    "workload": {
                        "id": 2,
                        "name": "Epic Integration",
                        "status": "active",
                        "criticality": "mission-critical",
                        "owner": "Mike Johnson"
                    },
                    "usage_pattern": {
                        "avg_utilization": 72,
                        "peak_utilization": 89,
                        "stability_score": 98,
                        "days_analyzed": 180
                    },
                    "intelligence": {
                        "action": "approve",
                        "action_display": "Recommended",
                        "reason": "Stable mission-critical workload with 98% stability score over 6 months. No active evaluations. Epic Integration is a long-term strategic platform.",
                        "source": "workload_analysis",
                        "risk_score": 1.8,
                        "risk_level": "low",
                        "confidence": 92,
                        "factors": [
                            "High stability score (98%)",
                            "Mission-critical status",
                            "No competing SaaS evaluations",
                            "6+ months of consistent usage"
                        ]
                    },
                    "created_at": (self.base_date - timedelta(days=3)).isoformat(),
                    "azure_recommendation_id": "azure-adv-rec-002"
                },
                
                # HOLD - Snowflake evaluation affecting Synapse
                {
                    "id": "ri-rec-003",
                    "name": "Azure Synapse DWU - East US 2",
                    "resource_type": "Microsoft.Synapse/workspaces",
                    "resource_type_display": "Azure Synapse Analytics",
                    "sku": "DW1000c",
                    "sku_display": "DW1000c (Dedicated SQL Pool)",
                    "region": "eastus2",
                    "region_display": "East US 2",
                    "recommendation_type": "RI",
                    "term": "P1Y",
                    "term_display": "1-Year",
                    "quantity": 1,
                    "monthly_cost_current": 15200,
                    "monthly_cost_with_ri": 9728,
                    "net_savings_monthly": 5472,
                    "net_savings_annual": 65664,
                    "savings_percent": 36,
                    "break_even_months": 5,
                    "upfront_cost": 0,
                    "workload": {
                        "id": 4,
                        "name": "Data Analytics Platform",
                        "status": "evaluating",
                        "criticality": "high",
                        "owner": "Lisa Park"
                    },
                    "usage_pattern": {
                        "avg_utilization": 65,
                        "peak_utilization": 92,
                        "stability_score": 75,
                        "days_analyzed": 120
                    },
                    "intelligence": {
                        "action": "hold",
                        "action_display": "On Hold",
                        "reason": "Two competing evaluations: Snowflake Enterprise (65% probability) and Databricks Unity Catalog (45% probability). Platform decision expected Q1 2026.",
                        "source": "saas_evaluation",
                        "risk_score": 6.5,
                        "risk_level": "medium",
                        "confidence": 78,
                        "evaluation": {
                            "id": 2,
                            "name": "Snowflake Enterprise",
                            "vendor": "Snowflake Inc.",
                            "adoption_probability": 65,
                            "decision_date": "2026-03-15",
                            "poc_success_score": None
                        },
                        "alternative_recommendation": "Wait for platform decision. Monthly cost acceptable during evaluation period."
                    },
                    "created_at": (self.base_date - timedelta(days=7)).isoformat(),
                    "azure_recommendation_id": "azure-adv-rec-003"
                },
                
                # APPROVE - Stable PACS workload (1-year due to hardware refresh)
                {
                    "id": "ri-rec-004",
                    "name": "E8s_v5 Virtual Machines - West US 2",
                    "resource_type": "Microsoft.Compute/virtualMachines",
                    "resource_type_display": "Virtual Machines",
                    "sku": "Standard_E8s_v5",
                    "sku_display": "E8s v5 (8 vCPU, 64 GB)",
                    "region": "westus2",
                    "region_display": "West US 2",
                    "recommendation_type": "RI",
                    "term": "P1Y",
                    "term_display": "1-Year",
                    "quantity": 4,
                    "monthly_cost_current": 4200,
                    "monthly_cost_with_ri": 2688,
                    "net_savings_monthly": 1512,
                    "net_savings_annual": 18144,
                    "savings_percent": 36,
                    "break_even_months": 4,
                    "upfront_cost": 0,
                    "workload": {
                        "id": 3,
                        "name": "PACS Imaging",
                        "status": "active",
                        "criticality": "mission-critical",
                        "owner": "Dr. Sarah Chen"
                    },
                    "usage_pattern": {
                        "avg_utilization": 68,
                        "peak_utilization": 85,
                        "stability_score": 95,
                        "days_analyzed": 365
                    },
                    "intelligence": {
                        "action": "approve",
                        "action_display": "Recommended",
                        "reason": "Stable imaging workload. 1-year term recommended (vs 3-year) due to planned hardware refresh cycle in Q4 2026 that may change compute requirements.",
                        "source": "workload_analysis",
                        "risk_score": 2.4,
                        "risk_level": "low",
                        "confidence": 88,
                        "factors": [
                            "High stability (95% score)",
                            "Mission-critical medical imaging",
                            "Hardware refresh planned Q4 2026",
                            "1-year term provides flexibility"
                        ]
                    },
                    "created_at": (self.base_date - timedelta(days=2)).isoformat(),
                    "azure_recommendation_id": "azure-adv-rec-004"
                },
                
                # MODIFY - Growing ML workload, suggest SP instead
                {
                    "id": "ri-rec-005",
                    "name": "NC6s_v3 GPU Virtual Machines - South Central US",
                    "resource_type": "Microsoft.Compute/virtualMachines",
                    "resource_type_display": "Virtual Machines (GPU)",
                    "sku": "Standard_NC6s_v3",
                    "sku_display": "NC6s v3 (6 vCPU, V100 GPU)",
                    "region": "southcentralus",
                    "region_display": "South Central US",
                    "recommendation_type": "RI",
                    "term": "P1Y",
                    "term_display": "1-Year",
                    "quantity": 2,
                    "monthly_cost_current": 6800,
                    "monthly_cost_with_ri": 4352,
                    "net_savings_monthly": 2448,
                    "net_savings_annual": 29376,
                    "savings_percent": 36,
                    "break_even_months": 5,
                    "upfront_cost": 0,
                    "workload": {
                        "id": 6,
                        "name": "ML Training Pipeline",
                        "status": "growth",
                        "criticality": "standard",
                        "owner": "Dr. James Lee"
                    },
                    "usage_pattern": {
                        "avg_utilization": 45,
                        "peak_utilization": 98,
                        "stability_score": 55,
                        "days_analyzed": 90
                    },
                    "intelligence": {
                        "action": "modify",
                        "action_display": "Modify Recommended",
                        "reason": "Growing ML workload with variable usage pattern (55% stability). Recommend Savings Plan instead of RI for flexibility across GPU SKUs and regions as AI/ML needs evolve.",
                        "source": "workload_lifecycle",
                        "risk_score": 4.2,
                        "risk_level": "medium",
                        "confidence": 75,
                        "recommended_change": {
                            "from": "1-Year Reserved Instance",
                            "to": "1-Year Compute Savings Plan",
                            "reason": "SP provides flexibility for growing/changing GPU workloads"
                        },
                        "factors": [
                            "Low stability score (55%)",
                            "Workload in growth phase",
                            "GPU SKU may change as needs evolve",
                            "SP covers any compute across regions"
                        ]
                    },
                    "created_at": (self.base_date - timedelta(days=4)).isoformat(),
                    "azure_recommendation_id": "azure-adv-rec-005"
                }
            ],
            
            "savings_plan_recommendations": [
                # Organization-wide Savings Plan
                {
                    "id": "sp-rec-001",
                    "name": "Compute Savings Plan - Shared Scope",
                    "recommendation_type": "SP",
                    "term": "P3Y",
                    "term_display": "3-Year",
                    "scope": "Shared",
                    "scope_display": "Organization-wide",
                    "hourly_commitment": 45.50,
                    "monthly_commitment": 33215,
                    "monthly_cost_current": 48200,
                    "monthly_cost_with_sp": 25096,
                    "net_savings_monthly": 23104,
                    "net_savings_annual": 277248,
                    "savings_percent": 48,
                    "break_even_months": 6,
                    "coverage_percent": 35,
                    "intelligence": {
                        "action": "approve",
                        "action_display": "Recommended",
                        "reason": "Organization-wide compute usage is stable at macro level. Savings Plan provides maximum flexibility across regions, VM families, and services while capturing 48% savings.",
                        "source": "organization_analysis",
                        "risk_score": 2.1,
                        "risk_level": "low",
                        "confidence": 90,
                        "factors": [
                            "Stable organization-wide compute pattern",
                            "Flexibility across 6 Azure regions",
                            "Covers VMs, AKS, App Service, Functions",
                            "Complements existing RIs"
                        ]
                    },
                    "created_at": (self.base_date - timedelta(days=1)).isoformat(),
                    "azure_recommendation_id": "azure-sp-rec-001"
                }
            ],
            
            "summary": {
                "total_recommendations": 6,
                "total_ri_recommendations": 5,
                "total_sp_recommendations": 1,
                "by_action": {
                    "approve": 3,
                    "hold": 2,
                    "modify": 1,
                    "block": 0
                },
                "potential_savings": {
                    "ri_monthly": 21332,
                    "ri_annual": 255984,
                    "sp_monthly": 23104,
                    "sp_annual": 277248,
                    "total_monthly": 44436,
                    "total_annual": 533232
                },
                "actionable_savings": {
                    "approved_monthly": 31784,
                    "approved_annual": 381408,
                    "on_hold_monthly": 10204,
                    "on_hold_annual": 122448
                },
                "coverage_impact": {
                    "current_coverage": 30,
                    "projected_coverage_if_all_approved": 52,
                    "projected_coverage_actionable": 45
                }
            }
        }
    
    def get_smart_recommendations(self) -> Dict[str, Any]:
        """Alias for get_recommendations with AI enrichment."""
        return self.get_recommendations()
    
    # =========================================================================
    # WORKLOADS
    # =========================================================================
    
    def get_workloads(self) -> List[Dict[str, Any]]:
        """
        Business workloads mapped to Azure resources.
        Each workload can have SaaS evaluations that affect RI/SP decisions.
        """
        return [
            {
                "id": 1,
                "name": "Patient Front Door",
                "description": "Patient scheduling, check-in, portal, and call center application",
                "owner_name": "Jennifer Martinez",
                "owner_email": "jmartinez@contosohealth.org",
                "department": "Patient Experience",
                "status": "evaluating",
                "status_display": "Under Evaluation",
                "criticality": "mission-critical",
                "criticality_display": "Mission Critical",
                "resource_count": 12,
                "monthly_cost": 18500,
                "monthly_cost_formatted": "$18.5K",
                "resource_groups": ["rg-pfd-prod", "rg-pfd-staging"],
                "resource_group_patterns": ["rg-pfd-*", "rg-patient-*"],
                "tags": {"CostCenter": "CC-1001", "Environment": "Production"},
                "has_active_evaluation": True,
                "active_evaluation_count": 1,
                "commitment_status": "hold",
                "commitment_status_reason": "PatientRUs App evaluation in progress",
                "created_at": "2024-03-15",
                "updated_at": self.base_date.isoformat()
            },
            {
                "id": 2,
                "name": "Epic Integration",
                "description": "Epic EHR integration layer - HL7 FHIR interfaces, data sync, and API gateway",
                "owner_name": "Mike Johnson",
                "owner_email": "mjohnson@contosohealth.org",
                "department": "Clinical IT",
                "status": "active",
                "status_display": "Active",
                "criticality": "mission-critical",
                "criticality_display": "Mission Critical",
                "resource_count": 24,
                "monthly_cost": 45200,
                "monthly_cost_formatted": "$45.2K",
                "resource_groups": ["rg-epic-prod", "rg-epic-integration"],
                "resource_group_patterns": ["rg-epic-*"],
                "tags": {"CostCenter": "CC-1002", "Environment": "Production", "Compliance": "HIPAA"},
                "has_active_evaluation": False,
                "active_evaluation_count": 0,
                "commitment_status": "eligible",
                "commitment_status_reason": "Stable workload, eligible for 3-year RI",
                "created_at": "2023-06-01",
                "updated_at": self.base_date.isoformat()
            },
            {
                "id": 3,
                "name": "PACS Imaging",
                "description": "Picture Archiving and Communication System for radiology and medical imaging",
                "owner_name": "Dr. Sarah Chen",
                "owner_email": "schen@contosohealth.org",
                "department": "Radiology",
                "status": "active",
                "status_display": "Active",
                "criticality": "mission-critical",
                "criticality_display": "Mission Critical",
                "resource_count": 18,
                "monthly_cost": 32800,
                "monthly_cost_formatted": "$32.8K",
                "resource_groups": ["rg-pacs-prod", "rg-imaging-storage"],
                "resource_group_patterns": ["rg-pacs-*", "rg-imaging-*"],
                "tags": {"CostCenter": "CC-2001", "Environment": "Production", "DataClass": "PHI"},
                "has_active_evaluation": False,
                "active_evaluation_count": 0,
                "commitment_status": "eligible",
                "commitment_status_reason": "Stable workload, 1-year RI recommended (hardware refresh Q4 2026)",
                "created_at": "2023-01-15",
                "updated_at": self.base_date.isoformat()
            },
            {
                "id": 4,
                "name": "Data Analytics Platform",
                "description": "Azure Synapse-based analytics for population health, quality metrics, and financial reporting",
                "owner_name": "Lisa Park",
                "owner_email": "lpark@contosohealth.org",
                "department": "Data & Analytics",
                "status": "evaluating",
                "status_display": "Under Evaluation",
                "criticality": "high",
                "criticality_display": "High",
                "resource_count": 8,
                "monthly_cost": 28400,
                "monthly_cost_formatted": "$28.4K",
                "resource_groups": ["rg-analytics-prod", "rg-synapse-prod"],
                "resource_group_patterns": ["rg-analytics-*", "rg-synapse-*"],
                "tags": {"CostCenter": "CC-3001", "Environment": "Production"},
                "has_active_evaluation": True,
                "active_evaluation_count": 2,
                "commitment_status": "hold",
                "commitment_status_reason": "Snowflake and Databricks evaluations in progress",
                "created_at": "2024-01-10",
                "updated_at": self.base_date.isoformat()
            },
            {
                "id": 5,
                "name": "ASR Disaster Recovery",
                "description": "Azure Site Recovery for business continuity and disaster recovery",
                "owner_name": "Tom Williams",
                "owner_email": "twilliams@contosohealth.org",
                "department": "Infrastructure",
                "status": "active",
                "status_display": "Active",
                "criticality": "high",
                "criticality_display": "High",
                "resource_count": 6,
                "monthly_cost": 8900,
                "monthly_cost_formatted": "$8.9K",
                "resource_groups": ["rg-asr-primary", "rg-dr-secondary"],
                "resource_group_patterns": ["rg-asr-*", "rg-dr-*"],
                "tags": {"CostCenter": "CC-4001", "Environment": "DR"},
                "has_active_evaluation": False,
                "active_evaluation_count": 0,
                "commitment_status": "not_recommended",
                "commitment_status_reason": "DR resources should remain flexible/on-demand",
                "created_at": "2023-09-01",
                "updated_at": self.base_date.isoformat()
            },
            {
                "id": 6,
                "name": "ML Training Pipeline",
                "description": "GPU-based machine learning for diagnostic imaging AI and predictive analytics",
                "owner_name": "Dr. James Lee",
                "owner_email": "jlee@contosohealth.org",
                "department": "AI/ML Research",
                "status": "growth",
                "status_display": "Growth Phase",
                "criticality": "standard",
                "criticality_display": "Standard",
                "resource_count": 5,
                "monthly_cost": 12600,
                "monthly_cost_formatted": "$12.6K",
                "resource_groups": ["rg-ml-training", "rg-gpu-compute"],
                "resource_group_patterns": ["rg-ml-*", "rg-aitraining-*"],
                "tags": {"CostCenter": "CC-5001", "Environment": "Research"},
                "has_active_evaluation": False,
                "active_evaluation_count": 0,
                "commitment_status": "sp_recommended",
                "commitment_status_reason": "Growing workload - Savings Plan recommended over RI for flexibility",
                "created_at": "2024-06-01",
                "updated_at": self.base_date.isoformat()
            }
        ]
    
    # =========================================================================
    # TECHNOLOGY EVALUATIONS
    # =========================================================================
    
    def get_evaluations(self) -> List[Dict[str, Any]]:
        """
        Active SaaS/technology evaluations that affect RI/SP decisions.
        These are the key demo items showing why we HOLD certain recommendations.
        """
        return [
            {
                "id": 1,
                "name": "PatientRUs App",
                "vendor": "PatientRUs Inc.",
                "vendor_website": "https://patientrus.com",
                "evaluation_type": "saas_replacement",
                "evaluation_type_display": "SaaS Replacement",
                "workload_id": 1,
                "workload_name": "Patient Front Door",
                "affected_azure_services": [
                    "SQL Database",
                    "Virtual Machines",
                    "App Service",
                    "Azure Cache for Redis"
                ],
                "estimated_monthly_spend_affected": 18500,
                "estimated_annual_spend_affected": 222000,
                "saas_annual_cost": 185000,
                "potential_annual_savings": 37000,
                "status": "poc",
                "status_display": "POC In Progress",
                "started_date": "2025-09-15",
                "decision_date": "2026-02-08",
                "days_until_decision": (date(2026, 2, 8) - self.base_date).days,
                "adoption_probability_pct": 70,
                "poc_success_score": 78,
                "poc_criteria": [
                    {"name": "User adoption", "score": 85, "weight": 30},
                    {"name": "Feature parity", "score": 72, "weight": 25},
                    {"name": "Integration ease", "score": 80, "weight": 20},
                    {"name": "Performance", "score": 75, "weight": 15},
                    {"name": "Security compliance", "score": 78, "weight": 10}
                ],
                "executive_sponsor": "Sarah Thompson, COO",
                "evaluation_lead": "Jennifer Martinez",
                "hold_commitments": True,
                "commitment_hold_reason": "If adopted, Patient Front Door Azure resources will be decommissioned",
                "hold_expires": "2026-02-15",
                "ri_sp_impact": {
                    "recommendations_on_hold": 1,
                    "monthly_savings_on_hold": 4732,
                    "recommendation_ids": ["ri-rec-001"]
                },
                "notes": "POC showing strong user adoption. Final security review and Epic integration testing pending.",
                "documents": [
                    {"name": "POC Results Summary", "type": "pdf", "date": "2025-11-15"},
                    {"name": "TCO Analysis", "type": "xlsx", "date": "2025-10-01"}
                ],
                "created_at": "2025-09-15",
                "updated_at": self.base_date.isoformat()
            },
            {
                "id": 2,
                "name": "Snowflake Enterprise",
                "vendor": "Snowflake Inc.",
                "vendor_website": "https://snowflake.com",
                "evaluation_type": "platform_migration",
                "evaluation_type_display": "Platform Migration",
                "workload_id": 4,
                "workload_name": "Data Analytics Platform",
                "affected_azure_services": [
                    "Azure Synapse Analytics",
                    "Data Factory",
                    "Storage Accounts",
                    "Power BI Embedded"
                ],
                "estimated_monthly_spend_affected": 28400,
                "estimated_annual_spend_affected": 340800,
                "saas_annual_cost": 295000,
                "potential_annual_savings": 45800,
                "status": "evaluating",
                "status_display": "Technical Evaluation",
                "started_date": "2025-10-01",
                "decision_date": "2026-03-15",
                "days_until_decision": (date(2026, 3, 15) - self.base_date).days,
                "adoption_probability_pct": 65,
                "poc_success_score": None,
                "poc_criteria": None,
                "executive_sponsor": "David Kim, CDO",
                "evaluation_lead": "Lisa Park",
                "hold_commitments": True,
                "commitment_hold_reason": "Major platform decision pending - Synapse vs Snowflake vs Databricks",
                "hold_expires": "2026-03-30",
                "ri_sp_impact": {
                    "recommendations_on_hold": 1,
                    "monthly_savings_on_hold": 5472,
                    "recommendation_ids": ["ri-rec-003"]
                },
                "notes": "Comparing TCO, query performance, and data sharing capabilities. POC scheduled for January.",
                "documents": [
                    {"name": "Vendor Comparison Matrix", "type": "xlsx", "date": "2025-11-01"}
                ],
                "created_at": "2025-10-01",
                "updated_at": self.base_date.isoformat()
            },
            {
                "id": 3,
                "name": "Databricks Unity Catalog",
                "vendor": "Databricks Inc.",
                "vendor_website": "https://databricks.com",
                "evaluation_type": "platform_migration",
                "evaluation_type_display": "Platform Migration",
                "workload_id": 4,
                "workload_name": "Data Analytics Platform",
                "affected_azure_services": [
                    "Azure Synapse Analytics",
                    "HDInsight",
                    "Data Factory"
                ],
                "estimated_monthly_spend_affected": 28400,
                "estimated_annual_spend_affected": 340800,
                "saas_annual_cost": 320000,
                "potential_annual_savings": 20800,
                "status": "evaluating",
                "status_display": "Technical Evaluation",
                "started_date": "2025-11-01",
                "decision_date": "2026-04-10",
                "days_until_decision": (date(2026, 4, 10) - self.base_date).days,
                "adoption_probability_pct": 45,
                "poc_success_score": None,
                "poc_criteria": None,
                "executive_sponsor": "David Kim, CDO",
                "evaluation_lead": "Lisa Park",
                "hold_commitments": True,
                "commitment_hold_reason": "Alternative to Snowflake - evaluating in parallel",
                "hold_expires": "2026-04-20",
                "ri_sp_impact": {
                    "recommendations_on_hold": 1,
                    "monthly_savings_on_hold": 5472,
                    "recommendation_ids": ["ri-rec-003"]
                },
                "notes": "Alternative to Snowflake. Strong ML/AI integration story. Evaluating lakehouse architecture.",
                "documents": [],
                "created_at": "2025-11-01",
                "updated_at": self.base_date.isoformat()
            }
        ]
    
    # =========================================================================
    # ANOMALIES
    # =========================================================================
    
    def get_anomalies(self) -> Dict[str, Any]:
        """Cost anomalies - both active and resolved."""
        return {
            "active": [
                {
                    "id": "anom-001",
                    "detected_at": (self.base_date - timedelta(days=1)).isoformat() + "T14:32:00Z",
                    "resource_name": "aks-ml-cluster",
                    "resource_id": "/subscriptions/xxx/resourceGroups/rg-ml-training/providers/Microsoft.ContainerService/managedClusters/aks-ml-cluster",
                    "resource_group": "rg-ml-training",
                    "service": "Azure Kubernetes Service",
                    "workload": "ML Training Pipeline",
                    "expected_daily_cost": 450,
                    "actual_daily_cost": 890,
                    "excess_cost": 440,
                    "deviation_percent": 98,
                    "status": "investigating",
                    "status_display": "Under Investigation",
                    "severity": "high",
                    "assigned_to": "Dr. James Lee",
                    "probable_cause": "Unexpected GPU node scale-up during overnight training job",
                    "recommended_action": "Review AKS autoscaler settings and training job configuration"
                },
                {
                    "id": "anom-002",
                    "detected_at": (self.base_date - timedelta(hours=6)).isoformat() + "T08:15:00Z",
                    "resource_name": "cosmos-patient-db",
                    "resource_id": "/subscriptions/xxx/resourceGroups/rg-pfd-prod/providers/Microsoft.DocumentDB/databaseAccounts/cosmos-patient-db",
                    "resource_group": "rg-pfd-prod",
                    "service": "Cosmos DB",
                    "workload": "Patient Front Door",
                    "expected_daily_cost": 280,
                    "actual_daily_cost": 425,
                    "excess_cost": 145,
                    "deviation_percent": 52,
                    "status": "investigating",
                    "status_display": "Under Investigation",
                    "severity": "medium",
                    "assigned_to": "Jennifer Martinez",
                    "probable_cause": "Increased RU consumption from new patient portal feature",
                    "recommended_action": "Review query patterns and consider indexing optimization"
                }
            ],
            "resolved_this_month": [
                {
                    "id": "anom-003",
                    "detected_at": (self.base_date - timedelta(days=12)).isoformat(),
                    "resolved_at": (self.base_date - timedelta(days=10)).isoformat(),
                    "resource_name": "synapse-workspace-prod",
                    "service": "Azure Synapse Analytics",
                    "workload": "Data Analytics Platform",
                    "cause": "Analyst ran unoptimized query scanning full dataset",
                    "excess_cost": 2400,
                    "resolution": "Query terminated, query governance policies implemented",
                    "resolved_by": "Lisa Park",
                    "time_to_resolve_hours": 48
                },
                {
                    "id": "anom-004",
                    "detected_at": (self.base_date - timedelta(days=8)).isoformat(),
                    "resolved_at": (self.base_date - timedelta(days=7)).isoformat(),
                    "resource_name": "storage-backup-archive",
                    "service": "Storage Accounts",
                    "workload": "Shared Infrastructure",
                    "cause": "Backup script accidentally migrated 2TB to hot tier",
                    "excess_cost": 850,
                    "resolution": "Data moved back to cool tier, script corrected",
                    "resolved_by": "Tom Williams",
                    "time_to_resolve_hours": 18
                },
                {
                    "id": "anom-005",
                    "detected_at": (self.base_date - timedelta(days=15)).isoformat(),
                    "resolved_at": (self.base_date - timedelta(days=14)).isoformat(),
                    "resource_name": "vm-dev-test-large",
                    "service": "Virtual Machines",
                    "workload": "Development/Test",
                    "cause": "Developer left D64s VM running over weekend",
                    "excess_cost": 1200,
                    "resolution": "VM deallocated, auto-shutdown policy enabled",
                    "resolved_by": "Auto-resolved via policy",
                    "time_to_resolve_hours": 12
                },
                {
                    "id": "anom-006",
                    "detected_at": (self.base_date - timedelta(days=18)).isoformat(),
                    "resolved_at": (self.base_date - timedelta(days=17)).isoformat(),
                    "resource_name": "aks-epic-cluster",
                    "service": "Azure Kubernetes Service",
                    "workload": "Epic Integration",
                    "cause": "Memory leak caused pod restart loop with excessive logging",
                    "excess_cost": 680,
                    "resolution": "Patched application, reduced log retention",
                    "resolved_by": "Mike Johnson",
                    "time_to_resolve_hours": 8
                }
            ],
            "timeline": self._generate_anomaly_timeline(),
            "summary": {
                "total_detected_this_month": 12,
                "resolved": 9,
                "investigating": 2,
                "false_positive": 1,
                "mttr_hours": 22,  # Mean time to resolve
                "total_excess_cost_detected": 18500,
                "total_cost_recovered": 12300,
                "recovery_rate_percent": 66.5
            }
        }
    
    def _generate_anomaly_timeline(self) -> List[Dict[str, Any]]:
        """Generate anomaly resolution timeline for chart."""
        timeline = []
        for i in range(30):
            day = self.base_date - timedelta(days=29 - i)
            detected = random.randint(0, 2) if i < 25 else random.randint(0, 1)
            resolved = min(detected + random.randint(0, 1), detected + 1) if i > 2 else 0
            
            timeline.append({
                "date": day.isoformat(),
                "detected": detected,
                "resolved": resolved,
                "active": max(0, detected - resolved)
            })
        
        return timeline
    
    # =========================================================================
    # BUDGETS
    # =========================================================================
    
    def get_budgets(self) -> List[Dict[str, Any]]:
        """Azure budgets and their status."""
        return [
            {
                "id": "budget-001",
                "name": "Clinical Systems",
                "scope": "Resource Group: rg-epic-*, rg-pacs-*",
                "amount": 250000,
                "spent": 198500,
                "remaining": 51500,
                "percent_used": 79.4,
                "forecast_end_of_month": 242000,
                "forecast_percent": 96.8,
                "status": "on_track",
                "status_display": "On Track",
                "status_color": "green",
                "alert_thresholds": [70, 90, 100],
                "alerts_triggered": [70],
                "owner": "Mike Johnson",
                "department": "Clinical IT",
                "period": "Monthly",
                "reset_date": (self.base_date.replace(day=1) + timedelta(days=32)).replace(day=1).isoformat()
            },
            {
                "id": "budget-002",
                "name": "Data Platform",
                "scope": "Resource Group: rg-analytics-*, rg-synapse-*",
                "amount": 150000,
                "spent": 138200,
                "remaining": 11800,
                "percent_used": 92.1,
                "forecast_end_of_month": 168000,
                "forecast_percent": 112.0,
                "status": "at_risk",
                "status_display": "At Risk - Forecast Exceeds Budget",
                "status_color": "red",
                "alert_thresholds": [70, 90, 100],
                "alerts_triggered": [70, 90],
                "owner": "Lisa Park",
                "department": "Data & Analytics",
                "period": "Monthly",
                "reset_date": (self.base_date.replace(day=1) + timedelta(days=32)).replace(day=1).isoformat()
            },
            {
                "id": "budget-003",
                "name": "Development & Test",
                "scope": "Resource Group: rg-dev-*, rg-test-*",
                "amount": 80000,
                "spent": 52100,
                "remaining": 27900,
                "percent_used": 65.1,
                "forecast_end_of_month": 71000,
                "forecast_percent": 88.8,
                "status": "on_track",
                "status_display": "On Track",
                "status_color": "green",
                "alert_thresholds": [70, 90, 100],
                "alerts_triggered": [],
                "owner": "Platform Team",
                "department": "Engineering",
                "period": "Monthly",
                "reset_date": (self.base_date.replace(day=1) + timedelta(days=32)).replace(day=1).isoformat()
            },
            {
                "id": "budget-004",
                "name": "AI/ML Research",
                "scope": "Resource Group: rg-ml-*, rg-gpu-*",
                "amount": 60000,
                "spent": 48900,
                "remaining": 11100,
                "percent_used": 81.5,
                "forecast_end_of_month": 62500,
                "forecast_percent": 104.2,
                "status": "at_risk",
                "status_display": "At Risk - Forecast Exceeds Budget",
                "status_color": "yellow",
                "alert_thresholds": [70, 90, 100],
                "alerts_triggered": [70],
                "owner": "Dr. James Lee",
                "department": "AI/ML Research",
                "period": "Monthly",
                "reset_date": (self.base_date.replace(day=1) + timedelta(days=32)).replace(day=1).isoformat()
            },
            {
                "id": "budget-005",
                "name": "Infrastructure",
                "scope": "Resource Group: rg-network-*, rg-security-*, rg-shared-*",
                "amount": 100000,
                "spent": 71200,
                "remaining": 28800,
                "percent_used": 71.2,
                "forecast_end_of_month": 89000,
                "forecast_percent": 89.0,
                "status": "on_track",
                "status_display": "On Track",
                "status_color": "green",
                "alert_thresholds": [70, 90, 100],
                "alerts_triggered": [70],
                "owner": "Tom Williams",
                "department": "Infrastructure",
                "period": "Monthly",
                "reset_date": (self.base_date.replace(day=1) + timedelta(days=32)).replace(day=1).isoformat()
            }
        ]
    
    # =========================================================================
    # AI AGENTS
    # =========================================================================
    
    def get_agent_performance(self) -> List[Dict[str, Any]]:
        """AI agent activity, accuracy, and savings generated."""
        return [
            {
                "id": "agent-001",
                "name": "Cost Sentinel",
                "description": "Monitors for cost anomalies and unexpected spending spikes",
                "icon": "shield",
                "status": "active",
                "actions_today": 3,
                "actions_this_week": 18,
                "actions_this_month": 47,
                "savings_today": 440,
                "savings_this_week": 3200,
                "savings_this_month": 12300,
                "accuracy": 97.3,
                "false_positive_rate": 2.7,
                "avg_response_time_minutes": 4,
                "last_action": (self.base_date - timedelta(hours=2)).isoformat() + "T" + "14:32:00Z",
                "last_action_description": "Detected GPU cluster cost spike in ML workload"
            },
            {
                "id": "agent-002",
                "name": "Commitment Advisor",
                "description": "Analyzes RI/SP opportunities and provides purchase recommendations",
                "icon": "trending-up",
                "status": "active",
                "actions_today": 1,
                "actions_this_week": 5,
                "actions_this_month": 12,
                "savings_today": 0,
                "savings_this_week": 1800,
                "savings_this_month": 4200,
                "accuracy": 94.8,
                "false_positive_rate": 5.2,
                "avg_response_time_minutes": 15,
                "last_action": (self.base_date - timedelta(hours=8)).isoformat() + "T" + "08:15:00Z",
                "last_action_description": "Updated recommendation for Epic VMs based on new usage data"
            },
            {
                "id": "agent-003",
                "name": "Orphan Hunter",
                "description": "Identifies unused and orphaned resources for cleanup",
                "icon": "search",
                "status": "active",
                "actions_today": 0,
                "actions_this_week": 3,
                "actions_this_month": 8,
                "savings_today": 0,
                "savings_this_week": 450,
                "savings_this_month": 2100,
                "accuracy": 99.1,
                "false_positive_rate": 0.9,
                "avg_response_time_minutes": 60,
                "last_action": (self.base_date - timedelta(days=2)).isoformat() + "T" + "11:00:00Z",
                "last_action_description": "Found 3 unattached managed disks in rg-dev-test"
            },
            {
                "id": "agent-004",
                "name": "Right-Size Engine",
                "description": "Recommends VM right-sizing based on utilization patterns",
                "icon": "sliders",
                "status": "active",
                "actions_today": 2,
                "actions_this_week": 8,
                "actions_this_month": 15,
                "savings_today": 200,
                "savings_this_week": 600,
                "savings_this_month": 1200,
                "accuracy": 96.5,
                "false_positive_rate": 3.5,
                "avg_response_time_minutes": 30,
                "last_action": (self.base_date - timedelta(hours=4)).isoformat() + "T" + "12:45:00Z",
                "last_action_description": "Recommended D4s_v5 -> D2s_v5 for epic-app-03"
            },
            {
                "id": "agent-005",
                "name": "Spend Prophet",
                "description": "Forecasts future costs and alerts on budget trajectory",
                "icon": "chart-line",
                "status": "active",
                "actions_today": 1,
                "actions_this_week": 6,
                "actions_this_month": 22,
                "savings_today": 0,
                "savings_this_week": 0,
                "savings_this_month": 350,
                "accuracy": 91.2,
                "false_positive_rate": 8.8,
                "avg_response_time_minutes": 5,
                "last_action": (self.base_date).isoformat() + "T" + "06:00:00Z",
                "last_action_description": "Alerted: Data Platform budget projected to exceed by 12%"
            }
        ]
    
    def get_agent_summary(self) -> Dict[str, Any]:
        """Summary of all agent activity."""
        agents = self.get_agent_performance()
        return {
            "total_agents": len(agents),
            "active_agents": sum(1 for a in agents if a["status"] == "active"),
            "total_actions_today": sum(a["actions_today"] for a in agents),
            "total_actions_this_month": sum(a["actions_this_month"] for a in agents),
            "total_savings_today": sum(a["savings_today"] for a in agents),
            "total_savings_this_month": sum(a["savings_this_month"] for a in agents),
            "average_accuracy": round(sum(a["accuracy"] for a in agents) / len(agents), 1)
        }
    
    # =========================================================================
    # RI/SP ACTION TRACKING
    # =========================================================================
    
    def get_risp_actions(self) -> Dict[str, Any]:
        """Track admin decisions on RI/SP recommendations."""
        return {
            "summary": {
                "approved": 8,
                "on_hold": 4,
                "blocked": 1,
                "pending_review": 3,
                "total": 16
            },
            "savings": {
                "approved_monthly": 18200,
                "approved_annual": 218400,
                "on_hold_monthly": 10204,
                "on_hold_annual": 122448,
                "blocked_monthly": 1800,
                "blocked_annual": 21600
            },
            "approval_rate": 61.5,
            "recent_actions": [
                {
                    "id": "action-001",
                    "recommendation_id": "ri-rec-002",
                    "recommendation_name": "D16s_v5 VMs - Central US",
                    "action": "approved",
                    "action_display": "Approved",
                    "action_by": "admin@contosohealth.org",
                    "action_by_name": "System Administrator",
                    "action_at": (self.base_date - timedelta(days=2)).isoformat() + "T10:30:00Z",
                    "savings_monthly": 7168,
                    "notes": "Approved per Epic Integration team request"
                },
                {
                    "id": "action-002",
                    "recommendation_id": "ri-rec-001",
                    "recommendation_name": "SQL Server Enterprise - East US",
                    "action": "hold",
                    "action_display": "On Hold",
                    "action_by": "admin@contosohealth.org",
                    "action_by_name": "System Administrator",
                    "action_at": (self.base_date - timedelta(days=3)).isoformat() + "T14:15:00Z",
                    "savings_monthly": 4732,
                    "notes": "Holding pending PatientRUs evaluation decision"
                },
                {
                    "id": "action-003",
                    "recommendation_id": "ri-rec-004",
                    "recommendation_name": "E8s_v5 VMs - West US 2",
                    "action": "approved",
                    "action_display": "Approved",
                    "action_by": "admin@contosohealth.org",
                    "action_by_name": "System Administrator",
                    "action_at": (self.base_date - timedelta(days=5)).isoformat() + "T09:00:00Z",
                    "savings_monthly": 1512,
                    "notes": "1-year term selected due to hardware refresh"
                },
                {
                    "id": "action-004",
                    "recommendation_id": "ri-rec-003",
                    "recommendation_name": "Azure Synapse DWU - East US 2",
                    "action": "hold",
                    "action_display": "On Hold",
                    "action_by": "admin@contosohealth.org",
                    "action_by_name": "System Administrator",
                    "action_at": (self.base_date - timedelta(days=7)).isoformat() + "T11:45:00Z",
                    "savings_monthly": 5472,
                    "notes": "Holding for Snowflake/Databricks platform decision"
                }
            ],
            "by_workload": [
                {"workload": "Epic Integration", "approved": 3, "hold": 0, "blocked": 0},
                {"workload": "PACS Imaging", "approved": 2, "hold": 0, "blocked": 0},
                {"workload": "Patient Front Door", "approved": 0, "hold": 2, "blocked": 0},
                {"workload": "Data Analytics Platform", "approved": 0, "hold": 2, "blocked": 0},
                {"workload": "ML Training Pipeline", "approved": 0, "hold": 0, "blocked": 1},
                {"workload": "Other", "approved": 3, "hold": 0, "blocked": 0}
            ]
        }


# =========================================================================
# SINGLETON INSTANCE
# =========================================================================

demo_data_service = DemoDataService()


# =========================================================================
# CONVENIENCE FUNCTIONS
# =========================================================================

def get_all_demo_data() -> Dict[str, Any]:
    """Get all demo data in a single call (useful for testing)."""
    return {
        "cost_summary": demo_data_service.get_cost_summary(),
        "daily_costs": demo_data_service.get_daily_costs(),
        "cost_by_service": demo_data_service.get_cost_by_service(),
        "coverage": demo_data_service.get_coverage_summary(),
        "recommendations": demo_data_service.get_recommendations(),
        "workloads": demo_data_service.get_workloads(),
        "evaluations": demo_data_service.get_evaluations(),
        "anomalies": demo_data_service.get_anomalies(),
        "budgets": demo_data_service.get_budgets(),
        "agents": demo_data_service.get_agent_performance(),
        "agent_summary": demo_data_service.get_agent_summary(),
        "risp_actions": demo_data_service.get_risp_actions()
    }
