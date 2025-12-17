"""
SQLAlchemy models for historical cost tracking.
"""
from datetime import datetime, date
from sqlalchemy import Column, Integer, Float, String, Date, DateTime, Index, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class DailyCostHistory(Base):
    """Historical daily cost records."""
    __tablename__ = "daily_cost_history"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False, index=True)
    total_cost = Column(Float, nullable=False)
    currency = Column(String(10), default="USD")
    
    # Breakdown by top categories
    compute_cost = Column(Float, default=0)
    storage_cost = Column(Float, default=0)
    network_cost = Column(Float, default=0)
    database_cost = Column(Float, default=0)
    ai_ml_cost = Column(Float, default=0)
    other_cost = Column(Float, default=0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        UniqueConstraint('date', name='uq_daily_cost_date'),
    )


class ServiceCostHistory(Base):
    """Historical cost by service."""
    __tablename__ = "service_cost_history"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False, index=True)
    service_name = Column(String(255), nullable=False)
    cost = Column(Float, nullable=False)
    currency = Column(String(10), default="USD")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        UniqueConstraint('date', 'service_name', name='uq_service_cost_date_service'),
        Index('ix_service_cost_date_service', 'date', 'service_name'),
    )


class AnomalyRecord(Base):
    """Detected cost anomalies."""
    __tablename__ = "anomaly_records"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    detected_at = Column(DateTime, default=datetime.utcnow, index=True)
    anomaly_date = Column(Date, nullable=False)
    
    # What triggered it
    metric = Column(String(100), nullable=False)  # e.g., "daily_total", "compute", "gpu"
    actual_value = Column(Float, nullable=False)
    baseline_value = Column(Float, nullable=False)
    threshold_pct = Column(Float, nullable=False)  # e.g., 25.0 for 25%
    
    # Calculated fields
    variance_pct = Column(Float, nullable=False)
    variance_amount = Column(Float, nullable=False)
    
    # Status tracking
    status = Column(String(50), default="open")  # open, investigating, resolved, dismissed
    severity = Column(String(20), default="medium")  # low, medium, high, critical
    
    # Resolution
    root_cause = Column(String(500), nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    resolved_by = Column(String(100), nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class BudgetStatus(Base):
    """Azure Budget status cache."""
    __tablename__ = "budget_status"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    budget_name = Column(String(255), nullable=False, unique=True)
    budget_amount = Column(Float, nullable=False)
    time_grain = Column(String(50), default="Monthly")  # Monthly, Quarterly, Annually
    
    # Current period status
    current_spend = Column(Float, default=0)
    forecasted_spend = Column(Float, default=0)
    spend_pct = Column(Float, default=0)
    
    # Thresholds (from Azure Budget config)
    threshold_60_status = Column(String(20), default="ok")  # ok, triggered
    threshold_80_status = Column(String(20), default="ok")
    threshold_90_status = Column(String(20), default="ok")
    threshold_100_status = Column(String(20), default="ok")
    
    # Metadata
    category = Column(String(100), nullable=True)  # e.g., "Compute", "Storage"
    resource_group = Column(String(255), nullable=True)
    last_synced = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class RecommendationCache(Base):
    """Cached RI/SP recommendations."""
    __tablename__ = "recommendation_cache"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    recommendation_id = Column(String(500), nullable=False, unique=True)
    recommendation_type = Column(String(50), nullable=False)  # RI, SP, Advisor
    
    # Core data (stored as JSON string for flexibility)
    data_json = Column(String(5000), nullable=False)
    
    # Summary fields for quick queries
    potential_savings = Column(Float, default=0)
    currency = Column(String(10), default="USD")
    impact = Column(String(20), nullable=True)  # High, Medium, Low
    
    # Metadata
    last_synced = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)


class RICoverage(Base):
    """RI coverage tracking."""
    __tablename__ = "ri_coverage"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False, unique=True)
    
    # Coverage metrics
    total_on_demand_cost = Column(Float, default=0)
    total_reserved_cost = Column(Float, default=0)
    coverage_pct = Column(Float, default=0)
    
    # By VM family (top 5)
    coverage_by_family_json = Column(String(2000), nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)


class StatsSnapshot(Base):
    """Cached stats snapshot for fast retrieval."""
    __tablename__ = "stats_snapshot"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    snapshot_key = Column(String(50), nullable=False, unique=True, default="current")
    
    # Core stats
    monthly_spend = Column(Float, default=0)
    ai_savings = Column(Float, default=0)
    anomalies_resolved = Column(Integer, default=0)
    anomalies_total = Column(Integer, default=0)
    budgets_on_track = Column(Integer, default=0)
    budgets_total = Column(Integer, default=0)
    ri_coverage_pct = Column(Float, default=0)
    ri_target_pct = Column(Float, default=25)
    agents_active = Column(Integer, default=0)
    
    # Full JSON payload for additional data
    full_payload_json = Column(String(10000), nullable=True)
    
    # Metadata
    last_updated = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)


class AnomalySnapshot(Base):
    """Cached anomaly data snapshot."""
    __tablename__ = "anomaly_snapshot"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    snapshot_key = Column(String(50), nullable=False, unique=True, default="current")
    
    # JSON payload of anomaly data
    payload_json = Column(String(50000), nullable=True)
    
    # Metadata
    last_updated = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)


class RISPAction(Base):
    """RI/SP recommendation actions (approve, hold, block) with persistence."""
    __tablename__ = "risp_actions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Recommendation identification
    resource = Column(String(500), nullable=False)
    recommendation_type = Column(String(100), nullable=True)  # e.g., "3-YEAR RI", "1-YEAR SP"
    
    # Action details
    action = Column(String(50), nullable=False)  # approved, held, blocked
    action_by = Column(String(255), nullable=True, default="admin@contosohealth.org")
    action_by_name = Column(String(255), nullable=True, default="System Administrator")
    notes = Column(String(1000), nullable=True)
    
    # Financial data
    savings_monthly = Column(Float, default=0)
    monthly_cost = Column(Float, default=0)
    
    # AI Analysis (populated when approving)
    ai_analysis = Column(String(5000), nullable=True)
    ai_confidence = Column(Float, nullable=True)
    ai_risk_assessment = Column(String(500), nullable=True)
    
    # Azure Portal link
    azure_portal_link = Column(String(1000), nullable=True)
    
    # Metadata
    action_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index('ix_risp_action_resource', 'resource'),
        Index('ix_risp_action_action', 'action'),
    )
