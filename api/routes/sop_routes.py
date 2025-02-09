from fastapi import APIRouter, Depends
from services.sop_service import generate_sop

router = APIRouter()

@router.post("/generate-sop")
def create_sop(user_details: dict, sop_content: dict):
    sop_file = generate_sop(user_details, sop_content)
    return {"message": "SOP generated successfully", "file": sop_file}
