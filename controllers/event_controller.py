from models import EventManager, Role
from models.managers.contract_manager import ContractManager

from models import UserManager
from views.client_view import ClientView
from views.contract_view import ContractView
from views.event_view import EventView
from views.main_view import MainView
from views.user_view import UserView


class EventController:

    def __init__(self, user, db):
        self.event_manager = EventManager()
        self.user_manager = UserManager() 
        self.user = user
        self.db = db

    # MANAGEMENT TEAM
    def event_management_menu(self):
        """Unified event management menu for the MANAGEMENT role with filtering options."""
        while True:
            choice = EventView.management_events_menu()
            match choice:
                case "1":
                    self.list_all_events()
                case "2":
                    filter_choice = EventView.filter_events_menu()
                    match filter_choice:
                        case "1":
                            self.show_unassigned_events()
                        case "2":
                            self.show_events_by_client()
                        case "b":
                            break
                        case _:
                            MainView.print_invalid_input()

                case "3":
                    self.assign_support()
                case "b":
                    break
                case "q":
                    MainView.print_exit()
                    exit()
                case _:
                    MainView.print_invalid_input()
                    continue

    # SUPPORT TEAM
    def event_support_menu(self):
        """Event management submenu for the Support role."""
        while True:
            choice = EventView.support_events_menu()
            match choice:
                case "1":
                    self.show_assigned_events()
                case "2":
                    self.update_events()
                case "3":
                    self.get_my_events()
                case "b":
                    break
                case "q":
                    MainView.print_exit()
                    exit()
                case _:
                    MainView.print_invalid_input()

    # COMMERCIAL TEAM 
    def commercial_event_menu(self):
        """Event management submenu for the Commercial role."""
        while True:
            event_choice = EventView.commercial_events_menu()
            match event_choice:
                case "1":
                    self.create_event_for_signed_client()
                case "2":
                    self.list_all_events()
                case "3":
                    self.get_my_events()
                case "b":
                    break
                case "q":
                    MainView.print_exit()
                    exit()
                case _:
                    MainView.print_invalid_input()

    # ALL FUNCTIONS
    def create_event_for_signed_client(self):
        """Создать новое событие для клиента с подписанным контрактом."""
        if self.user.role != Role.COMMERCIAL:
            MainView.print_error(
                "Accès refusé. Seuls les commerciaux peuvent créer des événements.")
            return

        contract_id = ContractView.get_contract_id()
        contract_manager = ContractManager()
        contract = contract_manager.get_contract_by_id(contract_id)

        if not contract or not contract.signed: 
            MainView.print_error("Le contrat n'est pas signé ou introuvable.")
            return

        MainView.print_success(f"Contrat trouvé ! Nom de l'entreprise : {contract.client.company_name}")
        try:
            event_data = EventView.get_event_data()
            event_data['contract_id'] = contract_id
            event_data['client_id'] = contract.client_id

           
            new_event = self.event_manager.add_event(event_data)
              
            MainView.print_success(f"Nouvel événement créé avec succès. ID: {new_event.id}")
            return new_event
        except ValueError as e:
            MainView.print_error(
                f"Erreur lors de la création de l'événement: {e}")

    def list_all_events(self):
        """List all events - accessible to all users."""
        try:
            events = self.event_manager.get_all_events()
            EventView.display_event_list(events)
        except Exception as e:
            MainView.print_error(
                f"Erreur lors de la récupération des événements: {e}")

    def update_events(self):
        """Update an existing event."""
        try:
            event_id = EventView.get_event_id()
            existing_event = self.event_manager.get_event_by_id(event_id)

            if not existing_event:
                MainView.print_error(f"Événement avec ID {
                event_id} introuvable.")
                return

            # Check if user has permission to modify the event
            if self.user.role != Role.MANAGEMENT or existing_event.creator_id != self.user.id:
                MainView.print_error(
                    "Vous n'avez pas les droits pour modifier cet événement.")
                return

            EventView.display_event_details(existing_event)
            updated_data = EventView.get_updated_event_data()
            updated_event = self.event_manager.update_event(
                event_id, updated_data)

            if updated_event:
                MainView.print_success(
                    "Les informations de l'événement ont été mises à jour.")
                EventView.display_event_details(updated_event)
            else:
                MainView.print_error("Échec de la mise à jour de l'événement.")
        except ValueError as e:
            MainView.print_error(f"Erreur lors de la mise à jour: {e}")
        except Exception as e:
            MainView.print_error(f"Une erreur inattendue est survenue: {e}")

    def get_my_events(self):
        """Получить события, назначенные текущему пользователю."""
        try:
            if self.user is None:
                MainView.print_error("Utilisateur non connecté.")
                return

            if self.user.role == Role.SUPPORT:
                events = self.event_manager.get_events_by_support(self.user.id)
            elif self.user.role == Role.COMMERCIAL:
                events = self.event_manager.get_events_by_commercial(self.user.id)
            else:
                MainView.print_error("Rôle non autorisé pour cette opération.")
                return

            if events:
                EventView.display_event_list(events)
            else:
                MainView.print_info("Aucun événement trouvé.")
        except Exception as e:
            MainView.print_error(
                f"Erreur lors de la récupération des événements: {e}")

    def show_unassigned_events(self):
        """Show events without assigned support."""
        try:
            events = self.event_manager.get_unassigned_events()
            EventView.display_event_list(events)
        except Exception as e:
            MainView.print_error(
                f"Erreur lors de la récupération des événements: {e}")

    def show_assigned_events(self):
        """Show events without assigned support."""
        try:
            events = self.event_manager.get_assigned_events()
            EventView.display_event_list(events)
        except Exception as e:
            MainView.print_error(
                f"Erreur lors de la récupération des événements: {e}")

    def assign_support(self):
        """Назначить сотрудника поддержки на событие."""
        try:
            events = self.event_manager.get_unassigned_events()
            if not events:
                MainView.print_info("Aucun événement sans support trouvé.")
                return

            EventView.display_event_list(events)

            support_users = self.user_manager.get_support_users()
            if not support_users:
                MainView.print_error("Aucun employé support trouvé.")
                return

            UserView.display_users_list(support_users)

            event_id, support_id = EventView.get_support_assignment_data()
            
            support_user = self.user_manager.get_user_by_id(support_id)
            if not support_user or support_user.role != "SUPPORT":
                MainView.print_error("L'utilisateur sélectionné n'est pas un employé support.")
                return

            updated_event = self.event_manager.assign_support_to_event(event_id, support_id)
            if updated_event:
                MainView.print_success(f"Succès : événement ID:{event_id} assigné au Support ID:{support_id}")
            else:
                MainView.print_error("Échec de l'attribution du support.")
        
        except ValueError as e:
            MainView.print_error(f"Erreur de saisie: {e}")
        except Exception as e:
            MainView.print_error(f"Une erreur est survenue: {e}")


    def show_events_by_client(self):
        """Show events filtered by client."""
        try:
            client_id = ClientView.get_client_id()
            events = self.event_manager.get_events_by_client(client_id)
            EventView.display_event_list(events)
        except Exception as e:
            MainView.print_error(
                f"Erreur lors de la récupération des événements: {e}")
