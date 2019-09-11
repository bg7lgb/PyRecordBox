#-*- coding: utf-8 -*-

from ws4py.websocket import WebSocket
import logging,json

logger = logging.getLogger('PyRecordBox.PhoneWebSocket')

pws_app = None

class PhoneWebSocket(WebSocket):

    def opened(self):
        logger.debug('客户端已连接')
        global pws_app
        self.setApp(pws_app)

    def received_message(self, message):
        logger.debug(message.data)
        try:
            text = json.loads(message.data)
            if text['command'] =='dial':
                phone_no = str(text['phone_no'])
                logger.debug(phone_no)
                self.app.dialout(phone_no)
            else:
                logger.debug('收到命令 %s' %text['command'])
        except ValueError:
            # 不是合法的json格式
            self.send(message.data, message.is_text)

    def setApp(self, app):
        self.app = app
