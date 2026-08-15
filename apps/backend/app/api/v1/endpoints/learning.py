"""Endpoints for Reinforcement Learning (RL) tracking and policies."""

from typing import Annotated, Dict, Any, List
from uuid import UUID
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
import json

from app.api.dependencies import CurrentUser, get_current_user, get_db

router = APIRouter()

class RLEpisodeCreate(BaseModel):
    state: Dict[str, Any]
    action: str
    reward: float
    outcome: str
    policy_version: str = "v1"

class RLEpisodeResponse(BaseModel):
    id: UUID
    state: Dict[str, Any]
    action: str
    reward: float
    outcome: str
    policy_version: str
    created_at: datetime

@router.post("/episodes", status_code=201, response_model=RLEpisodeResponse)
async def log_rl_episode(
    payload: RLEpisodeCreate,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Log a reinforcement learning State-Action-Reward tuple.
    Directly logs state interactions (e.g. customer health scores, recommendations).
    """
    try:
        # PostgreSQL tenant context is set in get_db
        res = await db.execute(
            """
            INSERT INTO ai.rl_episodes (tenant_id, state, action, reward, outcome, policy_version)
            VALUES (:tenant_id, :state, :action, :reward, :outcome, :policy_version)
            RETURNING id, state, action, reward, outcome, policy_version, created_at
            """,
            {
                "tenant_id": user.tenant_id,
                "state": json.dumps(payload.state),
                "action": payload.action,
                "reward": payload.reward,
                "outcome": payload.outcome,
                "policy_version": payload.policy_version
            }
        )
        row = res.fetchone()
        await db.commit()
        
        return RLEpisodeResponse(
            id=row[0],
            state=row[1] if isinstance(row[1], dict) else json.loads(row[1]),
            action=row[2],
            reward=row[3],
            outcome=row[4],
            policy_version=row[5],
            created_at=row[6]
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to write reinforcement learning log: {str(e)}"
        )

@router.get("/metrics")
async def get_rl_metrics(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get metrics about recommendation outcomes, rewards, and policy progress."""
    try:
        # Fetch counts by action
        action_res = await db.execute(
            """
            SELECT action, COUNT(*), AVG(reward)
            FROM ai.rl_episodes
            WHERE tenant_id = :tenant_id
            GROUP BY action
            """,
            {"tenant_id": user.tenant_id}
        )
        actions = []
        for r in action_res.fetchall():
            actions.append({
                "action": r[0],
                "count": r[1],
                "average_reward": round(r[2] or 0.0, 2)
            })

        # Fetch outcome distributions
        outcome_res = await db.execute(
            """
            SELECT outcome, COUNT(*)
            FROM ai.rl_episodes
            WHERE tenant_id = :tenant_id
            GROUP BY outcome
            """,
            {"tenant_id": user.tenant_id}
        )
        outcomes = {}
        for r in outcome_res.fetchall():
            outcomes[r[0]] = r[1]

        # Calculate general stats
        stats_res = await db.execute(
            """
            SELECT COUNT(*), AVG(reward), SUM(CASE WHEN reward > 0 THEN 1 ELSE 0 END)
            FROM ai.rl_episodes
            WHERE tenant_id = :tenant_id
            """,
            {"tenant_id": user.tenant_id}
        )
        stats = stats_res.fetchone()
        total = stats[0] or 0
        avg_reward = stats[1] or 0.0
        positives = stats[2] or 0

        # Policy update trigger log (simulated model optimizations)
        policy_res = await db.execute(
            """
            SELECT policy_version, COUNT(*), AVG(reward)
            FROM ai.rl_episodes
            WHERE tenant_id = :tenant_id
            GROUP BY policy_version
            """,
            {"tenant_id": user.tenant_id}
        )
        policies = []
        for r in policy_res.fetchall():
            policies.append({
                "version": r[0],
                "samples": r[1],
                "mean_reward": round(r[2] or 0.0, 2)
            })

        return {
            "total_trials": total,
            "average_reward": round(avg_reward, 3),
            "conversion_rate": round(positives / max(total, 1), 2),
            "actions_performance": actions,
            "outcomes_distribution": outcomes,
            "policies_performance": policies,
            "learning_rate": 0.01,
            "discount_factor": 0.95
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/export", response_class=PlainTextResponse)
async def export_rllib_dataset(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Export logged episodes in Ray/RLlib Offline Dataset JSON lines format.
    Format: {"obs": state, "action": action, "reward": reward, "new_obs": state, "done": true}
    """
    try:
        res = await db.execute(
            """
            SELECT state, action, reward, outcome, created_at
            FROM ai.rl_episodes
            WHERE tenant_id = :tenant_id
            ORDER BY created_at ASC
            """,
            {"tenant_id": user.tenant_id}
        )
        rows = res.fetchall()
        
        json_lines = []
        for r in rows:
            state = r[0] if isinstance(r[0], dict) else json.loads(r[0])
            line = {
                "obs": state,
                "action": r[1],
                "reward": r[2],
                "new_obs": state,  # Contextual bandit simplification (static obs)
                "done": True,
                "info": {"outcome": r[3], "timestamp": r[4].isoformat()}
            }
            json_lines.append(json.dumps(line))
            
        return "\n".join(json_lines)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export RLlib dataset: {str(e)}")
