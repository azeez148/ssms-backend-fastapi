from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from datetime import datetime, timezone

from app.models.campaign import (
    Campaign, CampaignMedia, CampaignForm, CampaignFormField,
    CampaignDeadline, CampaignWinnerConfig, CampaignParticipant,
    CampaignSubmission, CampaignCommunication,
    CampaignStatus, ParticipationStatus
)
from app.schemas.campaign import (
    CampaignCreate, CampaignUpdate,
    CampaignMediaCreate, CampaignFormCreate,
    CampaignDeadlineCreate, CampaignWinnerConfigCreate,
    CampaignCommunicationCreate, CampaignParticipantCreate,
    CampaignSubmissionCreate
)


class CampaignService:

    # --- Campaign CRUD ---

    def create_campaign(self, db: Session, campaign_data: CampaignCreate) -> Campaign:
        campaign = Campaign(
            name=campaign_data.name,
            slug=campaign_data.slug,
            description=campaign_data.description,
            campaign_type=campaign_data.campaign_type,
            status=campaign_data.status,
            terms_and_conditions=campaign_data.terms_and_conditions,
            metadata_json=campaign_data.metadata_json,
            participation_requirements=campaign_data.participation_requirements,
            is_active=campaign_data.is_active,
        )
        db.add(campaign)
        db.flush()

        # Add media
        for media_data in campaign_data.media:
            media = CampaignMedia(campaign_id=campaign.id, **media_data.model_dump())
            db.add(media)

        # Add forms with fields
        for form_data in campaign_data.forms:
            form = CampaignForm(
                campaign_id=campaign.id,
                name=form_data.name,
                description=form_data.description,
                is_required=form_data.is_required,
                sort_order=form_data.sort_order,
            )
            db.add(form)
            db.flush()
            for field_data in form_data.fields:
                field = CampaignFormField(form_id=form.id, **field_data.model_dump())
                db.add(field)

        # Add deadlines
        for deadline_data in campaign_data.deadlines:
            deadline = CampaignDeadline(campaign_id=campaign.id, **deadline_data.model_dump())
            db.add(deadline)

        # Add winner configs
        for wc_data in campaign_data.winner_configs:
            wc = CampaignWinnerConfig(campaign_id=campaign.id, **wc_data.model_dump())
            db.add(wc)

        # Add communications
        for comm_data in campaign_data.communications:
            comm = CampaignCommunication(campaign_id=campaign.id, **comm_data.model_dump())
            db.add(comm)

        db.commit()
        db.refresh(campaign)
        return campaign

    def get_campaign(self, db: Session, campaign_id: int) -> Optional[Campaign]:
        return db.query(Campaign).filter(Campaign.id == campaign_id).first()

    def get_campaign_by_slug(self, db: Session, slug: str) -> Optional[Campaign]:
        return db.query(Campaign).filter(Campaign.slug == slug).first()

    def get_active_campaigns(self, db: Session) -> List[Campaign]:
        return db.query(Campaign).filter(
            and_(Campaign.is_active == True, Campaign.status == CampaignStatus.ACTIVE)
        ).all()

    def get_all_campaigns(self, db: Session, skip: int = 0, limit: int = 100) -> List[Campaign]:
        return db.query(Campaign).offset(skip).limit(limit).all()

    def update_campaign(self, db: Session, campaign_id: int, campaign_data: CampaignUpdate) -> Optional[Campaign]:
        campaign = self.get_campaign(db, campaign_id)
        if not campaign:
            return None

        update_data = campaign_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(campaign, field, value)

        db.commit()
        db.refresh(campaign)
        return campaign

    def delete_campaign(self, db: Session, campaign_id: int) -> bool:
        campaign = self.get_campaign(db, campaign_id)
        if not campaign:
            return False
        db.delete(campaign)
        db.commit()
        return True

    # --- Media ---

    def add_media(self, db: Session, campaign_id: int, media_data: CampaignMediaCreate) -> Optional[CampaignMedia]:
        campaign = self.get_campaign(db, campaign_id)
        if not campaign:
            return None
        media = CampaignMedia(campaign_id=campaign_id, **media_data.model_dump())
        db.add(media)
        db.commit()
        db.refresh(media)
        return media

    def delete_media(self, db: Session, media_id: int) -> bool:
        media = db.query(CampaignMedia).filter(CampaignMedia.id == media_id).first()
        if not media:
            return False
        db.delete(media)
        db.commit()
        return True

    # --- Forms ---

    def add_form(self, db: Session, campaign_id: int, form_data: CampaignFormCreate) -> Optional[CampaignForm]:
        campaign = self.get_campaign(db, campaign_id)
        if not campaign:
            return None
        form = CampaignForm(
            campaign_id=campaign_id,
            name=form_data.name,
            description=form_data.description,
            is_required=form_data.is_required,
            sort_order=form_data.sort_order,
        )
        db.add(form)
        db.flush()
        for field_data in form_data.fields:
            field = CampaignFormField(form_id=form.id, **field_data.model_dump())
            db.add(field)
        db.commit()
        db.refresh(form)
        return form

    def delete_form(self, db: Session, form_id: int) -> bool:
        form = db.query(CampaignForm).filter(CampaignForm.id == form_id).first()
        if not form:
            return False
        db.delete(form)
        db.commit()
        return True

    # --- Deadlines ---

    def add_deadline(self, db: Session, campaign_id: int, deadline_data: CampaignDeadlineCreate) -> Optional[CampaignDeadline]:
        campaign = self.get_campaign(db, campaign_id)
        if not campaign:
            return None
        deadline = CampaignDeadline(campaign_id=campaign_id, **deadline_data.model_dump())
        db.add(deadline)
        db.commit()
        db.refresh(deadline)
        return deadline

    def check_deadline(self, db: Session, campaign_id: int, deadline_type: str) -> bool:
        """Check if a deadline has passed. Returns True if within deadline or no enforced deadline exists."""
        deadline = db.query(CampaignDeadline).filter(
            and_(
                CampaignDeadline.campaign_id == campaign_id,
                CampaignDeadline.deadline_type == deadline_type,
                CampaignDeadline.is_enforced == True,
            )
        ).first()
        if not deadline:
            return True
        now = datetime.now(timezone.utc)
        if deadline.starts_at:
            starts_at = deadline.starts_at if deadline.starts_at.tzinfo else deadline.starts_at.replace(tzinfo=timezone.utc)
            if now < starts_at:
                return False
        ends_at = deadline.ends_at if deadline.ends_at.tzinfo else deadline.ends_at.replace(tzinfo=timezone.utc)
        if now > ends_at:
            return False
        return True

    # --- Participants ---

    def register_participant(
        self, db: Session, campaign_id: int, participant_data: CampaignParticipantCreate
    ) -> Optional[CampaignParticipant]:
        campaign = self.get_campaign(db, campaign_id)
        if not campaign:
            return None

        # Check registration deadline
        if not self.check_deadline(db, campaign_id, "registration"):
            return None

        # Check participation requirements
        if campaign.participation_requirements:
            if not self._check_requirements(campaign.participation_requirements, participant_data):
                return None

        participant = CampaignParticipant(
            campaign_id=campaign_id,
            name=participant_data.name,
            email=participant_data.email,
            whatsapp_number=participant_data.whatsapp_number,
            participant_metadata=participant_data.participant_metadata,
            status=ParticipationStatus.REGISTERED,
        )
        db.add(participant)
        db.commit()
        db.refresh(participant)
        return participant

    def get_participant(self, db: Session, participant_id: int) -> Optional[CampaignParticipant]:
        return db.query(CampaignParticipant).filter(CampaignParticipant.id == participant_id).first()

    def get_campaign_participants(self, db: Session, campaign_id: int) -> List[CampaignParticipant]:
        return db.query(CampaignParticipant).filter(
            CampaignParticipant.campaign_id == campaign_id
        ).all()

    def update_participant_status(
        self, db: Session, participant_id: int, status: ParticipationStatus
    ) -> Optional[CampaignParticipant]:
        participant = self.get_participant(db, participant_id)
        if not participant:
            return None
        participant.status = status
        db.commit()
        db.refresh(participant)
        return participant

    # --- Submissions ---

    def submit_response(
        self, db: Session, campaign_id: int, participant_id: int, submission_data: CampaignSubmissionCreate
    ) -> Optional[CampaignSubmission]:
        # Check submission deadline
        if not self.check_deadline(db, campaign_id, "submission"):
            return None

        participant = self.get_participant(db, participant_id)
        if not participant or participant.campaign_id != campaign_id:
            return None

        submission = CampaignSubmission(
            campaign_id=campaign_id,
            participant_id=participant_id,
            form_id=submission_data.form_id,
            response_data=submission_data.response_data,
        )
        db.add(submission)

        # Update participant status
        participant.status = ParticipationStatus.SUBMITTED
        db.commit()
        db.refresh(submission)
        return submission

    def get_participant_submissions(self, db: Session, participant_id: int) -> List[CampaignSubmission]:
        return db.query(CampaignSubmission).filter(
            CampaignSubmission.participant_id == participant_id
        ).all()

    # --- Results / Winners ---

    def get_campaign_results(self, db: Session, campaign_id: int):
        campaign = self.get_campaign(db, campaign_id)
        if not campaign:
            return None

        winners = db.query(CampaignParticipant).filter(
            and_(
                CampaignParticipant.campaign_id == campaign_id,
                CampaignParticipant.status == ParticipationStatus.WINNER,
            )
        ).all()

        total_participants = db.query(CampaignParticipant).filter(
            CampaignParticipant.campaign_id == campaign_id
        ).count()

        total_submissions = db.query(CampaignSubmission).filter(
            CampaignSubmission.campaign_id == campaign_id
        ).count()

        return {
            "campaign_id": campaign.id,
            "campaign_name": campaign.name,
            "winners": winners,
            "total_participants": total_participants,
            "total_submissions": total_submissions,
        }

    def select_winners_manual(self, db: Session, campaign_id: int, participant_ids: List[int]) -> List[CampaignParticipant]:
        winners = []
        for pid in participant_ids:
            participant = db.query(CampaignParticipant).filter(
                and_(
                    CampaignParticipant.id == pid,
                    CampaignParticipant.campaign_id == campaign_id,
                )
            ).first()
            if participant:
                participant.status = ParticipationStatus.WINNER
                winners.append(participant)
        db.commit()
        for w in winners:
            db.refresh(w)
        return winners

    # --- Winner Config ---

    def add_winner_config(
        self, db: Session, campaign_id: int, config_data: CampaignWinnerConfigCreate
    ) -> Optional[CampaignWinnerConfig]:
        campaign = self.get_campaign(db, campaign_id)
        if not campaign:
            return None
        config = CampaignWinnerConfig(campaign_id=campaign_id, **config_data.model_dump())
        db.add(config)
        db.commit()
        db.refresh(config)
        return config

    # --- Communications ---

    def add_communication(
        self, db: Session, campaign_id: int, comm_data: CampaignCommunicationCreate
    ) -> Optional[CampaignCommunication]:
        campaign = self.get_campaign(db, campaign_id)
        if not campaign:
            return None
        comm = CampaignCommunication(campaign_id=campaign_id, **comm_data.model_dump())
        db.add(comm)
        db.commit()
        db.refresh(comm)
        return comm

    def get_campaign_communications(self, db: Session, campaign_id: int) -> List[CampaignCommunication]:
        return db.query(CampaignCommunication).filter(
            CampaignCommunication.campaign_id == campaign_id
        ).all()

    # --- Helpers ---

    def _check_requirements(self, requirements: dict, participant_data: CampaignParticipantCreate) -> bool:
        """Validate participant against configurable requirements."""
        if requirements.get("email_required") and not participant_data.email:
            return False
        if requirements.get("whatsapp_required") and not participant_data.whatsapp_number:
            return False
        return True
