from pprint import pformat
from urllib.parse import urljoin, urlencode

from flask import request
from wechatpy import parse_message
from wechatpy.events import ClickEvent, SubscribeScanEvent, ScanEvent
from wechatpy.exceptions import InvalidSignatureException
from wechatpy.messages import TextMessage
from wechatpy.replies import TextReply
from wechatpy.utils import check_signature
from libs.checkin import emit_checked_in

from app import app, TOKEN, mongo
from libs.constants import *
from libs.outlook.events import get_events_by_wxid_x
from libs.utility import check_in
# from libs.outlook.events import get_events_by_wxid_x


@app.route('/weixin', methods=['GET', 'POST'])
def weixin():
    if request.method == 'GET':
        _g = lambda k: request.args.get(k)

        try:
            print(TOKEN, _g('signature'), _g('timestamp'), _g('nonce'))
            check_signature(TOKEN,
                            _g('signature'),
                            _g('timestamp'),
                            _g('nonce'))

            return _g('echostr')
        except InvalidSignatureException:
            pass

    elif request.method == 'POST':
        msg = parse_message(request.data)

        if isinstance(msg, ClickEvent):
            ev = msg

            if ev.key == WX_BTN_BIND_BX:
                reply = TextReply()
                reply.source = ev.target
                reply.target = ev.source
                reply.content = '请访问以下链接登陆到BX邮箱\n%s' % (
                    '%s?%s' % (urljoin(DOMAIN, 'mslogin'),
                               urlencode({'wx': ev.source}))
                )
                return reply.render()
            elif ev.key == WX_BTN_BEGIN_CHECKIN:
                reply = TextReply()
                reply.source = msg.target
                reply.target = msg.source
                reply.content = '请访问以下链接选择开始哪个会议\n%s' % (
                    '%s/check-in-meetings?openid=%s' % (DOMAIN, msg.source)
                )
                return reply.render()

        elif isinstance(msg, TextMessage):
            if msg.content.lower().startswith('e'):
                reply = TextReply()
                reply.source = msg.target
                reply.target = msg.source
                reply.content = '请访问以下链接选择开始哪个会议\n%s' % (
                    '%s/check-in-meetings?openid=%s' % (DOMAIN, msg.source)
                )

                return reply.render()

        elif isinstance(msg, ScanEvent) or isinstance(msg, SubscribeScanEvent):
            openid = msg.source
            meetingid = msg.scene_id
            emit_checked_in(openid=openid, meeting=mongo.db.meeting.find_one({'meetingid': meetingid}))
            return check_in(openid=openid, meetingid=meetingid)

