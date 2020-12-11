"""Contains classes and Enums for managing transactions

"""
from enum import Enum, unique
import logging
import json
import ctap.constants
from ctap.exceptions import TransactionStateException, TransactionChannelIDException
from ctap.messages import CTAPHIDCMD, CTAPHIDCancelResponse, CTAPHIDErrorResponse

log = logging.getLogger('debug')
ctaplog = logging.getLogger('debug.ctap')

@unique
class TRANSACTION_STATE(Enum):
    """Enum that holds the transaction state

    """
    EMPTY = 0
    REQUEST_RECV = 1
    RESPONSE_SET = 2
    CANCEL = 8
    ERROR = 9

class CTAPHIDTransaction:
    """Transaction class the enforces and hold the request-response
    messages associated with a CTAP transaction
    """
    def __init__(self, channel_id:bytes):
        """Instantiates a new instance associated with the specified channel

        Args:
            channel_id (bytes): channel id bytes
        """
        self.request = None
        self.response = None
        self.state = TRANSACTION_STATE.EMPTY
        self.channel_id = channel_id

    def get_cid(self)->bytes:
        """Gets the channel id associated with this transaction

        Returns:
            bytes: channel id bytes
        """
        return self.channel_id
    def is_error_transaction(self)->bool:
        """Checks whether this is a special error transaction
        that may not have a corresponding request

        Returns:
            bool: True if it is an error transaciton, False if not
        """
        return self.state == TRANSACTION_STATE.ERROR

    def __str__(self):
        out = {}
        if self.request is None:
            out["request"]=None
        else:
            out["request"]=json.loads(self.request.__str__())
        if self.response is None:
            out["response"]=None
        else:
            out["response"]= json.loads(self.response.__str__())
        out["state"]=self.state.name
        out["channel_id"] = self.channel_id.hex()
        return json.dumps(out)

    def set_request(self, request: CTAPHIDCMD):
        """Sets the request part of this transaction

        Args:
            request (CTAPHIDCMD): request to be set

        Raises:
            TransactionStateException: thrown if transaction is in an
                invalid state to receive a request
            TransactionChannelIDException: thrown if the request does not
                match the transaction channel id
        """
        if not self.verify_state(TRANSACTION_STATE.REQUEST_RECV):
            ctaplog.error("Invalid state in transaction to set request, current state: %s",
                self.state )
            raise TransactionStateException("Invalid state, cannot set request")
        if (request.get_cid() != ctap.constants.BROADCAST_ID and
        request.get_cid() != self.channel_id):
            raise TransactionChannelIDException("Invalid channel ID for transaction")
        self.state = TRANSACTION_STATE.REQUEST_RECV
        self.request = request
        ctaplog.debug("Set request, changed state: %s", self.state )

    def set_response(self, response: CTAPHIDCMD):
        """Sets the response part of the transaction

        Args:
            response (CTAPHIDCMD): response to set

        Raises:
            TransactionStateException: thrown if transaction is in an
                invalid state to receive a response
            TransactionChannelIDException: thrown if the response does not
                match the transaction channel id
        """
        if not self.verify_state(TRANSACTION_STATE.RESPONSE_SET):
            ctaplog.error("Invalid state in transaction to set response, current state: %s",
                self.state )
            raise TransactionStateException("Invalid state, cannot set response")
        if (response.get_cid() != ctap.constants.BROADCAST_ID and
        response.get_cid() != self.channel_id):
            raise TransactionChannelIDException("Invalid channel ID for transaction")
        self.state = TRANSACTION_STATE.RESPONSE_SET
        self.response = response
        ctaplog.debug("Set response, changed state: %s", self.state )

    def reset(self):
        """Resets the transaction clearling request, response and state
        """
        self.request = None
        self.response = None
        self.state = TRANSACTION_STATE.EMPTY

    def cancel(self, response: CTAPHIDCancelResponse):
        """Cancels the request by setting the state to cancel and
        setting the response to cancel

        Args:
            response (CTAPHIDCancelResponse): cancel response to send
        """
        self.reset()
        self.state = TRANSACTION_STATE.CANCEL
        self.response = response

    def error(self, response: CTAPHIDErrorResponse):
        """Sets the transaction to an error state and sets an error
        response to be sent

        Args:
            response (CTAPHIDErrorResponse): error response to send
        """
        self.state = TRANSACTION_STATE.ERROR
        self.response = response


    def verify_state(self, target_state: TRANSACTION_STATE):
        """Verifies the state machine of the CTAP HID Transaction.

        If a request has been received it must be followed by a response being
        sent before the next request can be received.

        Parameters
        ----------
        target_state : TRANSACTION_STATE
            Enum of target transaction state

        Returns
        -------
        bool
            True if valid, False if not
        """
        return (target_state.value == (self.state.value + 1) and
            target_state.value <= TRANSACTION_STATE.RESPONSE_SET.value)