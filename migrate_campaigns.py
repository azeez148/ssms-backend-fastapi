from app.core.database import Base, engine
from app.models.campaign import Campaign, CampaignQuestion, CampaignParticipant, CampaignWinner, CampaignCommunication

def migrate():
    print("Creating campaign tables...")
    Campaign.__table__.create(engine, checkfirst=True)
    CampaignQuestion.__table__.create(engine, checkfirst=True)
    CampaignParticipant.__table__.create(engine, checkfirst=True)
    CampaignWinner.__table__.create(engine, checkfirst=True)
    CampaignCommunication.__table__.create(engine, checkfirst=True)
    print("Campaign tables created successfully!")

if __name__ == "__main__":
    migrate()
