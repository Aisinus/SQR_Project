from fastapi import FastAPI, Depends, HTTPException, Security
from sqlalchemy.orm import Session
from fastapi.security.api_key import APIKeyHeader
import models
from database import engine
import jwt

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Auth details
API_KEY_NAME = 'Authorization'

api_key_header_auth = APIKeyHeader(name=API_KEY_NAME, auto_error=True)


async def validate_jwt(api_key_header_auth: str = Security(api_key_header_auth)):
    try:
        # Validate JWT
        payload = jwt.decode(api_key_header_auth, options={"verify_signature": False})

        # Get user name from JWT payload
        username = payload.get("username")
        if username is None:
            raise HTTPException(
                status_code=400,
                detail="Invalid JWT: No username provided in payload"
            )

        return username

    except (jwt.PyJWTError, ValueError):
        raise HTTPException(
            status_code=400,
            detail="Invalid JWT"
        ) from None


@app.post("/user")
def get_or_create_user(db: Session = Depends(get_db), username: str = Depends(validate_jwt)):
    # Check if user exists
    db_user = db.query(models.User).filter(models.User.name == username).first()
    
    # If user does not exist, create them
    if not db_user:
        db_user = models.User(name=username)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    
    # Return user info
    return {"username": db_user.name, "created_at": db_user.created_at}
