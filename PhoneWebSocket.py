#-*- coding: utf-8 -*-

from ws4py.websocket import WebSocket
import logging

logger = logging.getLogger('PyRecordBox.PhoneWebSocket')

class PhoneWebSocket(WebSocket):

    def opened(self):
        logger.debug('a client connected')

    def received_message(self, message):
        logger.debug(message.data)

        self.send(message.data, message.is_binary)



