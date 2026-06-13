from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models
from models import SessionLocal, FarmerWallet, FeedAggregationPool, PoolState

app = FastAPI(title="AgroPay Suite Production Engine Loop")

def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/api/v1/feedbulk/secure-commit")
async def secure_commit_to_pool(user_id: int, pool_id: int, volume: int, db: Session = Depends(get_db_session)):
    
    # Block negative injection volume exploits completely
    if volume <= 0:
        raise HTTPException(status_code=400, detail="Commitment volume must be greater than zero.")
        
    pool = db.query(FeedAggregationPool).filter(FeedAggregationPool.id == pool_id).with_for_update().first()
    user = db.query(FarmerWallet).filter(FarmerWallet.id == user_id).with_for_update().first()
    
    if not pool or not user:
        raise HTTPException(status_code=404, detail="Target processing entities not found.")
        
    price_per_bag = 15000.0
    if pool.current_bags + volume >= pool.target_moq:
        price_per_bag = 11000.0 
        
    total_cost = volume * price_per_bag
    if user.balance < total_cost:
        raise HTTPException(status_code=400, detail="Insufficient OPay wallet funds.")
        
    user.balance -= total_cost
    pool.current_bags += volume
    
    if pool.current_bags >= pool.target_moq:
        pool.status = PoolState.EXECUTED
        
    db.commit()
    return {"status": "success", "current_pool_volume": pool.current_bags, "state": pool.status.value}
