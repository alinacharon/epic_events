from sqlalchemy.orm import sessionmaker, joinedload

from config import engine
from models import Event, User, Role


class EventManager:
    def __init__(self):
        self.Session = sessionmaker(bind=engine)

    def add_event(self, event_data, session):
        # Validate dates
        if event_data['end_date'] < event_data['start_date']:
            raise ValueError("La date de fin ne peut pas être antérieure à la date de début.")

        # Create and validate the event
        event = Event(**event_data)
        session.add(event)
        return event

    def get_all_events(self):
        """Get all events."""
        with self.Session() as session:
            return session.query(Event).all()

    def get_event_by_id(self, event_id):
        """Get an event by its ID."""
        with self.Session() as session:
            return session.query(Event).options(joinedload(Event.contract)).get(event_id)

    def get_events_by_client(self, client_id):
        """Get all events for a specific client."""
        with self.Session() as session:
            return session.query(Event).filter(Event.client_id == client_id).all()

    def get_events_by_support(self, support_contact_id):
        """Get all events assigned to a specific support contact."""
        with self.Session() as session:
            return session.query(Event).filter(
                Event.support_contact_id == support_contact_id
            ).all()

    def get_unassigned_events(self):
        """Get all events without an assigned support contact."""
        with self.Session() as session:
            return session.query(Event).filter(
                Event.support_contact_id == None
            ).all()

    def get_assigned_events(self):
        """Get all events without an assigned support contact."""
        with self.Session() as session:
            return session.query(Event).filter(
                Event.support_contact_id != None
            ).all()

    def update_event(self, event_id, updated_data):
        """Update an existing event."""
        with self.Session() as session:
            event = session.query(Event).get(event_id)
            if not event:
                return False

            # Validate dates if they are being updated
            if 'start_date' in updated_data or 'end_date' in updated_data:
                start_date = updated_data.get('start_date', event.start_date)
                end_date = updated_data.get('end_date', event.end_date)
                if end_date < start_date:
                    raise ValueError("La date de fin ne peut pas être antérieure à la date de début.")

            # Update fields
            for key, value in updated_data.items():
                if value is not None:
                    setattr(event, key, value)

            session.commit()
            return True

    def assign_support_to_event(self, event_id, support_id):
        """Assign a support employee to an event."""
        with self.Session() as session:
            event = session.query(Event).get(event_id)
            if not event:
                raise ValueError("Événement non trouvé")

            support_user = session.query(User).filter(
                User.id == support_id,
                User.role == Role.SUPPORT
            ).first()
            if not support_user:
                raise ValueError("Employé support non trouvé")

            event.support_contact_id = support_id
            session.commit()
            return True
