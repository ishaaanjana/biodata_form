from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import declarative_base, sessionmaker, Session
import os

DATABASE_URL = "sqlite:///./biodata.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()



class BioDataModel(Base):
    __tablename__ = "biodatas"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    full_name = Column(String, nullable=False)
    dob = Column(String, nullable=False)
    gender = Column(String, nullable=False)
    mobile = Column(String, nullable=False)
    email = Column(String, nullable=False)
    education = Column(String, nullable=False)
    profession = Column(String, nullable=False)
    income = Column(String, nullable=True)
    address = Column(Text, nullable=False)
    father_name = Column(String, nullable=False)
    mother_name = Column(String, nullable=False)
    photo = Column(Text, nullable=True)
    bio = Column(Text, nullable=True)
    skills = Column(String, nullable=True)
    github = Column(String, nullable=True)
    linkedin = Column(String, nullable=True)


Base.metadata.create_all(bind=engine)



class BioDataCreate(BaseModel):
    full_name: str
    dob: str
    gender: str
    mobile: str
    email: str
    education: str
    profession: str
    income: Optional[str] = "N/A"
    address: str
    father_name: str
    mother_name: str
    photo: Optional[str] = ""
    bio: Optional[str] = ""
    skills: Optional[str] = ""
    github: Optional[str] = ""
    linkedin: Optional[str] = ""


class BioDataResponse(BioDataCreate):
    id: int

    class Config:
        from_attributes = True


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app = FastAPI(title="Developer Bio-Data & Portfolio Hub")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.mount("/static", StaticFiles(directory="."), name="static")


@app.get("/")
def serve_ui():
    return FileResponse("index.html")


@app.post("/biodata", response_model=BioDataResponse, status_code=201)
def create_biodata(payload: BioDataCreate, db: Session = Depends(get_db)):
    new_record = BioDataModel(**payload.model_dump())
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    return new_record


@app.get("/biodata", response_model=List[BioDataResponse])
def get_all_biodata(db: Session = Depends(get_db)):
    return db.query(BioDataModel).order_by(BioDataModel.id.desc()).all()


@app.delete("/biodata/{record_id}")
def delete_biodata(record_id: int, db: Session = Depends(get_db)):
    record = db.query(BioDataModel).filter(BioDataModel.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Bio-Data record not found")
    db.delete(record)
    db.commit()
    return {"message": "Record successfully deleted"}