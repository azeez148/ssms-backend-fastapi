import re
from datetime import datetime
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from app.models.campaign import (
    Campaign, CampaignQuestion, CampaignParticipant,
    CampaignWinner, CampaignCommunication, CampaignStatus, SubmissionStatus
)
from app.schemas.campaign import (
    CampaignCreate, CampaignUpdate, CampaignQuestionCreate,
    CampaignWinnerCreate, CampaignCommunicationCreate
)
from app.core.logging import logger

class CampaignService:
    def _generate_slug(self, db: Session, name: str) -> str:
        base_slug = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')
        slug = base_slug
        counter = 1
        while db.query(Campaign).filter(Campaign.slug == slug).first():
            slug = f"{base_slug}-{counter}"
            counter += 1
        return slug

    def create_campaign(self, db: Session, campaign_data: CampaignCreate, commit: bool = True) -> Campaign:
        # Extract questions if present
        questions_data = campaign_data.questions
        campaign_dict = campaign_data.model_dump(exclude={'questions'})

        if not campaign_dict.get('slug'):
            campaign_dict['slug'] = self._generate_slug(db, campaign_dict['name'])

        db_campaign = Campaign(**campaign_dict)
        db.add(db_campaign)
        db.flush()  # To get the campaign ID

        if questions_data:
            for q_data in questions_data:
                db_question = CampaignQuestion(**q_data.model_dump(), campaign_id=db_campaign.id)
                db.add(db_question)

        if commit:
            db.commit()
            db.refresh(db_campaign)
        return db_campaign

    def create_bulk_campaigns(self, db: Session, campaigns_data: List[CampaignCreate]) -> List[Campaign]:
        created_campaigns = []
        for campaign_data in campaigns_data:
            created_campaigns.append(self.create_campaign(db, campaign_data, commit=False))
        db.commit()
        for c in created_campaigns:
            db.refresh(c)
        return created_campaigns

    def get_campaigns(self, db: Session, page: int = 1, size: int = 10,
                      search: Optional[str] = None, status: Optional[str] = None) -> Tuple[List[Campaign], int]:
        query = db.query(Campaign)

        if search:
            query = query.filter(or_(
                Campaign.name.ilike(f"%{search}%"),
                Campaign.short_description.ilike(f"%{search}%"),
                Campaign.detailed_description.ilike(f"%{search}%")
            ))

        if status:
            query = query.filter(Campaign.status == status)

        total = query.count()
        campaigns = query.offset((page - 1) * size).limit(size).all()
        return campaigns, total

    def get_campaign_by_id(self, db: Session, campaign_id: int) -> Optional[Campaign]:
        return db.query(Campaign).filter(Campaign.id == campaign_id).first()

    def update_campaign(self, db: Session, campaign_id: int, campaign_update: CampaignUpdate) -> Optional[Campaign]:
        db_campaign = self.get_campaign_by_id(db, campaign_id)
        if not db_campaign:
            return None

        update_data = campaign_update.model_dump(exclude_unset=True, exclude={'id'})
        for key, value in update_data.items():
            setattr(db_campaign, key, value)

        db.commit()
        db.refresh(db_campaign)
        return db_campaign

    def update_campaign_status(self, db: Session, campaign_id: int, status: str) -> Optional[Campaign]:
        db_campaign = self.get_campaign_by_id(db, campaign_id)
        if not db_campaign:
            return None

        db_campaign.status = status
        db.commit()
        db.refresh(db_campaign)
        return db_campaign

    def get_campaign_stats(self, db: Session):
        total_campaigns = db.query(Campaign).count()
        active_campaigns = db.query(Campaign).filter(Campaign.status == CampaignStatus.ACTIVE).count()
        total_participants = db.query(func.sum(Campaign.total_participants)).scalar() or 0
        total_submissions = db.query(func.sum(Campaign.total_submissions)).scalar() or 0
        winners_announced = db.query(CampaignWinner).count()

        return {
            "total_campaigns": total_campaigns,
            "active_campaigns": active_campaigns,
            "total_participants": total_participants,
            "total_submissions": total_submissions,
            "winners_announced": winners_announced
        }

    # Questions
    def get_questions(self, db: Session, campaign_id: int) -> List[CampaignQuestion]:
        return db.query(CampaignQuestion).filter(CampaignQuestion.campaign_id == campaign_id).order_by(CampaignQuestion.order).all()

    def save_questions(self, db: Session, campaign_id: int, questions: List[CampaignQuestionCreate]) -> List[CampaignQuestion]:
        # Overwrite all questions
        db.query(CampaignQuestion).filter(CampaignQuestion.campaign_id == campaign_id).delete()

        db_questions = []
        for i, q_data in enumerate(questions):
            q_dict = q_data.model_dump()
            if q_dict.get('order') is None:
                q_dict['order'] = i
            db_question = CampaignQuestion(**q_dict, campaign_id=campaign_id)
            db.add(db_question)
            db_questions.append(db_question)

        db.commit()
        return db_questions

    # Participants
    def get_participants(self, db: Session, campaign_id: int, page: int = 1, size: int = 10, search: Optional[str] = None) -> Tuple[List[CampaignParticipant], int]:
        query = db.query(CampaignParticipant).filter(CampaignParticipant.campaign_id == campaign_id)

        if search:
            query = query.filter(or_(
                CampaignParticipant.participant_name.ilike(f"%{search}%"),
                CampaignParticipant.email.ilike(f"%{search}%")
            ))

        total = query.count()
        participants = query.offset((page - 1) * size).limit(size).all()
        return participants, total

    def add_participant(self, db: Session, campaign_id: int, participant_data: dict) -> CampaignParticipant:
        db_participant = CampaignParticipant(**participant_data, campaign_id=campaign_id, joined_on=datetime.now())
        db.add(db_participant)

        # Update campaign total
        db_campaign = self.get_campaign_by_id(db, campaign_id)
        if db_campaign:
            db_campaign.total_participants += 1

        db.commit()
        db.refresh(db_participant)
        return db_participant

    def remove_participant(self, db: Session, campaign_id: int, participant_id: int) -> bool:
        db_participant = db.query(CampaignParticipant).filter(
            CampaignParticipant.id == participant_id,
            CampaignParticipant.campaign_id == campaign_id
        ).first()

        if not db_participant:
            return False

        was_submitted = db_participant.submission_status == SubmissionStatus.SUBMITTED
        db.delete(db_participant)

        # Update campaign total
        db_campaign = self.get_campaign_by_id(db, campaign_id)
        if db_campaign:
            if db_campaign.total_participants > 0:
                db_campaign.total_participants -= 1
            if was_submitted and db_campaign.total_submissions > 0:
                db_campaign.total_submissions -= 1

        db.commit()
        return True

    def submit_entry(self, db: Session, campaign_id: int, participant_id: int) -> bool:
        db_participant = db.query(CampaignParticipant).filter(
            CampaignParticipant.id == participant_id,
            CampaignParticipant.campaign_id == campaign_id
        ).first()

        if not db_participant:
            return False

        if db_participant.submission_status == SubmissionStatus.SUBMITTED:
            return True # Already submitted

        db_participant.submission_status = SubmissionStatus.SUBMITTED

        # Update campaign total
        db_campaign = self.get_campaign_by_id(db, campaign_id)
        if db_campaign:
            db_campaign.total_submissions += 1

        db.commit()
        return True

    # Winners
    def get_winners(self, db: Session, campaign_id: int, winner_type: Optional[str] = None) -> List[CampaignWinner]:
        query = db.query(CampaignWinner).filter(CampaignWinner.campaign_id == campaign_id)
        if winner_type:
            query = query.filter(CampaignWinner.winner_type == winner_type)
        return query.all()

    def assign_winner(self, db: Session, campaign_id: int, winner_data: CampaignWinnerCreate) -> CampaignWinner:
        w_dict = winner_data.model_dump()

        # Try to resolve participant if id is missing but name is present
        if not w_dict.get('participant_id') and w_dict.get('participant_name'):
            participant = db.query(CampaignParticipant).filter(
                CampaignParticipant.campaign_id == campaign_id,
                CampaignParticipant.participant_name == w_dict['participant_name']
            ).first()
            if participant:
                w_dict['participant_id'] = participant.id

        if not w_dict.get('selected_date'):
            w_dict['selected_date'] = datetime.now()

        db_winner = CampaignWinner(**w_dict, campaign_id=campaign_id)
        db.add(db_winner)
        db.commit()
        db.refresh(db_winner)
        return db_winner

    def remove_winner(self, db: Session, campaign_id: int, winner_id: int) -> bool:
        db_winner = db.query(CampaignWinner).filter(
            CampaignWinner.id == winner_id,
            CampaignWinner.campaign_id == campaign_id
        ).first()

        if not db_winner:
            return False

        db.delete(db_winner)
        db.commit()
        return True

    # Communications
    def trigger_communication(self, db: Session, campaign_id: int, comm_data: CampaignCommunicationCreate) -> CampaignCommunication:
        # Logic for sending email/WhatsApp would go here
        # For now, we just log it to the database

        db_campaign = self.get_campaign_by_id(db, campaign_id)
        recipient_count = 0
        if comm_data.recipient_type == "all":
            recipient_count = db.query(CampaignParticipant).filter(CampaignParticipant.campaign_id == campaign_id).count()
        else:
            recipient_count = 1

        db_comm = CampaignCommunication(
            **comm_data.model_dump(),
            campaign_id=campaign_id,
            sent_at=datetime.now(),
            recipient_count=recipient_count
        )
        db.add(db_comm)
        db.commit()
        db.refresh(db_comm)
        return db_comm

    def get_communications(self, db: Session, campaign_id: int) -> List[CampaignCommunication]:
        return db.query(CampaignCommunication).filter(CampaignCommunication.campaign_id == campaign_id).all()

    def update_campaign_image(self, db: Session, campaign_id: int, image_url: str, image_type: str) -> Optional[Campaign]:
        db_campaign = self.get_campaign_by_id(db, campaign_id)
        if not db_campaign:
            return None

        if image_type == 'desktop':
            db_campaign.desktop_banner = image_url
        elif image_type == 'mobile':
            db_campaign.mobile_banner = image_url
        elif image_type == 'promotional':
            if not db_campaign.promotional_images:
                db_campaign.promotional_images = []
            # Make sure it's a list (JSON column might return list or str depending on DB/SQLAlchemy config)
            if isinstance(db_campaign.promotional_images, list):
                db_campaign.promotional_images.append(image_url)
            else:
                db_campaign.promotional_images = [image_url]

        db.commit()
        db.refresh(db_campaign)
        return db_campaign
