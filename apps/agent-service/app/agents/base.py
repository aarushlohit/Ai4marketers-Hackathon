"""
Base Agent Framework for Multi-Agent AI Platform.

Every agent has:
- Identity
- Goal
- System Prompt
- Memory
- Tools
- Permissions
- Reasoning Engine
- Communication Channel
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import uuid


class AgentType(str, Enum):
    SALES = "sales"
    MARKETING = "marketing"
    CUSTOMER_SUCCESS = "customer_success"
    EXECUTIVE = "executive"
    WORKFLOW = "workflow"
    RECOMMENDATION = "recommendation"
    ANALYTICS = "analytics"
    SECURITY = "security"


class AgentIdentity(BaseModel):
    """Identity definition for an agent."""
    name: str
    agent_type: AgentType
    description: str
    department: str
    avatar: str = "🤖"


class AgentGoal(BaseModel):
    """Strategic goal for an agent."""
    primary_objective: str
    success_criteria: List[str] = Field(default_factory=list)
    kpis: List[str] = Field(default_factory=list)


class AgentMemory(BaseModel):
    """Memory store for an agent."""
    session_memory: Dict[str, Any] = Field(default_factory=dict)
    long_term_memory: Dict[str, Any] = Field(default_factory=dict)
    working_memory: Dict[str, Any] = Field(default_factory=dict)


class AgentTool(BaseModel):
    """Tool definition for an agent."""
    name: str
    description: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    function: Optional[str] = None


class AgentPermissions(BaseModel):
    """RBAC permissions for an agent."""
    can_access_customers: bool = False
    can_access_deals: bool = False
    can_access_meetings: bool = False
    can_access_tickets: bool = False
    can_access_emails: bool = False
    can_access_analytics: bool = False
    can_send_communications: bool = False
    can_modify_records: bool = False
    max_query_depth: int = 2


class AgentConfig(BaseModel):
    """Complete agent configuration."""
    identity: AgentIdentity
    goal: AgentGoal
    system_prompt: str
    tools: List[AgentTool] = Field(default_factory=list)
    permissions: AgentPermissions = Field(default_factory=AgentPermissions)
    context_window: int = 4096
    temperature: float = 0.3
    max_iterations: int = 5


class AgentMessage(BaseModel):
    """Message exchanged between agents."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    from_agent: str
    to_agent: str
    message_type: str = "query"  # query | response | broadcast | delegate
    content: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    session_id: Optional[str] = None
    status: str = "pending"


class Agent(BaseModel):
    """Unified Agent model."""
    id: Optional[str] = None
    tenant_id: Optional[str] = None
    config: AgentConfig
    memory: AgentMemory = Field(default_factory=AgentMemory)
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# ---------------------------------------------------------------------------
# Factory: Pre-built agent configurations
# ---------------------------------------------------------------------------

def create_sales_agent() -> AgentConfig:
    return AgentConfig(
        identity=AgentIdentity(
            name="Sales Agent",
            agent_type=AgentType.SALES,
            description="Expert in pipeline analysis, deal forecasting, and revenue optimization",
            department="Sales",
            avatar="💰",
        ),
        goal=AgentGoal(
            primary_objective="Maximize revenue by identifying upsell opportunities and optimizing deal pipeline",
            success_criteria=[
                "Identify at-risk deals 48 hours in advance",
                "Surface cross-sell opportunities from customer data",
                "Provide accurate quarterly forecasts",
            ],
            kpis=["pipeline_velocity", "win_rate", "deal_size", "sales_cycle_length"],
        ),
        system_prompt="""You are the Sales Agent, a strategic AI assistant for the sales team.
Your role is to analyze the sales pipeline, identify opportunities and risks, and provide actionable recommendations.
You have access to deal data, customer interaction history, and meeting transcripts.
Always provide data-backed insights and prioritize high-impact opportunities.""",
        tools=[
            AgentTool(name="analyze_pipeline", description="Analyze sales pipeline for risks and opportunities", parameters={"filters": {"type": "object"}}),
            AgentTool(name="forecast_revenue", description="Predict revenue for upcoming quarters", parameters={"horizon": {"type": "string"}}),
            AgentTool(name="get_deal_details", description="Retrieve detailed deal information", parameters={"deal_id": {"type": "string"}}),
        ],
        permissions=AgentPermissions(
            can_access_customers=True,
            can_access_deals=True,
            can_access_meetings=True,
        ),
    )


def create_marketing_agent() -> AgentConfig:
    return AgentConfig(
        identity=AgentIdentity(
            name="Marketing Agent",
            agent_type=AgentType.MARKETING,
            description="Expert in campaign analysis, audience segmentation, and marketing ROI",
            department="Marketing",
            avatar="📢",
        ),
        goal=AgentGoal(
            primary_objective="Drive engagement and conversion through intelligent campaign optimization",
            success_criteria=[
                "Identify high-performing channels and campaigns",
                "Segment audiences for personalized outreach",
                "Optimize marketing spend allocation",
            ],
            kpis=["campaign_roi", "conversion_rate", "engagement_score", "cost_per_acquisition"],
        ),
        system_prompt="""You are the Marketing Agent, a strategic AI assistant for the marketing team.
Your role is to analyze campaign performance, identify audience segments, and optimize marketing strategies.
You have access to campaign data, customer segments, and engagement metrics.
Focus on data-driven recommendations and measurable ROI improvements.""",
        tools=[
            AgentTool(name="analyze_campaigns", description="Analyze marketing campaign performance", parameters={"campaign_ids": {"type": "array"}}),
            AgentTool(name="segment_audience", description="Segment customers for targeted campaigns", parameters={"criteria": {"type": "object"}}),
            AgentTool(name="optimize_spend", description="Recommend budget allocation across channels", parameters={"budget": {"type": "number"}}),
        ],
        permissions=AgentPermissions(
            can_access_customers=True,
            can_access_analytics=True,
            can_send_communications=True,
        ),
    )


def create_customer_success_agent() -> AgentConfig:
    return AgentConfig(
        identity=AgentIdentity(
            name="Customer Success Agent",
            agent_type=AgentType.CUSTOMER_SUCCESS,
            description="Expert in customer retention, health monitoring, and churn prevention",
            department="Customer Success",
            avatar="🤝",
        ),
        goal=AgentGoal(
            primary_objective="Maximize customer retention by proactively identifying and mitigating churn risks",
            success_criteria=[
                "Detect churn signals 7+ days before renewal",
                "Automate personalized outreach for at-risk accounts",
                "Maintain customer health score above 85",
            ],
            kpis=["retention_rate", "churn_prediction_accuracy", "health_score", "nps_score"],
        ),
        system_prompt="""You are the Customer Success Agent, a strategic AI assistant for the customer success team.
Your role is to monitor customer health, predict churn risks, and recommend retention strategies.
You have access to customer health scores, support tickets, product usage data, and communication history.
Always prioritize proactive outreach and personalized engagement.""",
        tools=[
            AgentTool(name="assess_health", description="Calculate comprehensive customer health score", parameters={"customer_id": {"type": "string"}}),
            AgentTool(name="predict_churn", description="Predict churn probability for a customer", parameters={"customer_id": {"type": "string"}}),
            AgentTool(name="get_support_history", description="Retrieve customer support ticket history", parameters={"customer_id": {"type": "string"}}),
        ],
        permissions=AgentPermissions(
            can_access_customers=True,
            can_access_tickets=True,
            can_access_emails=True,
            can_send_communications=True,
        ),
    )


def create_executive_agent() -> AgentConfig:
    return AgentConfig(
        identity=AgentIdentity(
            name="Executive Agent",
            agent_type=AgentType.EXECUTIVE,
            description="Strategic advisor synthesizing insights from all agents for executive decision-making",
            department="Executive",
            avatar="🎯",
        ),
        goal=AgentGoal(
            primary_objective="Provide comprehensive strategic insights by coordinating across all AI agents",
            success_criteria=[
                "Synthesize multi-agent insights into executive reports",
                "Identify cross-departmental trends and opportunities",
                "Deliver actionable recommendations with business impact analysis",
            ],
            kpis=["insight_accuracy", "decision_support_quality", "cross_agent_collaboration"],
        ),
        system_prompt="""You are the Executive Agent, the strategic hub of the Miracle Birds AI platform.
Your role is to orchestrate communication between all specialized agents to produce comprehensive strategic insights.
You coordinate with Sales, Marketing, Customer Success, and other agents to gather data,
then synthesize their findings into executive-level reports with clear recommendations.
Every answer must include evidence, confidence levels, and business impact analysis.""",
        tools=[
            AgentTool(name="query_agent", description="Query another agent for specialized insights", parameters={"agent_type": {"type": "string"}, "query": {"type": "string"}}),
            AgentTool(name="generate_report", description="Generate executive report from multi-agent synthesis", parameters={"topic": {"type": "string"}}),
            AgentTool(name="analyze_trends", description="Identify cross-departmental trends", parameters={"timeframe": {"type": "string"}}),
        ],
        permissions=AgentPermissions(
            can_access_customers=True,
            can_access_deals=True,
            can_access_meetings=True,
            can_access_tickets=True,
            can_access_analytics=True,
            max_query_depth=5,
        ),
    )


def create_workflow_agent() -> AgentConfig:
    return AgentConfig(
        identity=AgentIdentity(
            name="Workflow Agent",
            agent_type=AgentType.WORKFLOW,
            description="Automates business processes and triggers intelligent workflows",
            department="Operations",
            avatar="⚡",
        ),
        goal=AgentGoal(
            primary_objective="Automate and optimize business workflows through intelligent orchestration",
            success_criteria=[
                "Automate repetitive tasks based on business rules",
                "Trigger workflows from CRM events and AI predictions",
                "Monitor and optimize workflow performance",
            ],
            kpis=["automation_rate", "workflow_success_rate", "response_time"],
        ),
        system_prompt="""You are the Workflow Agent, responsible for business process automation.
You evaluate conditions, trigger actions, and orchestrate multi-step workflows.
You have access to the workflow engine and can execute actions like sending emails,
updating CRM records, and notifying team members.""",
        tools=[
            AgentTool(name="trigger_workflow", description="Execute a workflow by name", parameters={"workflow_name": {"type": "string"}, "context": {"type": "object"}}),
            AgentTool(name="evaluate_condition", description="Evaluate a business rule condition", parameters={"condition": {"type": "object"}}),
            AgentTool(name="send_notification", description="Send a notification to team members", parameters={"channel": {"type": "string"}, "message": {"type": "string"}}),
        ],
        permissions=AgentPermissions(
            can_access_customers=True,
            can_access_deals=True,
            can_send_communications=True,
            can_modify_records=True,
        ),
    )


def create_recommendation_agent() -> AgentConfig:
    return AgentConfig(
        identity=AgentIdentity(
            name="Recommendation Agent",
            agent_type=AgentType.RECOMMENDATION,
            description="Generates AI-powered business recommendations with confidence scoring",
            department="Strategy",
            avatar="💡",
        ),
        goal=AgentGoal(
            primary_objective="Generate high-confidence business recommendations from multi-source intelligence",
            success_criteria=[
                "Generate recommendations with confidence scores above 80%",
                "Provide clear business reasoning for each recommendation",
                "Track recommendation outcomes and improve accuracy",
            ],
            kpis=["recommendation_accuracy", "confidence_calibration", "impact_realization"],
        ),
        system_prompt="""You are the Recommendation Agent, focused on generating actionable business recommendations.
You analyze data from multiple sources to identify the highest-impact actions.
Each recommendation must include expected revenue impact, confidence level, and clear business reasoning.""",
        tools=[
            AgentTool(name="generate_recommendation", description="Generate recommendations based on analysis", parameters={"context": {"type": "object"}}),
            AgentTool(name="score_opportunity", description="Score a business opportunity by potential impact", parameters={"opportunity": {"type": "object"}}),
        ],
        permissions=AgentPermissions(
            can_access_customers=True,
            can_access_deals=True,
            can_access_analytics=True,
        ),
    )


def create_analytics_agent() -> AgentConfig:
    return AgentConfig(
        identity=AgentIdentity(
            name="Analytics Agent",
            agent_type=AgentType.ANALYTICS,
            description="Deep data analysis, pattern discovery, and metric computation",
            department="Analytics",
            avatar="📊",
        ),
        goal=AgentGoal(
            primary_objective="Uncover actionable insights through deep data analysis and pattern recognition",
            success_criteria=[
                "Identify statistically significant patterns in business data",
                "Provide clear visualizations and explanations of findings",
                "Connect data points across departments for holistic insights",
            ],
            kpis=["pattern_discovery_rate", "analysis_depth", "insight_actionability"],
        ),
        system_prompt="""You are the Analytics Agent, specialized in data analysis and pattern discovery.
You process large datasets, apply statistical methods, and uncover hidden patterns.
Your analyses power the recommendations and insights used by all other agents.""",
        tools=[
            AgentTool(name="analyze_trends", description="Analyze trends across time series data", parameters={"metric": {"type": "string"}, "timeframe": {"type": "string"}}),
            AgentTool(name="find_correlations", description="Find correlations between business metrics", parameters={"metrics": {"type": "array"}}),
            AgentTool(name="compute_forecast", description="Compute statistical forecast for a metric", parameters={"metric": {"type": "string"}, "horizon": {"type": "string"}}),
        ],
        permissions=AgentPermissions(
            can_access_customers=True,
            can_access_deals=True,
            can_access_analytics=True,
            can_access_meetings=True,
            can_access_tickets=True,
            can_access_emails=True,
        ),
    )


def create_security_agent() -> AgentConfig:
    return AgentConfig(
        identity=AgentIdentity(
            name="Security Agent",
            agent_type=AgentType.SECURITY,
            description="Expert in enterprise compliance, threat detection, Zero Trust policies, and GDPR auditing",
            department="Security & Compliance",
            avatar="🛡️",
        ),
        goal=AgentGoal(
            primary_objective="Maintain system security compliance and audit trail records while enforcing Zero Trust policy gates",
            success_criteria=[
                "Scan all incoming and outgoing prompts for prompt injections and leaks",
                "Log all system access and actions with 100% auditable fidelity",
                "Flag high-risk compliance failures and block data transfers without explicit consent",
            ],
            kpis=["pii_leak_prevention_rate", "threat_detection_latency", "compliance_score"],
        ),
        system_prompt="""You are the Security Agent, the primary gatekeeper for the Miracle Birds Platform.
Your role is to monitor prompt compliance, audit system interactions, enforce GDPR consent guidelines, and detect anomalies.
You collaborate with other agents to audit their data accesses and confirm security postures.
Always fail closed when detecting high-risk security threat signals and provide clear explanations.""",
        tools=[
            AgentTool(name="check_compliance", description="Run a checklist for SOC 2 and GDPR compliance audit parameters", parameters={"tenant_id": {"type": "string"}}),
            AgentTool(name="scan_pii", description="Analyze raw text logs and mask sensitive PII fields", parameters={"text": {"type": "string"}}),
            AgentTool(name="detect_threats", description="Scan security logs and raise alerts for security events", parameters={"tenant_id": {"type": "string"}}),
        ],
        permissions=AgentPermissions(
            can_access_customers=True,
            can_access_analytics=True,
            max_query_depth=3,
        ),
    )


# Registry of all agent factories
AGENT_FACTORIES = {
    AgentType.SALES: create_sales_agent,
    AgentType.MARKETING: create_marketing_agent,
    AgentType.CUSTOMER_SUCCESS: create_customer_success_agent,
    AgentType.EXECUTIVE: create_executive_agent,
    AgentType.WORKFLOW: create_workflow_agent,
    AgentType.RECOMMENDATION: create_recommendation_agent,
    AgentType.ANALYTICS: create_analytics_agent,
    AgentType.SECURITY: create_security_agent,
}

