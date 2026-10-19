"""EPP response codes.
Copied from the abandoned https://pypi.python.org/pypi/EPP package
"""

XMLNS = {
    # Possible namespaces in the response
    # See greeting message for all possible supported extensions
    # Base:
    "epp": "urn:ietf:params:xml:ns:epp-1.0",  # Base EPP; https://www.rfc-editor.org/info/rfc5730
    "obj": "urn:ietf:params:xml:ns:obj-1.0",  # Base EPP; https://www.rfc-editor.org/info/rfc5730
    "domain": "urn:ietf:params:xml:ns:domain-1.0",  # Domain name mapping; https://www.rfc-editor.org/info/rfc5731
    "host": "urn:ietf:params:xml:ns:host-1.0",  # Host mapping; https://www.rfc-editor.org/info/rfc5732
    "contact": "urn:ietf:params:xml:ns:contact-1.0",  # Contact mapping; https://www.rfc-editor.org/info/rfc5733
    # IETF extensions:
    "secDNS": "urn:ietf:params:xml:ns:secDNS-1.1",  # DNSSec; https://www.rfc-editor.org/info/rfc5910
    "org": "urn:ietf:params:xml:ns:epp:org-1.0",  # Organization mappings; https://www.rfc-editor.org/info/rfc8543/
    "orgext": "urn:ietf:params:xml:ns:epp:orgext-1.0",  # Organization extensions; https://www.rfc-editor.org/info/html/rfc8544
    "rgp": "urn:ietf:params:xml:ns:rgp-1.0",  # Redemption Grace Period https://www.rfc-editor.org/info/rfc3915/
    "fee": "urn:ietf:params:xml:ns:fee-0.11",  # Registar fees https://www.rfc-editor.org/info/rfc8748/
    "xmldsig": "http://www.w3.org/2000/09/xmldsig#",  # Signatures https://www.w3.org/TR/xmldsig-core/
    "launch": "urn:ietf:params:xml:ns:launch-1.0",  # Launch phase; https://www.rfc-editor.org/info/rfc8334/
    "mark": "urn:ietf:params:xml:ns:mark-1.0",  # Trademarks https://www.rfc-editor.org/info/rfc7848/
    "smd": "urn:ietf:params:xml:ns:signedMark-1.0",  # Signed Trademarks https://www.rfc-editor.org/info/rfc7848/
    # Fury extensions:
    "fury": "urn:ietf:params:xml:ns:fury-2.0",  # Fury extension; https://www.cira.ca/en/resources/documents/registry/cira-fury-21-epp-extension/
    "fury-rgp": "urn:ietf:params:xml:ns:fury-rgp-1.0",  # Fury Redemption Grace Period extension https://www.cira.ca/en/resources/documents/registry/cira-fury-rgp-1-epp-extension
    "idn": "urn:ietf:params:xml:ns:idn-1.0",  # Internationalized Domain names; https://www.cira.ca/en/resources/documents/registry/cira-idn-1-epp-extension/
}

# Command completed successfully
EPP_OK = 1000

# Command completed successfully; action pending
EPP_OK_PENDING = 1001

# Command completed successfully; no messages
EPP_QUEUE_EMPTY = 1300

# Command completed successfully; ack to dequeue
EPP_QUEUE_NOT_EMPTY = 1301

EPP_LOGOUT_OK = 1500

# command element that is not defined by EPP
EPP_UNKNOWN_CMD = 2000

# improperly formed command element
EPP_CMD_SYNTAX = 2001

# properly formed command element but the command cannot be executed
# due to a sequencing or context error, e.g. <logout> before <login>
EPP_CMD_USE = 2002

# command for which a required parameter value has not been provided
EPP_PARAM_MISSING = 2003

# command parameter whose value is outside the range of values specified by the protocol.
# The error value SHOULD be returned via a <value> element in the EPP response
EPP_PARAM_VALUE_RANGE = 2004

# command containing a parameter whose value is improperly formed.
# The error value SHOULD be returned via a <value> element in the EPP response
EPP_PARAM_VALUE_SYNTAX = 2005

# command element specifying a protocol version that is not implemented by the server.
EPP_UNIMPLEMENTED_PROTO_VER = 2100

# valid EPP command element that is not implemented by the server.
EPP_UNIMPLEMENTED_COMMAND = 2101

# valid EPP command element that contains a protocol option that is not implemented by the server
EPP_UNIMPLEMENTED_OPTION = 2102

# valid EPP command element that contains a protocol command extension that is not implemented by the server
EPP_UNIMPLEMENTED_EXTENSION = 2103

# attemps to execute a billable operation and the command cannot be completed due to a client-billing failure.
EPP_BILLING_FAIL = 2104

# object that is not eligible for renewal in accordance with server policy
EPP_INELIGIBLE_RENEW = 2105

# object that is not eligible for transfer in accordance with server policy
EPP_INELIGIBLE_TRANSFER = 2106

# error when validating client credentials
EPP_AUTHN_ERROR = 2200

# client-authorization error when executing a command. This error
# is used to note that a client lacks privileges to execute the requested command
EPP_AUTHORIZATION_ERROR = 2201

# invalid command authorization information when attempting
# to confirm authorization to execute a command.  This error
# is used to note that a client has the privileges required
# to execute the requested command, but the authorization
# information provided by the client does not match the
# authorization information archived by the server
EPP_INVALID_AUTH_INFO = 2202

# command to transfer an object that is pending transfer due to an earlier transfer request
EPP_OBJECT_PENDING_XFR = 2300

# received command to confirm, reject, or cancel the transfer of an
# object when no command has been made to transfer the object.
EPP_OBJECT_NOT_PENDING_XFR = 2301

# command to create an object that already exists in the repository
EPP_OBJECT_EXISTS = 2302

# command to query or transform an object that does not exist in the repository
EPP_OBJECT_DOES_NOT_EXIST = 2303

# command to transform an object that cannot be completed
# due to server policy or business practices.
EPP_OBJECT_STATUS = 2304

# command to transform an object that cannot be completed
# due to dependencies on other objects that are associated
# with the target object.
EPP_OBJECT_ASSOC = 2305

# command containing a parameter value that is syntactically valid
# but semantically invalid due to local policy.
# The error value SHOULD be returned via a <value> element in the EPP response.
EPP_PARAM_VALUE_POLICY = 2306

# a command to operate on an object service that is not supported by the server
EPP_UNIMPLEMENTED_OBJ_SVC = 2307

# command whose execution results in a violation of server data management policies
EPP_DATA_MGMT_POLICY = 2308

# unable to execute a command due to an internal server error
# that is not related to the protocol. The failure can be transient.
EPP_FAILED = 2400

# command that cannot be completed due to an internal server error
# that is not related to the protocol. The failure is not transient
# and will cause other commands to fail as well.
# The server MUST end the active session and close the existing connection.
EPP_FAILED_CLOSING = 2500

# error when validating client credentials and
# a server-defined limit on the number of allowable failures has been exceeded.
# The server MUST close the existing connection.
EPP_AUTH_FAILED_CLOSING = 2501

# <login> command that cannot be completed because the client has exceeded
# a system-defined limit on the number of sessions that the client can establish.
# It might be possible to establish a session by ending existing unused sessions
# and closing inactive connections.
EPP_AUTH_SESSION_LIMIT = 2502


# ---- extended codes by SIDN ----

# The specified domain name is not managed by you.
SIDN_EXT_NOT_MANAGED_BY_ACCOUNT = "C0038b"  # for 2308 (EPP_DATA_MGMT_POLICY)

# The specified token did not originate from the specified domain name.
SIDN_EXT_TRANSFER_TOKEN_INVALID = "C0098a"  # for 2308 (EPP_DATA_MGMT_POLICY)

# No transfers are recorded for this domain name.
SIDN_EXT_NO_XFR_RECORDED = "C0100"  # for 2301 (EPP_OBJECT_NOT_PENDING_XFR)

# The specified handle is not associated with this account.
SIDN_EXT_HANDLE_NOT_ASSOCIATED = "C0115"

# The specified domain name is unknown.
SIDN_EXT_DOMAIN_DOES_NOT_EXIST = "T0001"  # for 2303 (EPP_OBJECT_DOES_NOT_EXIST)
