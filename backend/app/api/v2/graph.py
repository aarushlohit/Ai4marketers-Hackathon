from fastapi import APIRouter

router = APIRouter()


@router.get("/relationships")
def get_graph_relationships(entity_type: str, entity_id: str):
    # Mock Neo4j graph response
    return {
        "status": "success",
        "nodes": [
            {"id": "c1", "label": "Company", "name": "Acme Corp"},
            {"id": "d1", "label": "Deal", "name": "Project Apollo"},
            {"id": "m1", "label": "Meeting", "name": "Q3 Planning"},
        ],
        "edges": [
            {"source": "c1", "target": "d1", "type": "HAS_DEAL"},
            {"source": "m1", "target": "d1", "type": "DISCUSSED"},
        ],
    }
