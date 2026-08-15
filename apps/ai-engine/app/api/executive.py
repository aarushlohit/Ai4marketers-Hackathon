"""Executive Intelligence endpoints — provides summaries and answers business Q&A."""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Dict, Any

from app.core.llm import get_llm
from app.prompts.crm_copilot import EXECUTIVE_SUMMARY_PROMPT
from langchain_core.messages import HumanMessage

router = APIRouter()


class ExecutiveBriefingRequest(BaseModel):
    tenant_name: str
    time_period: str = "this month"
    metrics_context: str


class ExecutiveBriefingResponse(BaseModel):
    briefing: str


class ExecutiveQuestionRequest(BaseModel):
    question: str
    context: str


class ExecutiveQuestionResponse(BaseModel):
    answer: str


@router.post("/briefing", response_model=ExecutiveBriefingResponse)
async def generate_briefing(payload: ExecutiveBriefingRequest):
    """Generate a formal executive summary based on metrics context."""
    prompt_text = EXECUTIVE_SUMMARY_PROMPT.format(
        company_name="Miracle Birds",
        time_period=payload.time_period,
        tenant_name=payload.tenant_name,
        metrics_context=payload.metrics_context
    )

    llm = get_llm()
    try:
        response = await llm.ainvoke([HumanMessage(content=prompt_text)])
        return ExecutiveBriefingResponse(briefing=response.content)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating briefing: {str(e)}"
        )


@router.post("/ask", response_model=ExecutiveQuestionResponse)
async def ask_executive_question(payload: ExecutiveQuestionRequest):
    """Answer high-level business queries (e.g. 'Why did revenue decrease?')."""
    prompt_text = f"""You are a senior business intelligence analyst.
    Answer the following executive question based on the provided pipeline and financial context.
    
    Question: {payload.question}
    
    Context:
    {payload.context}
    
    Format your answer as a concise, professional, data-driven report with bullet points. Suggest potential strategic actions.
    """

    llm = get_llm()
    try:
        response = await llm.ainvoke([HumanMessage(content=prompt_text)])
        return ExecutiveQuestionResponse(answer=response.content)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error answering question: {str(e)}"
        )
