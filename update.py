#update.py
from .. import models, schemas, oauth2, RiotAPI
from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db

router = APIRouter(
    prefix="/update",
    tags=['admin util']
)

@router.get("/")
def fillChampion(db: Session = Depends(get_db)):
    Aatrox = db.query(models.Champion).filter(models.Champion.en_US == 'Aatrox').first()

    if Aatrox:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not authorized to perform requested action')

    dicts = RiotAPI.fillChampion()
    for c in dicts:
        db.add(models.Champion(id=c['key'],en_US=c['id']
            ,ko_KR=c['name']))

    db.commit()

    
