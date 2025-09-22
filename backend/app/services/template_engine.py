"""
Agent Template Engine with enterprise extensibility.
Built for MVP simplicity, designed for industry-specific scale.
"""

import json
import yaml
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum

from app.core.interfaces import AgentConfig
import logging

logger = logging.getLogger(__name__)


class IndustryType(Enum):
    """
    Industry classifications for template specialization.
    Current: Basic industries
    Future: 200+ industry-specific templates
    """
    GENERAL = "general"
    CUSTOMER_SERVICE = "customer_service"
    SALES = "sales"
    MARKETING = "marketing"
    FINANCE = "finance"
    HEALTHCARE = "healthcare"
    LEGAL = "legal"
    EDUCATION = "education"
    ECOMMERCE = "ecommerce"
    REAL_ESTATE = "real_estate"
    MANUFACTURING = "manufacturing"
    LOGISTICS = "logistics"
    # Future: Expand to 200+ specific industries


class TemplateCategory(Enum):
    """Template functional categories"""
    CONVERSATIONAL = "conversational"
    ANALYTICAL = "analytical"
    CREATIVE = "creative"
    WORKFLOW = "workflow"
    INTEGRATION = "integration"
    SPECIALIZED = "specialized"


@dataclass
class AgentTemplate:
    """
    Agent template with enterprise metadata.
    
    Current: Basic template structure
    Future: Complex workflow templates, industry regulations
    """
    id: str
    name: str
    description: str
    industry: IndustryType
    category: TemplateCategory
    version: str
    
    # Agent configuration
    config: AgentConfig
    
    # Template metadata
    tags: List[str]
    use_cases: List[str]
    requirements: List[str]
    
    # Enterprise features
    compliance_level: str  # "basic", "enterprise", "regulated"
    security_classification: str  # "public", "internal", "confidential"
    approved_for_production: bool
    
    # Template customization
    customizable_fields: List[str]
    required_integrations: List[str]
    
    # Metadata
    created_at: datetime
    updated_at: datetime
    created_by: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert template to dictionary for API responses"""
        template_dict = asdict(self)
        # Convert enums to strings
        template_dict['industry'] = self.industry.value
        template_dict['category'] = self.category.value
        # Convert datetime to ISO strings
        template_dict['created_at'] = self.created_at.isoformat()
        template_dict['updated_at'] = self.updated_at.isoformat()
        return template_dict


class AgentTemplateEngine:
    """
    Enterprise Agent Template Engine.
    
    Current: File-based templates with basic customization
    Future: Database-backed, industry-specific, AI-generated templates
    """
    
    def __init__(self, templates_dir: str = "templates"):
        self.templates_dir = Path(templates_dir)
        self.templates_dir.mkdir(exist_ok=True)
        
        # In-memory template cache (future: Redis cache)
        self._template_cache: Dict[str, AgentTemplate] = {}
        self._load_default_templates()
    
    async def get_template(self, template_id: str) -> Optional[AgentTemplate]:
        """
        Get template by ID with caching.
        
        Current: Memory cache
        Future: Multi-tier caching, template versioning
        """
        try:
            if template_id in self._template_cache:
                return self._template_cache[template_id]
            
            # Load from file if not in cache
            template_file = self.templates_dir / f"{template_id}.json"
            if template_file.exists():
                template = self._load_template_from_file(template_file)
                self._template_cache[template_id] = template
                return template
            
            logger.warning(f"Template not found: {template_id}")
            return None
            
        except Exception as e:
            logger.error(f"Failed to get template {template_id}: {str(e)}")
            return None
    
    async def list_templates(
        self, 
        industry: Optional[IndustryType] = None,
        category: Optional[TemplateCategory] = None,
        tags: Optional[List[str]] = None
    ) -> List[AgentTemplate]:
        """
        List templates with filtering.
        
        Current: Basic filtering
        Future: Advanced search, ML-powered recommendations
        """
        try:
            # Ensure all templates are loaded
            await self._load_all_templates()
            
            templates = list(self._template_cache.values())
            
            # Apply filters
            if industry:
                templates = [t for t in templates if t.industry == industry]
            
            if category:
                templates = [t for t in templates if t.category == category]
            
            if tags:
                templates = [t for t in templates if any(tag in t.tags for tag in tags)]
            
            # Sort by name (future: relevance scoring)
            templates.sort(key=lambda t: t.name)
            
            return templates
            
        except Exception as e:
            logger.error(f"Failed to list templates: {str(e)}")
            return []
    
    async def create_agent_from_template(
        self, 
        template_id: str, 
        customizations: Optional[Dict[str, Any]] = None
    ) -> Optional[AgentConfig]:
        """
        Create agent configuration from template.
        
        Current: Basic field replacement
        Future: Advanced customization, validation, optimization
        """
        try:
            template = await self.get_template(template_id)
            if not template:
                return None
            
            # Start with template config
            config = AgentConfig(
                name=template.config.name,
                description=template.config.description,
                system_prompt=template.config.system_prompt,
                model=template.config.model,
                temperature=template.config.temperature,
                max_tokens=template.config.max_tokens,
                tools=template.config.tools.copy(),
                metadata=template.config.metadata.copy()
            )
            
            # Apply customizations
            if customizations:
                config = self._apply_customizations(config, template, customizations)
            
            # Add template metadata
            config.metadata["template_id"] = template_id
            config.metadata["template_version"] = template.version
            config.metadata["created_from_template"] = datetime.utcnow().isoformat()
            
            return config
            
        except Exception as e:
            logger.error(f"Failed to create agent from template {template_id}: {str(e)}")
            return None
    
    async def save_template(self, template: AgentTemplate) -> bool:
        """
        Save template to storage.
        
        Current: File-based storage
        Future: Database with versioning, approval workflows
        """
        try:
            template_file = self.templates_dir / f"{template.id}.json"
            
            # Update timestamp
            template.updated_at = datetime.utcnow()
            
            # Save to file
            with open(template_file, 'w') as f:
                json.dump(template.to_dict(), f, indent=2)
            
            # Update cache
            self._template_cache[template.id] = template
            
            logger.info(f"Template saved: {template.id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save template {template.id}: {str(e)}")
            return False
    
    async def delete_template(self, template_id: str) -> bool:
        """
        Delete template (enterprise: soft delete with audit).
        
        Current: Hard delete
        Future: Soft delete, audit trail, dependency checking
        """
        try:
            template_file = self.templates_dir / f"{template_id}.json"
            
            if template_file.exists():
                template_file.unlink()
            
            if template_id in self._template_cache:
                del self._template_cache[template_id]
            
            logger.info(f"Template deleted: {template_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete template {template_id}: {str(e)}")
            return False
    
    async def clone_template(
        self, 
        source_template_id: str, 
        new_template_id: str,
        customizations: Optional[Dict[str, Any]] = None
    ) -> Optional[AgentTemplate]:
        """
        Clone template with modifications.
        
        Current: Basic cloning
        Future: Intelligent template derivation, change tracking
        """
        try:
            source_template = await self.get_template(source_template_id)
            if not source_template:
                return None
            
            # Create new template from source
            new_template = AgentTemplate(
                id=new_template_id,
                name=f"{source_template.name} (Copy)",
                description=f"Cloned from {source_template.name}",
                industry=source_template.industry,
                category=source_template.category,
                version="1.0.0",
                config=AgentConfig(
                    name=source_template.config.name,
                    description=source_template.config.description,
                    system_prompt=source_template.config.system_prompt,
                    model=source_template.config.model,
                    temperature=source_template.config.temperature,
                    max_tokens=source_template.config.max_tokens,
                    tools=source_template.config.tools.copy(),
                    metadata=source_template.config.metadata.copy()
                ),
                tags=source_template.tags.copy(),
                use_cases=source_template.use_cases.copy(),
                requirements=source_template.requirements.copy(),
                compliance_level=source_template.compliance_level,
                security_classification=source_template.security_classification,
                approved_for_production=False,  # Clones need re-approval
                customizable_fields=source_template.customizable_fields.copy(),
                required_integrations=source_template.required_integrations.copy(),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                created_by="system"  # Future: actual user tracking
            )
            
            # Apply customizations
            if customizations:
                new_template = self._apply_template_customizations(new_template, customizations)
            
            # Save the new template
            await self.save_template(new_template)
            
            return new_template
            
        except Exception as e:
            logger.error(f"Failed to clone template {source_template_id}: {str(e)}")
            return None
    
    # Private methods for template management
    
    def _load_default_templates(self):
        """Load default MVP templates"""
        default_templates = [
            self._create_customer_service_template(),
            self._create_sales_assistant_template(),
            self._create_content_creator_template(),
            self._create_data_analyst_template(),
        ]
        
        for template in default_templates:
            self._template_cache[template.id] = template
    
    def _create_customer_service_template(self) -> AgentTemplate:
        """Customer service agent template"""
        return AgentTemplate(
            id="customer_service_basic",
            name="Customer Service Assistant",
            description="AI agent for handling customer inquiries and support",
            industry=IndustryType.CUSTOMER_SERVICE,
            category=TemplateCategory.CONVERSATIONAL,
            version="1.0.0",
            config=AgentConfig(
                name="Customer Service Assistant",
                description="Friendly and helpful customer service agent",
                system_prompt="""You are a professional customer service assistant. Your goal is to help customers with their questions and concerns in a friendly, efficient, and helpful manner.

Key Guidelines:
- Always be polite and professional
- Listen carefully to customer concerns
- Provide clear and actionable solutions
- Escalate complex issues when necessary
- Follow company policies and procedures

Remember to:
- Greet customers warmly
- Ask clarifying questions when needed
- Provide step-by-step instructions
- Confirm customer satisfaction
- Thank customers for their business""",
                model="anthropic/claude-3-haiku",
                temperature=0.7,
                max_tokens=1000,
                tools=[],
                metadata={"purpose": "customer_support", "tone": "friendly_professional"}
            ),
            tags=["customer_service", "support", "conversational"],
            use_cases=[
                "Answer customer questions",
                "Troubleshoot basic issues",
                "Process simple requests",
                "Provide product information"
            ],
            requirements=["Access to knowledge base", "Escalation procedures"],
            compliance_level="enterprise",
            security_classification="internal",
            approved_for_production=True,
            customizable_fields=["system_prompt", "tone", "escalation_rules"],
            required_integrations=["knowledge_base", "ticketing_system"],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            created_by="system"
        )
    
    def _create_sales_assistant_template(self) -> AgentTemplate:
        """Sales assistant agent template"""
        return AgentTemplate(
            id="sales_assistant_basic",
            name="Sales Assistant",
            description="AI agent for sales support and lead qualification",
            industry=IndustryType.SALES,
            category=TemplateCategory.CONVERSATIONAL,
            version="1.0.0",
            config=AgentConfig(
                name="Sales Assistant",
                description="Persuasive and knowledgeable sales support agent",
                system_prompt="""You are a professional sales assistant. Your goal is to help qualify leads, answer product questions, and guide prospects through the sales process.

Key Responsibilities:
- Qualify leads and understand their needs
- Present product benefits clearly
- Handle objections professionally
- Schedule demos and meetings
- Maintain CRM records

Sales Approach:
- Build rapport with prospects
- Ask discovery questions
- Listen actively to understand pain points
- Present solutions that match needs
- Create urgency appropriately
- Always follow ethical sales practices""",
                model="anthropic/claude-3-sonnet",
                temperature=0.8,
                max_tokens=1200,
                tools=[],
                metadata={"purpose": "sales_support", "tone": "persuasive_professional"}
            ),
            tags=["sales", "lead_qualification", "conversational"],
            use_cases=[
                "Qualify inbound leads",
                "Answer product questions",
                "Schedule sales meetings",
                "Follow up with prospects"
            ],
            requirements=["CRM integration", "Product knowledge base"],
            compliance_level="enterprise",
            security_classification="confidential",
            approved_for_production=True,
            customizable_fields=["system_prompt", "sales_methodology", "product_info"],
            required_integrations=["crm", "calendar", "product_catalog"],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            created_by="system"
        )
    
    def _create_content_creator_template(self) -> AgentTemplate:
        """Content creation agent template"""
        return AgentTemplate(
            id="content_creator_basic",
            name="Content Creator",
            description="AI agent for creating marketing and educational content",
            industry=IndustryType.MARKETING,
            category=TemplateCategory.CREATIVE,
            version="1.0.0",
            config=AgentConfig(
                name="Content Creator",
                description="Creative and engaging content generation agent",
                system_prompt="""You are a skilled content creator specializing in marketing and educational content. Your goal is to create engaging, informative, and brand-aligned content across various formats.

Content Types:
- Blog posts and articles
- Social media content
- Email campaigns
- Product descriptions
- Educational materials

Best Practices:
- Understand the target audience
- Maintain consistent brand voice
- Create compelling headlines
- Include clear calls-to-action
- Optimize for SEO when applicable
- Ensure content is accurate and valuable""",
                model="anthropic/claude-3-sonnet",
                temperature=0.9,
                max_tokens=2000,
                tools=[],
                metadata={"purpose": "content_creation", "tone": "creative_engaging"}
            ),
            tags=["content", "marketing", "creative", "writing"],
            use_cases=[
                "Write blog posts",
                "Create social media content",
                "Draft email campaigns",
                "Generate product descriptions"
            ],
            requirements=["Brand guidelines", "Style guide"],
            compliance_level="basic",
            security_classification="public",
            approved_for_production=True,
            customizable_fields=["system_prompt", "brand_voice", "content_types"],
            required_integrations=["cms", "social_media", "brand_assets"],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            created_by="system"
        )
    
    def _create_data_analyst_template(self) -> AgentTemplate:
        """Data analysis agent template"""
        return AgentTemplate(
            id="data_analyst_basic",
            name="Data Analyst",
            description="AI agent for data analysis and insights generation",
            industry=IndustryType.GENERAL,
            category=TemplateCategory.ANALYTICAL,
            version="1.0.0",
            config=AgentConfig(
                name="Data Analyst",
                description="Analytical agent for data insights and reporting",
                system_prompt="""You are a professional data analyst. Your goal is to analyze data, identify patterns, and provide actionable insights for business decision-making.

Core Capabilities:
- Data exploration and profiling
- Statistical analysis
- Trend identification
- Report generation
- Data visualization recommendations

Analysis Approach:
- Start with data understanding
- Ask clarifying questions about objectives
- Apply appropriate analytical methods
- Present findings clearly
- Recommend actions based on insights
- Highlight limitations and assumptions""",
                model="anthropic/claude-3-sonnet",
                temperature=0.3,
                max_tokens=1500,
                tools=[],
                metadata={"purpose": "data_analysis", "tone": "analytical_precise"}
            ),
            tags=["analytics", "data", "insights", "reporting"],
            use_cases=[
                "Analyze business metrics",
                "Create data reports",
                "Identify trends and patterns",
                "Generate insights and recommendations"
            ],
            requirements=["Data access", "Analytics tools"],
            compliance_level="enterprise",
            security_classification="confidential",
            approved_for_production=True,
            customizable_fields=["system_prompt", "analysis_methods", "reporting_format"],
            required_integrations=["database", "analytics_platform", "visualization"],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            created_by="system"
        )
    
    def _apply_customizations(
        self, 
        config: AgentConfig, 
        template: AgentTemplate, 
        customizations: Dict[str, Any]
    ) -> AgentConfig:
        """Apply customizations to agent config"""
        for field, value in customizations.items():
            if field in template.customizable_fields:
                if hasattr(config, field):
                    setattr(config, field, value)
                elif field in config.metadata:
                    config.metadata[field] = value
        
        return config
    
    def _apply_template_customizations(
        self, 
        template: AgentTemplate, 
        customizations: Dict[str, Any]
    ) -> AgentTemplate:
        """Apply customizations to template"""
        for field, value in customizations.items():
            if hasattr(template, field) and field != "id":
                setattr(template, field, value)
        
        return template
    
    def _load_template_from_file(self, template_file: Path) -> AgentTemplate:
        """Load template from JSON file"""
        with open(template_file, 'r') as f:
            data = json.load(f)
        
        # Convert string enums back to enum instances
        data['industry'] = IndustryType(data['industry'])
        data['category'] = TemplateCategory(data['category'])
        
        # Convert ISO strings back to datetime
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        
        # Reconstruct AgentConfig
        config_data = data.pop('config')
        config = AgentConfig(**config_data)
        data['config'] = config
        
        return AgentTemplate(**data)
    
    async def _load_all_templates(self):
        """Load all templates from files"""
        for template_file in self.templates_dir.glob("*.json"):
            template_id = template_file.stem
            if template_id not in self._template_cache:
                try:
                    template = self._load_template_from_file(template_file)
                    self._template_cache[template_id] = template
                except Exception as e:
                    logger.error(f"Failed to load template {template_id}: {str(e)}")


# Enterprise Template Manager
class TemplateManager:
    """
    Enterprise template management with governance.
    Future: Approval workflows, version control, compliance checking
    """
    
    def __init__(self, template_engine: AgentTemplateEngine):
        self.engine = template_engine
    
    async def get_templates_by_industry(self, industry: IndustryType) -> List[AgentTemplate]:
        """Get all templates for specific industry"""
        return await self.engine.list_templates(industry=industry)
    
    async def get_production_ready_templates(self) -> List[AgentTemplate]:
        """Get templates approved for production use"""
        all_templates = await self.engine.list_templates()
        return [t for t in all_templates if t.approved_for_production]
    
    async def validate_template_compliance(self, template: AgentTemplate) -> Dict[str, Any]:
        """
        Validate template compliance.
        Future: Industry-specific compliance rules
        """
        issues = []
        
        # Basic validation
        if not template.name or len(template.name) < 3:
            issues.append("Template name too short")
        
        if not template.description or len(template.description) < 10:
            issues.append("Template description too short")
        
        if not template.config.system_prompt or len(template.config.system_prompt) < 50:
            issues.append("System prompt too short")
        
        # Security validation
        if template.security_classification == "confidential" and not template.required_integrations:
            issues.append("Confidential templates should specify required integrations")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "compliance_level": template.compliance_level,
            "security_classification": template.security_classification
        }