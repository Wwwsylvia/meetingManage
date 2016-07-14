#-*-coding:utf-8-*- 
__author__ = 'kanchan'

from app import mongo
import pymongo
import traceback
from flask import json


def error_return(reason):
    return json.jsonify({'result': 'failed',
                         'reason': reason})


def check_in(openid, meetingid):
    try:
        m = mongo.db.meetings.find_one({'meetingid': meetingid})
        for user in m['attendee']:
            if user['openid'] == openid:
                if user['status'] == 'checked':
                    return '已经签到啦，不用重复签到'
                else:
                    mongo.db.meeting.update_one({'meetingid': meetingid,
                                                 'attendee.openid': openid},
                                                {'$set': {'attendee.status': 'checked'}})
                    return '签到成功！'
    except pymongo.errors.PyMongoError:
        traceback.print_exc()
        reason = 'check_in(): Error when update mongodb in check_in().'
        print(reason)
        return error_return(reason)
    except:
        traceback.print_exc()
        return error_return('Other exception')