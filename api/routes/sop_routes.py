from fastapi import File, UploadFile, APIRouter, FileResponse, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from database.connection import SessionLocal
from database.models import SOP
from services.email_service import send_email
from services.grammar_checker import check_grammar
from auth.jwt_handler import verify_access_token

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/generate-sop")
def generate_sop(user_email: str, db: Session = Depends(get_db)):
    # Generate SOP (replace with actual generation logic)
    sop_content = "Generated SOP content..."
    
    # Save SOP to the database
    new_sop = SOP(user_email=user_email, sop_content=sop_content)
    db.add(new_sop)
    db.commit()
    
    # Send a confirmation email
    send_email(
        to_email=user_email,
        subject="Your SOP is Ready!",
        content="<p>Your SOP has been successfully generated. You can download it from your dashboard.</p>"
    )
    return {"message": "SOP generated successfully and email sent!"}

@router.post("/check-grammar")
def grammar_check(text: str):
    """Endpoint to check grammar for a given text."""
    result = check_grammar(text)
    return {"grammar_issues": result['matches']}

@router.post("/upload-sop")
def upload_sop(file: UploadFile = File(...)):
    with open(f"uploads/{file.filename}", "wb") as out_file:
        content = file.file.read()
        out_file.write(content)
    return {"filename": file.filename}

@router.get("/download-sop/{filename}")
def download_sop(filename: str):
    file_path = f"uploads/{filename}"
    return FileResponse(file_path, media_type='application/octet-stream', filename=filename)

def get_current_user(token: str = Depends(oauth2_scheme)):
    user = verify_access_token(token)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return user
