import re
from datetime import datetime
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from app.models.campaign import (
    Campaign, CampaignQuestion, CampaignParticipant,
    CampaignWinner, CampaignCommunication, CampaignStatus, SubmissionStatus,
    CampaignV2, CampaignField, CampaignParticipation, CampaignStatusV2, ParticipationStatus,
    CampaignTypeV2, FieldType
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

    # V2 Service Methods
    def get_campaigns_v2(self, db: Session, status: Optional[str] = None) -> List[CampaignV2]:
        query = db.query(CampaignV2)
        if status:
            query = query.filter(CampaignV2.status == status)

        campaigns = query.all()
        for c in campaigns:
            c.participation_count = db.query(CampaignParticipation).filter(CampaignParticipation.campaign_id == c.id).count()
            c.submission_count = db.query(CampaignParticipation).filter(
                CampaignParticipation.campaign_id == c.id,
                CampaignParticipation.status == ParticipationStatus.SUBMITTED
            ).count()
        return campaigns

    def get_campaigns_v2_admin(self, db: Session, page: int = 1, per_page: int = 10,
                             status: Optional[str] = None, search: Optional[str] = None) -> Tuple[List[CampaignV2], int]:
        query = db.query(CampaignV2)
        if status:
            query = query.filter(CampaignV2.status == status)
        if search:
            query = query.filter(CampaignV2.title.ilike(f"%{search}%"))

        total = query.count()
        campaigns = query.offset((page - 1) * per_page).limit(per_page).all()

        for c in campaigns:
            c.participation_count = db.query(CampaignParticipation).filter(CampaignParticipation.campaign_id == c.id).count()
            c.submission_count = db.query(CampaignParticipation).filter(
                CampaignParticipation.campaign_id == c.id,
                CampaignParticipation.status == ParticipationStatus.SUBMITTED
            ).count()

        return campaigns, total

    def get_active_campaigns_v2(self, db: Session) -> List[CampaignV2]:
        campaigns = db.query(CampaignV2).filter(CampaignV2.status == CampaignStatusV2.active).all()
        for c in campaigns:
            c.participation_count = db.query(CampaignParticipation).filter(CampaignParticipation.campaign_id == c.id).count()
            c.submission_count = db.query(CampaignParticipation).filter(
                CampaignParticipation.campaign_id == c.id,
                CampaignParticipation.status == ParticipationStatus.SUBMITTED
            ).count()
        return campaigns

    def get_campaign_v2_by_id(self, db: Session, campaign_id: str) -> Optional[CampaignV2]:
        c = db.query(CampaignV2).filter(CampaignV2.id == campaign_id).first()
        if c:
            c.participation_count = db.query(CampaignParticipation).filter(CampaignParticipation.campaign_id == c.id).count()
            c.submission_count = db.query(CampaignParticipation).filter(
                CampaignParticipation.campaign_id == c.id,
                CampaignParticipation.status == ParticipationStatus.SUBMITTED
            ).count()
        return c

    def create_campaign_v2(self, db: Session, campaign_data: dict, user_id: Optional[str] = None) -> CampaignV2:
        import uuid
        try:
            questions = campaign_data.pop('questions', []) or []

            # Map keys
            rename_map = {
                "starts_at": "start_date",
                "ends_at": "end_date",
                "metadata": "meta_data"
            }
            for old_key, new_key in rename_map.items():
                if old_key in campaign_data:
                    campaign_data[new_key] = campaign_data.pop(old_key)

            # Enum conversion
            if 'type' in campaign_data and campaign_data['type']:
                campaign_data['type'] = CampaignTypeV2(campaign_data['type'])
            if 'status' in campaign_data and campaign_data['status']:
                campaign_data['status'] = CampaignStatusV2(campaign_data['status'])

            # Allowed fields whitelist
            allowed_fields = {
                "title", "description", "type", "status",
                "start_date", "end_date", "image_url",
                "rules", "terms_and_conditions", "meta_data",
                "winners", "results_summary"
            }
            filtered_data = {k: v for k, v in campaign_data.items() if k in allowed_fields}

            campaign_id = str(uuid.uuid4())
            db_campaign = CampaignV2(id=campaign_id, **filtered_data, created_by=user_id)
            db.add(db_campaign)

            for q in questions:
                field_id = str(uuid.uuid4())
                if 'type' in q and q['type']:
                    q['type'] = FieldType(q['type'])
                db_field = CampaignField(id=field_id, campaign_id=campaign_id, **q)
                db.add(db_field)

            db.commit()
            db.refresh(db_campaign)
            return self.get_campaign_v2_by_id(db, campaign_id)
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating campaign v2: {str(e)}")
            raise e

    def update_campaign_v2(self, db: Session, campaign_id: str, campaign_data: dict, user_id: Optional[str] = None) -> Optional[CampaignV2]:
        try:
            db_campaign = db.query(CampaignV2).filter(CampaignV2.id == campaign_id).first()
            if not db_campaign:
                return None

            questions = campaign_data.pop('questions', None)

            # Map keys
            rename_map = {
                "starts_at": "start_date",
                "ends_at": "end_date",
                "metadata": "meta_data"
            }
            for old_key, new_key in rename_map.items():
                if old_key in campaign_data:
                    campaign_data[new_key] = campaign_data.pop(old_key)

            # Enum conversion
            if 'type' in campaign_data and campaign_data['type']:
                campaign_data['type'] = CampaignTypeV2(campaign_data['type'])
            if 'status' in campaign_data and campaign_data['status']:
                campaign_data['status'] = CampaignStatusV2(campaign_data['status'])

            # Allowed fields whitelist
            allowed_fields = {
                "title", "description", "type", "status",
                "start_date", "end_date", "image_url",
                "rules", "terms_and_conditions", "meta_data",
                "winners", "results_summary"
            }

            for key, value in campaign_data.items():
                if key in allowed_fields:
                    setattr(db_campaign, key, value)

            db_campaign.updated_by = user_id

            if questions is not None:
                # Overwrite fields
                db.query(CampaignField).filter(CampaignField.campaign_id == campaign_id).delete(synchronize_session=False)
                import uuid
                for q in questions:
                    field_id = str(uuid.uuid4())
                    if 'type' in q and q['type']:
                        q['type'] = FieldType(q['type'])
                    db_field = CampaignField(id=field_id, campaign_id=campaign_id, **q)
                    db.add(db_field)

            db.commit()
            db.refresh(db_campaign)
            return self.get_campaign_v2_by_id(db, campaign_id)
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating campaign v2: {str(e)}")
            raise e

    def patch_campaign_v2(self, db: Session, campaign_id: str, patch_data: dict, user_id: Optional[str] = None) -> Optional[CampaignV2]:
        try:
            db_campaign = db.query(CampaignV2).filter(CampaignV2.id == campaign_id).first()
            if not db_campaign:
                return None

            # Map keys
            rename_map = {
                "starts_at": "start_date",
                "ends_at": "end_date",
                "metadata": "meta_data"
            }
            for old_key, new_key in rename_map.items():
                if old_key in patch_data:
                    patch_data[new_key] = patch_data.pop(old_key)

            # Enum conversion
            if 'status' in patch_data and patch_data['status']:
                patch_data['status'] = CampaignStatusV2(patch_data['status'])
            if 'type' in patch_data and patch_data['type']:
                patch_data['type'] = CampaignTypeV2(patch_data['type'])

            force = patch_data.pop('force', False)

            # Allowed fields whitelist
            allowed_fields = {
                "title", "description", "type", "status",
                "start_date", "end_date", "image_url",
                "rules", "terms_and_conditions", "meta_data",
                "winners", "results_summary"
            }

            for key, value in patch_data.items():
                if key in allowed_fields and value is not None:
                    setattr(db_campaign, key, value)

            db_campaign.updated_by = user_id
            db.commit()
            db.refresh(db_campaign)
            return self.get_campaign_v2_by_id(db, campaign_id)
        except Exception as e:
            db.rollback()
            logger.error(f"Error patching campaign v2: {str(e)}")
            raise e

    def delete_campaign_v2(self, db: Session, campaign_id: str) -> bool:
        try:
            db_campaign = db.query(CampaignV2).filter(CampaignV2.id == campaign_id).first()
            if not db_campaign:
                return False
            db.delete(db_campaign)
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting campaign v2: {str(e)}")
            raise e

    def get_campaign_stats_v2(self, db: Session) -> dict:
        total_campaigns = db.query(CampaignV2).count()
        active_campaigns = db.query(CampaignV2).filter(CampaignV2.status == CampaignStatusV2.ACTIVE).count()
        draft_campaigns = db.query(CampaignV2).filter(CampaignV2.status == CampaignStatusV2.DRAFT).count()
        total_participations = db.query(CampaignParticipation).count()

        # Calculate completion rate
        total_submissions = db.query(CampaignParticipation).filter(CampaignParticipation.status == ParticipationStatus.SUBMITTED).count()
        completion_rate = (total_submissions / total_participations * 100) if total_participations > 0 else 0

        return {
            "totalCampaigns": total_campaigns,
            "activeCampaigns": active_campaigns,
            "draftCampaigns": draft_campaigns,
            "totalParticipations": total_participations,
            "completionRate": completion_rate
        }

    def bulk_action_v2(self, db: Session, ids: List[str], action: str, force: bool = False, user_id: Optional[str] = None) -> dict:
        success = []
        failed = []

        try:
            for campaign_id in ids:
                try:
                    db_campaign = db.query(CampaignV2).filter(CampaignV2.id == campaign_id).first()
                    if not db_campaign:
                        failed.append({"id": campaign_id, "error": "Not found"})
                        continue

                    if action == 'publish':
                        db_campaign.status = CampaignStatusV2.ACTIVE
                    elif action == 'unpublish':
                        db_campaign.status = CampaignStatusV2.PAUSED
                    elif action == 'pause':
                        db_campaign.status = CampaignStatusV2.PAUSED
                    elif action == 'delete':
                        db.delete(db_campaign)

                    if action != 'delete' and db_campaign:
                        db_campaign.updated_by = user_id

                    success.append(campaign_id)
                except Exception as e:
                    failed.append({"id": campaign_id, "error": str(e)})

            db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"Error performing bulk action v2: {str(e)}")
            return {"success": [], "failed": [{"id": "all", "error": str(e)}]}

        return {"success": success, "failed": failed}

    def participate_v2(self, db: Session, campaign_id: str, user_id: str, responses: dict) -> CampaignParticipation:
        import uuid
        try:
            db_campaign = self.get_campaign_v2_by_id(db, campaign_id)
            if not db_campaign:
                raise Exception("Campaign not found")

            if db_campaign.status != CampaignStatusV2.ACTIVE:
                raise Exception("Campaign is not active")

            if db_campaign.end_date and datetime.now() > db_campaign.end_date:
                raise Exception("Campaign has ended")

            # Check if already participated
            existing = db.query(CampaignParticipation).filter(
                CampaignParticipation.campaign_id == campaign_id,
                CampaignParticipation.user_id == user_id
            ).first()
            if existing:
                raise Exception("Already participated")

            db_participation = CampaignParticipation(
                id=str(uuid.uuid4()),
                campaign_id=campaign_id,
                user_id=user_id,
                responses=responses,
                participation_date=datetime.now()
            )
            db.add(db_participation)
            db.commit()
            db.refresh(db_participation)
            return db_participation
        except Exception as e:
            db.rollback()
            logger.error(f"Error participating in campaign v2: {str(e)}")
            raise e

    def get_my_participations_v2(self, db: Session, user_id: str) -> List[CampaignParticipation]:
        return db.query(CampaignParticipation).filter(CampaignParticipation.user_id == user_id).all()

    def get_my_participation_v2(self, db: Session, campaign_id: str, user_id: str) -> Optional[CampaignParticipation]:
        return db.query(CampaignParticipation).filter(
            CampaignParticipation.campaign_id == campaign_id,
            CampaignParticipation.user_id == user_id
        ).first()

    def get_campaign_results_v2(self, db: Session, campaign_id: str) -> Optional[dict]:
        db_campaign = self.get_campaign_v2_by_id(db, campaign_id)
        if not db_campaign:
            return None

        participations = db.query(CampaignParticipation).filter(CampaignParticipation.campaign_id == campaign_id).all()

        results = {} # Field ID -> {Option -> Count}
        for p in participations:
            for field_id, response in p.responses.items():
                if field_id not in results:
                    results[field_id] = {}

                resp_str = str(response)
                results[field_id][resp_str] = results[field_id].get(resp_str, 0) + 1

        return {
            "campaign_id": campaign_id,
            "total_participations": len(participations),
            "responses": results
        }

    def update_campaign_image(self, db: Session, campaign_id: int, image_url: str, image_type: str) -> Optional[Campaign]:
        db_campaign = self.get_campaign_by_id(db, campaign_id)
        if not db_campaign:
            return None

        if image_type == 'desktop':
            db_campaign.desktop_banner = image_url
        elif image_type == 'mobile':
            db_campaign.mobile_banner = image_url
        elif image_type == 'promotional':
            # Make sure it's a list and create a copy to trigger SQLAlchemy update
            current_images = db_campaign.promotional_images or []
            if not isinstance(current_images, list):
                current_images = []

            new_images = list(current_images)
            new_images.append(image_url)
            db_campaign.promotional_images = new_images

        db.commit()
        db.refresh(db_campaign)
        return db_campaign
