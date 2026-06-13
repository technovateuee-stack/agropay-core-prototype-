import enum
from sqlalchemy import Column, Integer, String, Float, Enum, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite:///./agropay_final_sandbox.db"

# Safely queue concurrent writes
engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False, "timeout": 30}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class PoolState(enum.Enum):
    PENDING = "pending"
    EXECUTED = "executed"

class FarmerWallet(Base):
    __tablename__ = "farmer_wallets"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    phone = Column(String, unique=True, index=True)
    balance = Column(Float, default=50000.0)

class FeedAggregationPool(Base):
    __tablename__ = "feed_aggregation_pools"
    id = Column(Integer, primary_key=True, index=True)
    cluster_name = Column(String, nullable=False)
    target_moq = Column(Integer, default=120)
    current_bags = Column(Integer, default=0)
    status = Column(Enum(PoolState), default=PoolState.PENDING)

Base.metadata.create_all(bind=engine)
