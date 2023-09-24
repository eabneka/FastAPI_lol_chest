#chest.py
import json
from .. import models, schemas, oauth2, RiotAPI
from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from sqlalchemy.sql.expression import join

def updateMastery(summonerId:str, db: Session = Depends(get_db)):
    dicts = RiotAPI.top_n_Mastery(summonerId)
    for m in dicts:
        db.add(models.ChampionMastery(chestGranted=m['chestGranted'],championId=m['championId']
            ,lastPlayTime=m['lastPlayTime'],summonerId=m['summonerId'],championPoints=m['championPoints']))
        


router = APIRouter(
    prefix="/chest",
    tags=['\'S-\' chest']
)

@router.get("/{nickname}",response_model=List[schemas.ChestOut])
def get_post(nickname: str, db: Session = Depends(get_db)):
    summoner = db.query(models.Summoner).filter(models.Summoner.name == nickname).first()
    
    if not summoner:
        try:
            accountId, summonerId, name = RiotAPI.summonerByName(nickname)
        except:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"summoner with name:{nickname} was not found")

        summoner = models.Summoner(accountId=accountId,summonerId=summonerId, name=name)
        db.add(summoner)
        db.commit()
        db.refresh(summoner)

        updateMastery(summonerId, db)

        db.commit()

    res =db.query(models.ChampionMastery, models.Champion.en_US, models.Champion.ko_KR).join(models.Champion, models.Champion.id==models.ChampionMastery.championId,isouter=True).filter(models.ChampionMastery.summonerId==summoner.summonerId).order_by(models.ChampionMastery.championPoints.desc()).all()#.column_descriptions
    #db.column_descriptions
    print(type(res))
    print(res)
    print(type(res[0]))
    print(res[0])

    dic = res[0]._asdict()
    ls=[]
    for i in res:
        print(i)
        ls.append(i._asdict())
    print(type(dic))
    print(dic)

    results = list ( map (lambda x : x._mapping, res) )
    return results




@router.get('/update/{nickname}')
def update_summoner(nickname: str, db: Session = Depends(get_db)):
    summoner = db.query(models.Summoner).filter(models.Summoner.name == nickname).first()

    if not summoner:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"summoner with name:{nickname} was not found")

    post_query = db.query(models.ChampionMastery).filter(models.ChampionMastery.summonerId == summoner.summonerId)

    post = post_query.first()
    if post == None:#deleted_post == None
        db.query(models.Summoner).filter(models.Summoner.name == nickname).delete(synchronize_session=False)
        db.commit()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"summoner with name:{nickname} was not found")
    post_query.delete(synchronize_session=False)

    updateMastery(summoner.summonerId, db)
    db.commit()