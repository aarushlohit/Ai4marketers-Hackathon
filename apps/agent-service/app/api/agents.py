"""Agent Service — Agent Management API."""

import json
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from datetime import datetime, timezone
import uuid
from sqlalchemy import select, update, insert, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db, AsyncSessionLocal
from app.agents.base import (
    Agent, AgentConfig, AgentType, AgentIdentity, AgentGoal,
    AgentPermissions, AgentTool, AgentMemory, AGENT_FACTORIES,
)

router = APIRouter()

class AgentCreateRequest(BaseModel):
    name: str
    agent_type: AgentType
    tenant_id: str = "00000000-0000-0000-0000-000000000001"

class AgentResponse(BaseModel):
    id: str
    name: str
    agent_type: str
    identity: dict
    goal: dict
    tools: List[dict]
    permissions: dict
    is_active: bool
    created_at: str

# In-memory backup agent store
_agents_store: dict = {}

def _generate_id() -> str:
    return str(uuid.uuid4())

@router.post("", response_model=AgentResponse)
async def create_agent(request: AgentCreateRequest, db: AsyncSession = Depends(get_db)):
    """Create a new AI agent from the factory and persist to the database."""
    if request.agent_type not in AGENT_FACTORIES:
        raise HTTPException(status_code=400, detail=f"Unknown agent type: {request.agent_type}")

    config = AGENT_FACTORIES[request.agent_type]()
    if request.name:
        config.identity.name = request.name

    agent_id = _generate_id()
    agent = Agent(
        id=agent_id,
        tenant_id=request.tenant_id,
        config=config,
    )
    _agents_store[agent_id] = agent

    try:
        # Enforce PostgreSQL tenant setting context
        await db.execute(text(f"SELECT set_config('app.tenant_id', '{request.tenant_id}', true)"))
        
        await db.execute(
            text("""
            INSERT INTO ai.agents (id, tenant_id, name, agent_type, identity, goal, system_prompt, tools, permissions, config, is_active)
            VALUES (:id, :tenant_id, :name, :agent_type, :identity, :goal, :system_prompt, :tools, :permissions, :config, :is_active)
            """),
            {
                "id": uuid.UUID(agent_id),
                "tenant_id": uuid.UUID(request.tenant_id),
                "name": agent.config.identity.name,
                "agent_type": agent.config.identity.agent_type.value,
                "identity": json.dumps(agent.config.identity.model_dump()),
                "goal": json.dumps(agent.config.goal.model_dump()),
                "system_prompt": agent.config.system_prompt,
                "tools": json.dumps([t.model_dump() for t in agent.config.tools]),
                "permissions": json.dumps(agent.config.permissions.model_dump()),
                "config": json.dumps({
                    "context_window": agent.config.context_window,
                    "temperature": agent.config.temperature,
                    "max_iterations": agent.config.max_iterations
                }),
                "is_active": True
            }
        )
        await db.commit()
    except Exception as e:
        print("Database insert failed, using memory fallback:", e)

    return AgentResponse(
        id=agent.id,
        name=agent.config.identity.name,
        agent_type=agent.config.identity.agent_type.value,
        identity=agent.config.identity.model_dump(),
        goal=agent.config.goal.model_dump(),
        tools=[t.model_dump() for t in agent.config.tools],
        permissions=agent.config.permissions.model_dump(),
        is_active=agent.is_active,
        created_at=agent.created_at.isoformat(),
    )

@router.get("", response_model=List[AgentResponse])
async def list_agents(agent_type: Optional[str] = None, active_only: bool = True, tenant_id: str = "00000000-0000-0000-0000-000000000001", db: AsyncSession = Depends(get_db)):
    """List all agents from the database, filtered by type."""
    try:
        # Enforce PostgreSQL tenant setting context
        await db.execute(text(f"SELECT set_config('app.tenant_id', '{tenant_id}', true)"))
        
        query = "SELECT id, name, agent_type, identity, goal, tools, permissions, is_active, created_at FROM ai.agents WHERE tenant_id = :tenant_id"
        params = {"tenant_id": uuid.UUID(tenant_id)}
        if active_only:
            query += " AND is_active = true"
        if agent_type:
            query += " AND agent_type = :agent_type"
            params["agent_type"] = agent_type
            
        res = await db.execute(text(query), params)
        db_agents = res.fetchall()
        
        if db_agents:
            agents = []
            for row in db_agents:
                identity = json.loads(row[3]) if isinstance(row[3], str) else row[3]
                goal = json.loads(row[4]) if isinstance(row[4], str) else row[4]
                tools = json.loads(row[5]) if isinstance(row[5], str) else row[5]
                permissions = json.loads(row[6]) if isinstance(row[6], str) else row[6]
                
                agents.append(AgentResponse(
                    id=str(row[0]),
                    name=row[1],
                    agent_type=row[2],
                    identity=identity,
                    goal=goal,
                    tools=tools,
                    permissions=permissions,
                    is_active=row[7],
                    created_at=row[8].isoformat() if isinstance(row[8], datetime) else str(row[8])
                ))
            return agents
    except Exception as e:
        print("Database query failed, using memory fallback:", e)

    # In-memory fallback
    agents = []
    for agent in _agents_store.values():
        if active_only and not agent.is_active:
            continue
        if agent_type and agent.config.identity.agent_type.value != agent_type:
            continue
        agents.append(AgentResponse(
            id=agent.id,
            name=agent.config.identity.name,
            agent_type=agent.config.identity.agent_type.value,
            identity=agent.config.identity.model_dump(),
            goal=agent.config.goal.model_dump(),
            tools=[t.model_dump() for t in agent.config.tools],
            permissions=agent.config.permissions.model_dump(),
            is_active=agent.is_active,
            created_at=agent.created_at.isoformat(),
        ))
    return agents

@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: str, db: AsyncSession = Depends(get_db)):
    """Get a specific agent by ID."""
    try:
        res = await db.execute(text("SELECT id, name, agent_type, identity, goal, tools, permissions, is_active, created_at, tenant_id FROM ai.agents WHERE id = :id"), {"id": uuid.UUID(agent_id)})
        row = res.fetchone()
        if row:
            identity = json.loads(row[3]) if isinstance(row[3], str) else row[3]
            goal = json.loads(row[4]) if isinstance(row[4], str) else row[4]
            tools = json.loads(row[5]) if isinstance(row[5], str) else row[5]
            permissions = json.loads(row[6]) if isinstance(row[6], str) else row[6]
            return AgentResponse(
                id=str(row[0]),
                name=row[1],
                agent_type=row[2],
                identity=identity,
                goal=goal,
                tools=tools,
                permissions=permissions,
                is_active=row[7],
                created_at=row[8].isoformat() if isinstance(row[8], datetime) else str(row[8])
            )
    except Exception as e:
        print("Database query for single agent failed, using memory fallback:", e)

    if agent_id not in _agents_store:
        raise HTTPException(status_code=404, detail="Agent not found")
    agent = _agents_store[agent_id]
    return AgentResponse(
        id=agent.id,
        name=agent.config.identity.name,
        agent_type=agent.config.identity.agent_type.value,
        identity=agent.config.identity.model_dump(),
        goal=agent.config.goal.model_dump(),
        tools=[t.model_dump() for t in agent.config.tools],
        permissions=agent.config.permissions.model_dump(),
        is_active=agent.is_active,
        created_at=agent.created_at.isoformat(),
    )

@router.delete("/{agent_id}")
async def delete_agent(agent_id: str, db: AsyncSession = Depends(get_db)):
    """Deactivate an agent."""
    try:
        await db.execute(text("UPDATE ai.agents SET is_active = false WHERE id = :id"), {"id": uuid.UUID(agent_id)})
        await db.commit()
    except Exception as e:
        print("Database deactivation failed, using memory fallback:", e)

    if agent_id in _agents_store:
        _agents_store[agent_id].is_active = False
        return {"status": "success", "message": f"Agent {agent_id} deactivated"}
        
    return {"status": "success", "message": f"Agent {agent_id} deactivated (DB-only)"}

@router.post("/initialize-defaults")
async def initialize_default_agents(tenant_id: str = "00000000-0000-0000-0000-000000000001", db: AsyncSession = Depends(get_db)):
    """Initialize all default agent types for a tenant in the database."""
    created = []
    
    # Enforce PostgreSQL tenant setting context
    try:
        await db.execute(text(f"SELECT set_config('app.tenant_id', '{tenant_id}', true)"))
    except Exception as e:
        print("Failed to set app.tenant_id context:", e)
        
    for agent_type, factory in AGENT_FACTORIES.items():
        config = factory()
        agent_id = _generate_id()
        agent = Agent(
            id=agent_id,
            tenant_id=tenant_id,
            config=config,
        )
        _agents_store[agent_id] = agent
        
        try:
            await db.execute(
                text("""
                INSERT INTO ai.agents (id, tenant_id, name, agent_type, identity, goal, system_prompt, tools, permissions, config, is_active)
                VALUES (:id, :tenant_id, :name, :agent_type, :identity, :goal, :system_prompt, :tools, :permissions, :config, :is_active)
                ON CONFLICT (id) DO NOTHING
                """),
                {
                    "id": uuid.UUID(agent_id),
                    "tenant_id": uuid.UUID(tenant_id),
                    "name": config.identity.name,
                    "agent_type": config.identity.agent_type.value,
                    "identity": json.dumps(config.identity.model_dump()),
                    "goal": json.dumps(config.goal.model_dump()),
                    "system_prompt": config.system_prompt,
                    "tools": json.dumps([t.model_dump() for t in config.tools]),
                    "permissions": json.dumps(config.permissions.model_dump()),
                    "config": json.dumps({
                        "context_window": config.context_window,
                        "temperature": config.temperature,
                        "max_iterations": config.max_iterations
                    }),
                    "is_active": True
                }
            )
            created.append({
                "id": agent_id,
                "name": config.identity.name,
                "type": agent_type.value,
            })
        except Exception as e:
            print(f"Failed to persist default agent {agent_type}:", e)
            # Memory list fallback sync
            created.append({
                "id": agent_id,
                "name": config.identity.name,
                "type": agent_type.value,
            })
            
    try:
        await db.commit()
    except Exception:
        pass
        
    return {"status": "success", "agents_created": created}
