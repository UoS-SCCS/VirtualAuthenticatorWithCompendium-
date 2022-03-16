"""Provides abstract and concrete UI classes

An abstract UI is defined that can be provided by either a CLI
interface or a QT interface. Both examples are provided

Classes:

 * :class:`DICEAuthenticatorListener`
 * :class:`DICEAuthenticatorUI`
 * :class:`ConsoleAuthenticatorUI`
 * :class:`QTAuthenticatorUI`

"""
"""
 © Copyright 2020-2022 University of Surrey

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
from email import message
import sys
from abc import ABC, abstractmethod
from enum import Enum, unique
import os
import time
import threading
import json
import random
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QWidgetAction,QLabel,QApplication,
    QSystemTrayIcon, QMenu, QVBoxLayout, QFrame, QHBoxLayout, QCheckBox,
    QAction, QDialog,QPushButton, QDesktopWidget, QGraphicsDropShadowEffect,
    QLineEdit)
from PyQt5.QtCore import QObject, Qt, QEvent, QTimer, pyqtSlot, pyqtSignal
from compendium.client import Compendium
from compendium.utils import B64

from authenticator.preferences import DICEPreferences
result_available = threading.Event()
result = None
class DICEAuthenticatorListener(ABC):
    """Defines the listener interface for authenticators
    that wish to listen to UI events
    """
    @abstractmethod
    def shutdown(self):
        """Fired when the application should shutdown, could
        be triggered by entering a Quit command on the CLI or
        clicking a menu
        """

    @abstractmethod
    def menu_clicked(self, menu_item:str):
        """Fired when a menu selection is made with the menu item
        included

        Args:
            menu_item (str): menu item that was selected
        """

    def post_ui_load(self):
        """Fired when the UI has finished loading
        """

class DICEAuthenticatorUI(ABC):
    """Abstract UI class that should be implemented by a
    compatible UI

    """
    def __init__(self):
        self._listeners = []


    @abstractmethod
    def start(self):
        """Called to start the UI. This is necessary where the
        UI will run either in the main thread or a new thread
        """

    def add_listener(self, listener:DICEAuthenticatorListener):
        """Adds a listener to receive UI events

        Args:
            listener (DICEAuthenticatorListener): listener to be added
        """
        self._listeners.append(listener)

    @abstractmethod
    def check_user_presence(self, msg:str=None):
        """Performs a user presence check. How this is performed
        is left up to the UI, it could be pop-up, notifiaction
        or some other interface

        Args:
            msg (str, optional): The notification message to show
            if not just a default. Defaults to None.
        """

    @abstractmethod
    def get_user_password(self, msg:str=None):
        """Requests a password from the user

        Args:
            msg (str, optional): The notification message to show
            if not just a default. Defaults to None.
        """

    @abstractmethod
    def check_user_verification(self, msg:str=None):
        """Performs a user verification test

        Args:
            msg (str, optional): The notification message to show
            if not just a default. Defaults to None.
        """
    @abstractmethod
    def create(self):
        """Creates the UI but doesn't show it yet
        """

    @abstractmethod
    def shutdown(self):
        """Requests the UI to initiate a shutdown, equivalent to exit in the UI
        """
    def fire_event_shutdown(self):
        """Fires the shutdown event to all listeners
        """
        for listener in self._listeners:
            listener.shutdown()

    def fire_menu_clicked(self, menu_item:str):
        """Fires the menu clicked event

        Args:
            menu_item (str): menu item that was clicked
        """
        for listener in self._listeners:
            listener.menu_clicked(menu_item)

    def fire_post_ui_loaded(self):
        """Fires the menu clicked event

        Args:
            menu_item (str): menu item that was clicked
        """
        time.sleep(0.05)
        for listener in self._listeners:
            listener.post_ui_load()

class ConsoleAuthenticatorUI(DICEAuthenticatorUI):
    """Simple console UI to allow the user to perform
    basic operations like quiting.

    """
    def __init__(self):
        super().__init__()
        self.type="Console"

    def start(self):
        while 1:
            for line in sys.stdin:
                if line.rstrip() == "quit":
                    #This doesn't actually kill the thread because
                    #python handles threads in a slightly odd way
                    self.fire_event_shutdown()
                    sys.exit()
                else:
                    print("Unknown command entered on CLI: %s" % line.rstrip() )

    def check_user_presence(self, msg:str=None):
        pass

    def get_user_password(self, msg:str=None):
        pass

    def check_user_verification(self, msg:str=None):
        pass

    def create(self):
        pass

    def shutdown(self):
        self.fire_event_shutdown()
        sys.exit(0)

@unique
class DICE_UI_Event(Enum):
    """Enum to define different event types in the DICE app

    """
    SHOW_UP = QEvent.Type(QEvent.registerEventType())
    SHOW_UV = QEvent.Type(QEvent.registerEventType())
    CHECK_UV = QEvent.Type(QEvent.registerEventType())
    SHOW_PWD = QEvent.Type(QEvent.registerEventType())
class DICEEvent(QEvent):
    """Holds a DICE Event that represents one of the types
    and potentially includes a message as well

    """
    def __init__(self,action:DICE_UI_Event):
        QEvent.__init__(self, action.value)
        self.dice_type = action
        self.msg = ""
    def set_message(self, msg:str):
        """Sets the underlying message for this event

        Args:
            msg (str): Message for this event
        """
        self.msg = msg

class QTAuthenticatorUIApp(QApplication):
    """QT5 UI with system tray icon

    """
    def __init__(self):
        super().__init__([])
        self.pwd_box = None
        self.dialog = None
        self.pwd_box_uv = None
    def customEvent(self, event):
        """Processes the custom event firing

        Args:
            event (DICEevent): event that has been fired
        """

        if event.dice_type == DICE_UI_Event.SHOW_UP:
            self.show_user_presence(event.msg)
        if event.dice_type == DICE_UI_Event.SHOW_PWD:
            self.get_user_password(event.msg)
        if event.dice_type == DICE_UI_Event.SHOW_UV:
            self.get_user_verification(event.msg)
        if event.dice_type == DICE_UI_Event.CHECK_UV:
            self.register_for_user_verification()




    def show_user_presence(self, msg:str="User Presence Check"):
        """Shows the user presence check dialog

        Args:
            msg (str, optional): The message to show the user in dialog.
                Defaults to "User Presence Check".
        """
        self.dialog = QDialog(flags = Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.dialog.setAttribute(Qt.WA_TranslucentBackground)
        parent_path = os.path.dirname(os.path.abspath(__file__))
        outer_layout = QVBoxLayout(self.dialog)
        outer_layout.setContentsMargins(0,0,0,0)
        outer_frame = QFrame()

        outer_frame.setProperty("bgFrame",True)
        outer_frame.setStyleSheet("#header {font-weight:bold; text-align:center;}\n\
        *[bgFrame='true'] {border-image: url(" + parent_path +"/icons/bgpy.png" +")\
             0 0 0 0 stretch stretch;}")

        outer_layout.addWidget(outer_frame)
        layout = QVBoxLayout(outer_frame)
        header = QLabel("DICE Key Notification");
        header.setObjectName("header")
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        label = QLabel(msg)
        label.setWordWrap(True)
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        frame = QFrame()
        blayout = QHBoxLayout(frame)
        allow_button = QPushButton("Allow")
        deny_button = QPushButton("Deny")
        allow_button.clicked.connect(lambda:self._perm_button_clicked(True))
        deny_button.clicked.connect(lambda:self._perm_button_clicked(False))
        blayout.addWidget(allow_button)
        blayout.addWidget(deny_button)
        frame.setLayout(blayout)
        layout.addWidget(frame)
        outer_frame.setLayout(layout)
        self.dialog.setLayout(outer_layout)


        screen_shape = QDesktopWidget().screenGeometry()
        self.dialog.setGeometry(screen_shape.width()-440,0,350,200)
        self.dialog.show()

    def get_user_password(self, msg:str="Enter Password"):
        """Shows the user password dialog

        Args:
            msg (str, optional): The message to show the user in the dialog.
                Defaults to "Enter Password".
        """
        self.dialog = QDialog(flags = Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.dialog.setAttribute(Qt.WA_TranslucentBackground)
        parent_path = os.path.dirname(os.path.abspath(__file__))
        outer_layout = QVBoxLayout(self.dialog)
        outer_layout.setContentsMargins(0,0,0,0)
        outer_frame = QFrame()

        outer_frame.setProperty("bgFrame",True)
        outer_frame.setStyleSheet("#header {font-weight:bold; text-align:center;}\n\
        *[bgFrame='true'] {border-image: url(" + parent_path +"/icons/bgpy.png" +")\
            0 0 0 0 stretch stretch;}")
        outer_layout.addWidget(outer_frame)
        layout = QVBoxLayout(outer_frame)
        header = QLabel("DICE Key Notification");
        header.setObjectName("header")
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        label = QLabel(msg)
        label.setWordWrap(True)
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        frame = QFrame()
        blayout = QHBoxLayout(frame)
        self.pwd_box = QLineEdit()
        self.pwd_box.setEchoMode(QLineEdit.Password)
        blayout.addWidget(self.pwd_box)
        submit_button = QPushButton("Submit")
        submit_button.clicked.connect(self._submit_pwd_button_clicked)
        blayout.addWidget(submit_button)
        frame.setLayout(blayout)
        layout.addWidget(frame)
        outer_frame.setLayout(layout)
        self.dialog.setLayout(outer_layout)


        screen_shape = QDesktopWidget().screenGeometry()

        self.pwd_box.setFocus()
        self.dialog.setGeometry(screen_shape.width()-440,0,350,200)
        self.dialog.show()

    def get_user_verification(self, msg:str="Enter Password"):
        """Shows the user verification dialog

        Args:
            msg (str, optional): Message to show the user in the dialog.
                Defaults to "Enter Password".
        """
        self.dialog = QDialog(flags = Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.dialog.setAttribute(Qt.WA_TranslucentBackground)
        parent_path = os.path.dirname(os.path.abspath(__file__))
        outer_layout = QVBoxLayout(self.dialog)
        outer_layout.setContentsMargins(0,0,0,0)
        outer_frame = QFrame()

        outer_frame.setProperty("bgFrame",True)
        outer_frame.setStyleSheet("#header {font-weight:bold; text-align:center;}\n\
        *[bgFrame='true'] {border-image: url(" + parent_path +"/icons/bgpy.png" +")\
             0 0 0 0 stretch stretch;}")
        outer_layout.addWidget(outer_frame)
        layout = QVBoxLayout(outer_frame)
        header = QLabel("DICE Key Notification")
        header.setObjectName("header")
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        label = QLabel(msg)
        label.setWordWrap(True)
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        frame = QFrame()
        blayout = QHBoxLayout(frame)
        self.pwd_box_uv = QLineEdit()
        self.pwd_box_uv.setEchoMode(QLineEdit.Password)
        blayout.addWidget(self.pwd_box_uv)
        frame.setLayout(blayout)
        layout.addWidget(frame)

        framebtn = QFrame()
        btnlayout = QHBoxLayout(framebtn)
        allow_button = QPushButton("Allow")
        deny_button = QPushButton("Deny")
        allow_button.clicked.connect(lambda:self._uv_button_clicked(True))
        deny_button.clicked.connect(lambda:self._uv_button_clicked(False))
        btnlayout.addWidget(allow_button)
        btnlayout.addWidget(deny_button)
        framebtn.setLayout(btnlayout)
        layout.addWidget(framebtn)

        outer_frame.setLayout(layout)
        self.dialog.setLayout(outer_layout)


        screen_shape = QDesktopWidget().screenGeometry()
        self.dialog.setGeometry(screen_shape.width()-440,0,350,200)
        self.pwd_box_uv.setFocus()
        self.dialog.show()
    def register_for_user_verification(self):
        """Function for Compendium use to trigger a registration
        for the User Verification key
        """
        pass
    def _perm_button_clicked(self, outcome:bool):
        #self.user_presence_allow = outcome
        self.dialog.close()
        global result
        result = outcome
        result_available.set()

    def _submit_pwd_button_clicked(self):
        global result
        result = self.pwd_box.text()
        self.dialog.close()
        result_available.set()

    def _uv_button_clicked(self, approved:bool):
        global result
        if approved:
            result = self.pwd_box_uv.text()
        else:
            result = False
        self.dialog.close()
        result_available.set()

class QTAuthenticatorUI(DICEAuthenticatorUI):
    """QT based UI that provides a system tray icon and more
    sophisticated user interaction functionality
    """
    def __init__(self):
        super().__init__()
        self.app=None
        self._listeners = []
        self.tray = None
        self.object = None
        self.dialog = None
        self.user_presence_allow = False
        self.menu = None



    def create(self):
        self.app = QTAuthenticatorUICompendiumApp()
        self.app.setQuitOnLastWindowClosed(False)






    def start(self):
        thread = threading.Thread(target=self.fire_post_ui_loaded)
        thread.setDaemon(True)
        thread.start()
        parent_path = os.path.dirname(os.path.abspath(__file__))
        # Create the icon
        icon = QIcon(parent_path + "/icons/die.png")

        # Create the tray
        self.tray = QSystemTrayIcon()
        self.tray.setIcon(icon)
        self.tray.setVisible(True)

        # Create the menu
        self.menu = QMenu()
        #prefs = QAction("Preferences")
        #prefs.triggered.connect(self._preferences)
        #self.menu.addAction(prefs)

        debug_app = QAction("Debug")
        debug_app.triggered.connect(self._debug)
        self.menu.addAction(debug_app)
        # Add a Quit option to the menu.
        quit_app = QAction("Quit")
        quit_app.triggered.connect(self._quit)
        self.menu.addAction(quit_app)
        # Add the menu to the tray
        self.tray.setContextMenu(self.menu)
        self.app.exec_()

    def _debug(self):
        self.fire_menu_clicked("debug")

    def _preferences(self):
        pass

    def _reset_lock(self):
        result_available.clear()
        global result
        result = None

    def check_user_presence(self, msg:str="User Presence Check")->bool:
        dice_event = DICEEvent(DICE_UI_Event.SHOW_UP)
        dice_event.set_message(msg)
        self._reset_lock()
        QApplication.postEvent(self.app,dice_event)
        result_available.wait()
        return result

    def get_user_password(self, msg:str=None)->str:
        dice_event = DICEEvent(DICE_UI_Event.SHOW_PWD)
        dice_event.set_message(msg)
        self._reset_lock()
        QApplication.postEvent(self.app,dice_event)
        result_available.wait()
        return result

    def check_user_verification(self, msg:str=None):
        dice_event = DICEEvent(DICE_UI_Event.SHOW_UV)
        dice_event.set_message(msg)
        self._reset_lock()
        QApplication.postEvent(self.app,dice_event)
        result_available.wait()
        return result

    def register_for_user_verfication(self):
        dice_event = DICEEvent(DICE_UI_Event.CHECK_UV)
        self._reset_lock()
        QApplication.postEvent(self.app,dice_event)
        result_available.wait()
        return result

    def shutdown(self):
        self._quit()
    def _quit(self):
        for listener in self._listeners:
            listener.shutdown()
        self.app.quit()

class QTAuthenticatorUICompendiumApp(QTAuthenticatorUIApp):
    """QT5 UI with system tray icon

    """
    def __init__(self):
        super().__init__()
        self.pwd_box = None
        self.dialog = None
        self.pwd_box_uv = None
        self.compendium_manager = CompendiumManager(self.enrolment_complete,self.registration_complete,self.verify_complete,self.put_complete,self.get_complete,self.compendium_error)
        self.compendium_label = None
        self.holding_method = None
        self.holding_msg = None
        self.dialog_showing = False
        self.challenge_nonce = None
        self.temp_key = None

    def get_user_password(self, msg:str="Enter Password"):
        """Shows the user password dialog

        Args:
            msg (str, optional): The message to show the user in the dialog.
                Defaults to "Enter Password".
        """
        if not self.compendium_manager.is_enrolled():
            if not self.dialog_showing:
                self.create_compendium_dialog("Enrol New Device")
                self.dialog_showing=True

            self.holding_method = self.get_user_password
            self.holding_msg = msg
            self.compendium_manager.enrol_device()
            return
        if not self.compendium_manager.is_encrypted_key_stored():
            if not self.dialog_showing:
                self.create_compendium_dialog("Register New Encryption Key")
                self.dialog_showing=True
            self.compendium_label.setText("Register New Encryption Key")
            self.temp_key = B64.encode(os.urandom(32))
            security_number = random.randint(1000,9999)
            self.compendium_security_label.setText("Security Code:" + str(security_number))
            self.compendium_manager.put_key(self.temp_key,str(security_number))
            self.holding_method = None
            self.holding_msg = None
            return
        if not self.dialog_showing:
            self.create_compendium_dialog("Requesting Key from Companion Device")
            self.dialog_showing=True
        self.compendium_label.setText("Requesting Key from Companion Device")
        security_number = random.randint(1000,9999)
        self.compendium_security_label.setText("Security Code:" + str(security_number))
        self.compendium_manager.get_key(str(security_number))
        self.holding_method = None
        self.holding_msg = None

    def register_for_user_verification(self):
        """Registers the Authenticator with the Companion Device so it
        can be used for User Verification
        """
        if not self.compendium_manager.is_enrolled():
            if not self.dialog_showing:
                self.create_compendium_dialog("Enrol New Device")
                self.dialog_showing=True

            self.holding_method = self.register_for_user_verfication
            self.compendium_manager.enrol_device()
            return
        if not self.dialog_showing:
            self.create_compendium_dialog("Register For User Verification")
            self.dialog_showing=True
        self.compendium_label.setText("Register For User Verification")
        self.compendium_manager.register_for_uv()
        self.holding_method = None
        self.holding_msg = None
    def create_compendium_dialog(self, task:str):
        """Creates a generic dialog to be used when showing Companion Device messages

        Args:
            task (str): String to use in the label to indicate what is happening
        """
        self.dialog = QDialog(flags = Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.dialog.setAttribute(Qt.WA_TranslucentBackground)
        parent_path = os.path.dirname(os.path.abspath(__file__))
        outer_layout = QVBoxLayout(self.dialog)
        outer_layout.setContentsMargins(0,0,0,0)
        outer_frame = QFrame()

        outer_frame.setProperty("bgFrame",True)
        outer_frame.setStyleSheet("#header {font-weight:bold; text-align:center;}\n\
        *[bgFrame='true'] {border-image: url(" + parent_path +"/icons/bgpy.png" +")\
             0 0 0 0 stretch stretch;}")
        outer_layout.addWidget(outer_frame)
        layout = QVBoxLayout(outer_frame)
        header = QLabel("DICE Key Notification")
        header.setObjectName("header")
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        self.compendium_label = QLabel(task)
        self.compendium_label.setWordWrap(True)
        self.compendium_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.compendium_label)
        self.compendium_security_label = QLabel()
        self.compendium_security_label.setWordWrap(True)
        self.compendium_security_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.compendium_security_label)

        framebtn = QFrame()
        btnlayout = QHBoxLayout(framebtn)
        cancel_button = QPushButton("Cancel")

        cancel_button.clicked.connect(lambda:self._compendium_cancel_clicked())

        btnlayout.addWidget(cancel_button)
        framebtn.setLayout(btnlayout)
        layout.addWidget(framebtn)

        outer_frame.setLayout(layout)
        self.dialog.setLayout(outer_layout)


        screen_shape = QDesktopWidget().screenGeometry()
        self.dialog.setGeometry(screen_shape.width()-440,0,350,200)
        self.dialog.show()


    def _compendium_cancel_clicked(self):
        global result
        result = False
        self.dialog.close()
        result_available.set()

    def get_user_verification(self, msg:str="Enter Password"):
        """Shows the user verification dialog

        Args:
            msg (str, optional): Message to show the user in the dialog.
                Defaults to "Enter Password".
        """

        if not self.compendium_manager.is_enrolled():
            if not self.dialog_showing:
                self.create_compendium_dialog("Enrol New Device")
                self.dialog_showing=True

            self.holding_method = self.get_user_verification
            self.holding_msg = msg
            self.compendium_manager.enrol_device()
            return
        if not self.compendium_manager.is_verify_key_stored():
            if not self.dialog_showing:
                self.create_compendium_dialog("Register For User Verification")
                self.dialog_showing=True
            self.compendium_label.setText("Register For User Verification")
            self.holding_method = self.get_user_verification
            self.holding_msg = msg
            self.compendium_manager.register_for_uv()
            return
        if not self.dialog_showing:
            self.create_compendium_dialog("Requesting Companion Device User Verification")
            self.dialog_showing=True
        self.compendium_label.setText("Requesting Companion Device User Verification")
        security_number = random.randint(1000,9999)
        self.compendium_security_label.setText("Security Code:" + str(security_number))
        self.challenge_nonce = os.urandom(32)
        self.compendium_manager.verify(msg,str(security_number),self.challenge_nonce)
        self.holding_method = None
        self.holding_msg = None




    def _perm_button_clicked(self, outcome:bool):
        #self.user_presence_allow = outcome
        self.dialog.close()
        global result
        result = outcome
        result_available.set()

    def _submit_pwd_button_clicked(self):
        global result
        result = self.pwd_box.text()
        self.dialog.close()
        result_available.set()


    def _uv_button_clicked(self, approved:bool):
        global result
        if approved:
            result = self.pwd_box_uv.text()
        else:
            result = False
        self.dialog.close()
        result_available.set()

    @pyqtSlot(str)
    def compendium_error(self, response:str):
        """Slot to receive response from CompendiumManager when an error has occurred

        Args:
            response (str): error message
        """
        self.dialog.close()
        self.dialog_showing=False
        global result
        result = CompendiumError(response)
        result_available.set()

    @pyqtSlot(bool)
    def enrolment_complete(self, response:bool):
        """Slot to receive enrolment complete notification

        Args:
            response (bool): True if successful, False otherwise
        """
        if self.holding_method is not None:
            self.holding_method(self.holding_msg)
            return
        self.dialog.close()
        self.dialog_showing=False
        global result
        result = True
        result_available.set()

    @pyqtSlot(bool)
    def registration_complete(self, response:bool):
        """Slot for receiving registration complete notification

        Args:
            response (bool): True if successful, False if not
        """
        if self.holding_method is not None:
            self.holding_method(self.holding_msg)
            return
        self.dialog.close()
        self.dialog_showing=False
        global result
        result = response
        result_available.set()

    @pyqtSlot(str)
    def verify_complete(self, response:str):
        """Slot for receiving verification complete notification

        This will take the returned signature in the response and
        perform a signature verification before returning True if
        valid and False if not

        Args:
            response (str): Base64 encoded signature
        """
        self.dialog.close()
        self.dialog_showing=False
        global result
        result = self.compendium_manager.check_signature(response, self.challenge_nonce)
        result_available.set()

    @pyqtSlot(str)
    def put_complete(self, response:str):
        """Slot to receive put complete notification

        Response contains the encrypted key which
        has already been stored. If this was called
        during a key generation - the only time it should
        currently be called - then the key generated
        will be returned instead so the caller can
        make use of the key immediately. Otherwise
        the encrypted blob is returned.

        Args:
            response (str): JSON encoded string with encrypted blob
        """
        self.dialog.close()
        self.dialog_showing=False
        global result
        if self.temp_key is not None:
            result = self.temp_key
            self.temp_key = None
        else:
            result = response
        result_available.set()

    @pyqtSlot(str)
    def get_complete(self, response:str):
        """Slot to receive Get complete notification

        Response contains the returned value as Base64

        Args:
            response (str): value returned as Base64
        """
        self.dialog.close()
        self.dialog_showing=False
        global result
        result = response
        result_available.set()
class CompendiumError():
    """Wrapper for detecting errors
    """
    def __init__(self, error:str):
        """Wrapper for errors

        Args:
            error (str): error message
        """
        self.err = error;

class Communicate(QObject):
    """QT Communication signale object

    Args:
        QObject (_type_):
    """
    signal_enrol_complete = pyqtSignal(bool)
    signal_reg_complete = pyqtSignal(bool)
    signal_verify_complete = pyqtSignal(str)
    signal_put_complete = pyqtSignal(str)
    signal_get_complete = pyqtSignal(str)
    signal_error_complete = pyqtSignal(str)


class CompendiumManager():
    """Class to manage the interactions with the compendium library

    """
    def __init__(self, enrol_cb,reg_cb,verify_cb,put_cb,get_cb,err_cb):
        """Initialise the Compendium Manager setting the QT slots to use
        as callbacks. This is necessary as this will receive messages from
        external threads which cannot directly interact with the main QT
        thread.

        This will use the built in authenticator preferences for storing
        Compendium related data, and will manage retrieving and using the
        keys and names.

        Currently this is implemented to support a single Companion Device

        TODO expand to handle multiple companion devices

        Args:
            enrol_cb (_type_): enrol callback slot
            reg_cb (_type_): registration callback slot
            verify_cb (_type_): verification callback slot
            put_cb (_type_): put callback slot
            get_cb (_type_): get callback slot
            err_cb (_type_): error callback slot
        """
        self._prefs = DICEPreferences()
        self._compendium = Compendium()
        self.signals = Communicate()
        self.signals.signal_enrol_complete.connect(enrol_cb)
        self.signals.signal_reg_complete.connect(reg_cb)
        self.signals.signal_verify_complete.connect(verify_cb)
        self.signals.signal_put_complete.connect(put_cb)
        self.signals.signal_get_complete.connect(get_cb)
        self.signals.signal_error_complete.connect(err_cb)


    def is_enrolled(self)->bool:
        """Checks whether a Companion Device has been enrolled

        Returns:
            bool: True if it has, False if not
        """
        if self._prefs.get_device_id() is not None:
            return True
        return False

    def is_encrypted_key_stored(self)->bool:
        """Checks if an encryption key has been setup

        Returns:
            bool: True if it has, False if not
        """
        if self._prefs.get_encrypted_key() is not None:
            return True
        return False

    def is_verify_key_stored(self)->bool:
        """Checks if a verification key has been setup

        Returns:
            bool: True if it has, False if not
        """
        if self._prefs.get_verification_key() is not None:
            return True
        return False

    def put_key(self, key:str, secure_code:str):
        """Makes a PUT call to the companion device to encrypt
        the key

        Args:
            key (str): Key encoded as Base64
            secure_code (str): Security Code string to display on companion device
        """
        self._compendium.put_data(B64.decode(key),self._prefs.get_device_id(),"Virtual Authenticator","Encrypt Config Data",secure_code,self._put_callback)
    def get_key(self, secure_code:str):
        """Makes a PUT call to the Companion Device to
        decrypt the stored encrypted key. This will
        retrieve the encrypted key from Authenticator
        preferences.

        Args:
            secure_code (str): Security Code string to display on companion device
        """
        self._compendium.get_data(json.loads(self._prefs.get_encrypted_key()),self._prefs.get_device_id(),"Virtual Authenticator","Encrypt Config Data",secure_code,self._get_callback)

    def register_for_uv(self):
        """Requests a user verification key from the Companion Device
        """
        self._compendium.register_user_verification(self._prefs.get_device_id(),"Virtual Authenticator UV","Register for User Verification",self._reg_callback)
    def verify(self, message:str, secure_code:str, nonce:bytes):
        """Makes a verification challenge

        Args:
            message (str): Message to show on the companion device (typically URL)
            secure_code (str): Security Code string to display on companion device
            nonce (bytes): challenge bytes to be signed
        """
        self._compendium.perform_user_verification(self._prefs.get_device_id(),"Virtual Authenticator UV",message,secure_code, self._verify_callback,nonce)

    def enrol_device(self):
        """Start the Enrollment process
        """
        self._compendium.enrol_new_device(self._enrol_callback)

    def _enrol_callback(self, data, error=None):
        """Callback for enrollment

        Will store the device ID in the Authenticator preferences
        Args:
            data (dict): Response from enrollment
            error (ProtocolRemoteException, optional): Exception with error
                message, or None if no error
        """
        if error is not None:
            self._compendium.reset()
            self.signals.signal_error_complete.emit(error.err_msg)
            return
        self._compendium.reset()
        self._prefs.set_device_id(data["CD_id"])
        self.signals.signal_enrol_complete.emit(True)

    def _put_callback(self, data, error=None):
        """Callback for PUT request that receives the
        encrypted blob from the Companion Device.

        This will store that data as the encrypted key
        in the Authenticator preferences

        Args:
            data (dict): Response with encrypted data
            error (ProtocolRemoteException, optional): Exception with error
                message, or None if no error
        """
        if error is not None:
            self._compendium.reset()
            self.signals.signal_error_complete.emit(error.err_msg)
            return
        self._prefs.set_encrypted_key(data["encdata"])
        self._compendium.reset()
        self.signals.signal_put_complete.emit(data["encdata"])

    def _get_callback(self, data, error=None):
        """Callback for the GET request

        Receives the decrypted data which it passes back
        to the original caller
        Args:
            data (dict): Response with decrypted data
            error (ProtocolRemoteException, optional): Exception with error
                message, or None if no error
        """
        if error is not None:
            self._compendium.reset()
            self.signals.signal_error_complete.emit(error.err_msg)
            return
        self._compendium.reset()
        self.signals.signal_get_complete.emit(data["data"])

    def _reg_callback(self, data, error=None):
        """Registration callback, will receive the
        app public key which will be stored in the Authenticator
        preferences

        Args:
            data (dict): Response containing app public key
            error (ProtocolRemoteException, optional): Exception with error
                message, or None if no error
        """
        if error is not None:
            self._compendium.reset()
            self.signals.signal_error_complete.emit(error.err_msg)
            return
        self._prefs.set_verification_key(data["app_pk"])
        self._compendium.reset()
        self.signals.signal_reg_complete.emit(True)

    def _verify_callback(self, data, error=None):
        """Verify callback that will receive the signature of
        the challenge nonce. It will be returned to the QT UI which
        is expected to verify it.

        Args:
            data (dict): Response containing the signature of the challenge
            error (ProtocolRemoteException, optional): Exception with error
                message, or None if no error
        """
        if error is not None:
            self._compendium.reset()
            self.signals.signal_error_complete.emit(error.err_msg)
            return
        self._compendium.reset()
        self.signals.signal_verify_complete.emit(data["app_sig"])

    def check_signature(self, signature:str, nonce:bytes)->bool:
        """Utlity method to verify the signature and challenge nonce
        using the stored app public key stored in the Authenticator
        preferences

        Args:
            signature (str): Base64 encoded signature of nonce
            nonce (bytes): challenge nonce issued to verify call

        Returns:
            bool: _description_
        """
        return self._compendium.verify_signature(signature,nonce,self._prefs.get_verification_key())