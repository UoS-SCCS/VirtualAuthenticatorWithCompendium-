"""Listener abstract class

This needs to be in its only module due to issues
with circular references
"""
"""
 © Copyright 2020-2021 University of Surrey

 Redistribution and use in source and binary forms, with or without
 modification, are permitted provided that the following conditions are met:

 1. Redistributions of source code must retain the above copyright notice,
 this list of conditions and the following disclaimer.

 2. Redistributions in binary form must reproduce the above copyright notice,
 this list of conditions and the following disclaimer in the documentation
 and/or other materials provided with the distribution.

 THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
 LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
 CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
 SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
 CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 POSSIBILITY OF SUCH DAMAGE.

"""
from abc import ABC, abstractmethod
from hid.packets import HIDPacket
from ctap.transaction import CTAPHIDTransaction
class USBHIDListener(ABC):
    """Abstract listener class to receive packets and
    notifications of when packets have been written.

    """
    @abstractmethod
    def received_packet(self, packet:HIDPacket):
        """Fired when an HIDPacket has been received

        Args:
            packet (HIDPacket): packet that has been received
        """

    @abstractmethod
    def response_sent(self, transaction:CTAPHIDTransaction):
        """Fired when the response has been set indicating the
        transaction is now complete

        Args:
            transaction (CTAPHIDTransaction): transaction from which
                the response was sent
        """
