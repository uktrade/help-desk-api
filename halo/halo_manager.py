import logging
from typing import List

from halo.halo_api_client import HaloAPIClient, HaloRecordNotFoundException
from halo.interfaces import (
    HelpDeskBase,
    HelpDeskComment,
    HelpDeskException,
    HelpDeskTicket,
    HelpDeskTicketNotFoundException,
    HelpDeskUser,
    TicketType,
)


def reverse_keys(dictionary):
    return {value: key for key, value in dictionary.items()}


STATUS_MAPPING = {
    "new": 1,
    "open": 2,  # in progress
    "pending": 3,  # action requried
    "on-hold": 28,
    "solved": 18,  # approved  ???
    "closed": 9,
}

REVERSE_STATUS_MAPPING = reverse_keys(STATUS_MAPPING)
PRIORITY_MAPPING = {
    "incident": {"low": 4, "normal": 3, "high": 2, "urgent": 1},
}
REVERSE_PRIORITY_MAPPING = {key: reverse_keys(value) for key, value in PRIORITY_MAPPING.items()}
TICKET_TYPE_MAPPING = {1: TicketType.INCIDENT, 27: TicketType.INCIDENT}

logger = logging.getLogger(__name__)


class HaloManager(HelpDeskBase):
    def __init__(self, client_id, client_secret):
        """Create a new Halo client - pass credentials to.
        :TODO - correct
        """
        self.client = HaloAPIClient(
            client_id=client_id,
            client_secret=client_secret,
        )

    def get_or_create_user(self, user: HelpDeskUser = None) -> HelpDeskUser:
        """Get or Create a new Halo user.   /PS-IGNORE
        :param HelpDeskUser
                full_name: string full name for Halo user.
                email: string email address text for the Halo user.
        :returns: HelpDeskUser instance representing Halo user.
        """
        if user is not None:
            transformed_user = self.__transform_helpdesk_user_to_halo_user(user)
            if transformed_user.get("id"):
                halo_user = self.client.get(path=f"Users/{transformed_user['id']}")
                if halo_user and transformed_user.get("email"):
                    logger.error("update user")
                    halo_user = self.client.post(path="Users", payload=transformed_user)
                    logger.error(halo_user)
            else:
                halo_user = self.client.post(path="Users", payload=transformed_user)
        else:
            transformed_user = self.client.get(path="agent/me")
            halo_user = {
                "id": transformed_user["id"],
                "name": transformed_user["name"],
                "emailaddress": transformed_user["email"],
            }

        if halo_user is None:
            message = f"No Halo user found for {transformed_user}"  # Error log /PS-IGNORE,
            logger.debug(message)
            raise HelpDeskException(message)
        return self.__transform_halo_user_to_helpdesk_user(halo_user)

    def create_ticket(self, ticket: HelpDeskTicket) -> HelpDeskTicket:
        """Create a new Zendesk ticket in response to a new user question.
        :param ticket: HelpDeskTicket with information to create Zendesk ticket.
        :returns: A HelpDeskTicket instance.
        """
        halo_ticket = self.__transform_helpdesk_to_halo_ticket(ticket)

        ticket_response = self.client.post(path="Tickets", payload=[halo_ticket])

        if ticket["comment"]:
            ticket_response["comment"] = self.client.post(
                path="Actions",
                payload=[
                    self.__transform_comment_to_halo_action(
                        ticket_response["id"], ticket["comment"]
                    )
                ],
            )

        return self.__transform_object_to_helpdesk_ticket(ticket_response)

    def get_ticket(self, ticket_id: int) -> HelpDeskTicket:
        """Recover the ticket by Halo ID.
        :param ticket_id: The Halo ID of the Ticket.
        :returns: A HelpDeskTicket instance.
        :raises:
            HelpDeskTicketNotFoundException: If no ticket is found.
        """
        logger.debug(f"Look for Ticket by is Halo ID:<{ticket_id}>")  # /PS-IGNORE
        try:
            return self.__transform_object_to_helpdesk_ticket(
                self.client.get(path=f"Tickets/{ticket_id}")
            )
        except HaloRecordNotFoundException:
            message = f"Could not find Halo ticket with ID:<{ticket_id}>"  # /PS-IGNORE

            logger.debug(message)
            raise HelpDeskTicketNotFoundException(message)

    def close_ticket(self, ticket_id: int) -> HelpDeskTicket:
        """Close a ticket in Halo.
        :param ticket_id: The Halo ticket ID.
        :returns: HelpDeskTicket instance.
        """
        raise NotImplementedError()

    def add_comment(self, ticket_id: int, comment: HelpDeskComment) -> HelpDeskTicket:
        """Add a comment to an existing ticket.
        :param ticket_id: id of Halo ticket instance.
        :param comment: HelpDeskComment instance.
        :returns: The updated HelpDeskTicket instance.
        """
        raise NotImplementedError()

    def update_ticket(self, ticket: HelpDeskTicket) -> HelpDeskTicket:
        """Update an existing ticket.
        :param ticket: HelpDeskTicket ticket.
        :returns: The updated HelpDeskTicket instance.
        :raises:
            HelpDeskTicketNotFoundException: If no ticket is found.
        """
        halo_ticket = self.__transform_helpdesk_to_halo_ticket(ticket)
        if not ticket.id:
            logger.error("No ticket id")
            raise HelpDeskTicketNotFoundException("No ticket id")

        updated_ticket = self.client.post(path="Tickets", payload=[halo_ticket])
        if updated_ticket is None:
            message = f"Could not update ticket with id {ticket.id}"
            logger.error(message)
            raise HelpDeskTicketNotFoundException(message)

        if halo_ticket["comment"]:
            updated_ticket["comment"] = self.client.post(
                path="Actions", payload=[halo_ticket["comment"]]
            )

        return self.__transform_object_to_helpdesk_ticket(updated_ticket)

    def get_comments(self, ticket_id: int) -> List[HelpDeskComment]:
        # actions = self.client.get(
        #     path="Actions", params={ticket_id:ticket_id}
        # )
        raise NotImplementedError

    def __transform_comment_to_halo_action(self, ticket_id: int, comment: HelpDeskComment):
        """Transform from HelpDeskComment to halo comment format.
        :param ticket_id: id of the ticket comment
        :param comment: HelpDeskComment instance.
        :returns: halo action object.
        """
        return {
            "note": comment.body,
            "ticket_id": ticket_id,
            "hiddenfromuser": not comment.public,
            # "who_agentid": comment.author_id,
            "outcome": "comment",
        }

    def __transform_halo_action_to_comment(self, halo_comment) -> HelpDeskComment:
        """Transform from halo comment format to HelpDeskComment.
        :param halo_comment: Halo Action instance.
        :returns: halo action object.
        """
        return HelpDeskComment(
            body=halo_comment["note"],
            public=not halo_comment["hiddenfromuser"],
            author_id=halo_comment.get("who_agentid"),
        )

    def __transform_helpdesk_to_halo_ticket(self, ticket: HelpDeskTicket) -> object:
        """Transform from HelpDeskTicket to halo ticket format.
        :param ticket: HelpDeskTicket instance.
        :returns: halo ticket object.
        """
        # custom_fields = None

        ticket_user = self.get_or_create_user(ticket.user)

        # if ticket.custom_fields:
        #     custom_fields = [
        #         {'id':custom_field.id, 'value':custom_field.value}
        #         for custom_field in ticket.custom_fields
        #     ]

        return {
            "id": ticket.id,
            "status_id": STATUS_MAPPING[ticket.status] if ticket.status else None,
            "priority_id": PRIORITY_MAPPING[ticket.ticket_type][ticket.priority]
            if (ticket.ticket_type and ticket.priority)
            else None,
            # "emailcclist": [ticket.recipient_email], #correct?
            "summary": ticket.subject,
            "details": ticket.description,
            "user_id": ticket_user.id,
            "agent_id": ticket.assignee_id,
            "team_id": ticket.group_id,
            "ticket_tags": ", ".join(ticket.tags) if ticket.tags else None,
            # ticket.service_name field be determined
            "third_party_id": ticket.external_id,  # /PS-IGNORE
            # TODO 'custom_fields':custom_fields, #+ [{'id':144,'name':
            # 'CFemailAddress', 'value': ticket.recipient_email }],
            "tickettype_id": TICKET_TYPE_MAPPING[ticket.ticket_type]
            if ticket.ticket_type
            else None,
            "comment": self.__transform_comment_to_halo_action(ticket.id, ticket.comment)
            if ticket.id and ticket.comment
            else None,
            "category_1": "Standard Applications>Adobe",
        }

    def __transform_object_to_helpdesk_ticket(self, ticket: object) -> HelpDeskTicket:
        """Transform Halo ticket object into HelpDeskTicket instance.
        :param ticket: Halo ticket object.
        :returns: HelpDeskTicket instance.
        """
        ticket_user, comment = None, None

        if ticket.get("user"):
            ticket_user = HelpDeskUser(
                id=ticket["user"]["id"],
                full_name=ticket["user"]["name"],
                email=ticket["user"]["emailaddress"],
            )
        elif ticket.get("user_id"):
            ticket_user = HelpDeskUser(id=ticket["user_id"])

        # if getattr(ticket, "custom_fields", None):
        #     custom_fields = [
        #         HelpDeskCustomField(id=custom_field.id, value=custom_field.value)
        #         for custom_field in ticket.custom_fields
        #     ]

        # Get ticket comments if comments set latest comment
        ticket_actions = self.client.get(f"Actions?ticket_id={ticket['id']}")
        for action in reversed(ticket_actions["actions"]):
            if action["outcome"] == "comment":
                comment = self.__transform_halo_action_to_comment(action)

        helpdesk_ticket = HelpDeskTicket(
            id=ticket["id"],
            status=REVERSE_STATUS_MAPPING[ticket["status_id"]] if ticket.get("status_id") else None,
            subject=ticket["summary"],
            description=ticket.get("details", None),
            # recipient_email=getattr(ticket, "recipient", None),
            user=ticket_user,
            created_at=ticket.get("dateoccurred"),
            updated_at=ticket.get("flastupdate"),
            priority=REVERSE_PRIORITY_MAPPING[TICKET_TYPE_MAPPING[ticket["tickettype_id"]].value][
                ticket.get("priority_id")
            ],
            due_at=ticket.get("deadlinedate", None),
            assignee_id=ticket.get("agent_id", None),
            group_id=ticket.get("team_id", None),
            external_id=ticket.get("third_party_id", None),  # /PS-IGNORE
            tags=(ticket.get("ticket_tags", [])).split(", "),
            # custom_fields=custom_fields,
            comment=comment,
            ticket_type=TICKET_TYPE_MAPPING[ticket["tickettype_id"]]
            if ticket.get("tickettype_id")
            else None,
        )
        return helpdesk_ticket

    def __transform_helpdesk_user_to_halo_user(self, user: HelpDeskUser) -> object:
        """Transform HelpDesk user into Halo user object.
        :param user: HelpDeskUser instance.
        :returns: Halo User object.
        """
        if user and (user.id or user.email):
            return {"id": user.id, "name": user.full_name, "emailaddress": user.email}
        else:
            # This should not be possible so raise exception
            raise HelpDeskException(
                "Cannot transform user to Halo user",
            )

    def __transform_halo_user_to_helpdesk_user(self, user: object) -> HelpDeskUser:
        """Transform Halo user object into HelpDesk user instance.
        :param user: Halo user object
        :returns: HelpDeskUser user instance.
        """
        return HelpDeskUser(id=user["id"], full_name=user["name"], email=user["emailaddress"])
