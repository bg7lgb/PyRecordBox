#-*- coding: utf-8 -*-

from ws4py.websocket import WebSocket
import logging,json

logger = logging.getLogger('PyRecordBox.PhoneWebSocket')

pws_app = None

class PhoneWebSocket(WebSocket):

    def opened(self):
        logger.debug(u'客户端已连接')
        global pws_app
        self.setApp(pws_app)

    def received_message(self, message):
        logger.debug(message.data)
        try:
            text = json.loads(message.data)
            if text['command'] =='dial':
                self.app.dialout(text['phone_no'])
            else:
                logger.debug(u'收到命令 %s' %text['command'])
        except ValueError:
            # 不是合法的json格式
            self.send(message.data, message.is_text)

    def setApp(self, app):
        self.app = app
