from zope.interface import (
    Attribute,
    Interface,
    )


class IAuthSourceService(Interface):
    """ Represents an authentication source. """

    vary = Attribute("List of HTTP headers to Vary the response by.")

    def get_value():
        """ Returns the opaque value that was stored. """

    def headers_remember(value):
        """ Returns any and all headers for remembering the value, as a list.
        Value is a standard Python type that shall be serializable using
        JSON. """

    def headers_forget():
        """ Returns any and all headers for forgetting the current requests
        value. """


class IAuthService(Interface):
    """ Represents an authentication service. This service verifies that the
    users authentication ticket is valid and returns groups the user is a
    member of. """

    def userid():
        """ Return the current user id, None, or raise an error. Raising an
        error is used when no attempt to verify a ticket has been made yet and
        signifies that the authentication policy should attempt to call
        ``verify_ticket``"""

    def groups():
        """ Returns the groups for the current user, as a list. Including the
        current userid in this list is not required, as it will be implicitly
        added by the authentication policy. """

    def verify_ticket(principal, ticket):
        """ Verify that the principal matches the ticket given. """

    def add_ticket(principal, ticket):
        """ Add a new ticket for the principal. If there is a failure, due to a
        missing/non-existent principal, or failure to add ticket for principal,
        should raise an error """

    def remove_ticket(ticket):
        """ Remove a ticket for the current user. Upon success return True """
