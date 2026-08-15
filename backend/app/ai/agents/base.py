from typing import TypedDict, Annotated, Sequence
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], "The messages in the conversation"]
    context: dict


def sales_agent(state: AgentState):
    # Mock sales agent processing
    return {"messages": state["messages"]}


def executive_agent(state: AgentState):
    # Mock executive agent processing
    return {"messages": state["messages"]}


def create_multi_agent_graph():
    workflow = StateGraph(AgentState)

    workflow.add_node("sales_agent", sales_agent)
    workflow.add_node("executive_agent", executive_agent)

    # Define a simple linear workflow for testing
    workflow.add_edge("sales_agent", "executive_agent")
    workflow.add_edge("executive_agent", END)

    workflow.set_entry_point("sales_agent")
    return workflow.compile()


multi_agent_app = create_multi_agent_graph()
