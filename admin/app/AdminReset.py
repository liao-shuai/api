# -*- coding:utf-8 -*-
from api.db.mongodb import apiDB

from os import urandom
from binascii import b2a_hex
from flask import flash
from api.db.models.vendor20000.Device import Device as DeviceModel
from api.app.getway.AdminReset import DeviceReset
from config import DATABASE as admindb

import datetime

devicedb = apiDB


class OneReset():

    def one_reset(self, imei, username):
        if devicedb.device.find({"_id": imei}).count() > 0:
            device = DeviceModel.mustFindOne(imei)
            if device.get('token') is None:
                flash(u'%s手表未开机,不需要恢复出厂设置' % imei)
            else:
                admin = admindb.users.find_one({"username": username})
                if admin['permissions'] == 'admin':
                    num = admin['resetnum']
                    if num < 50:
                        s = DeviceReset()
                        s.post(imei)
                        resetlist = admin.get('resetlist', [])
                        data = {
                            'imei': imei,
                            'time': datetime.datetime.now(),
                        }
                        resetlist.append(data)
                        admindb.users.update_one({'username': username}, {'$set': {'resetlist': resetlist}})
                        flash(u'解绑 %s 成功' % imei)
                        num += 1
                        admindb.users.update_one({'username': username}, {'$set': {'resetnum': num}})
                    else:
                        flash(u'今天已解绑50次,请明天再执行')
                else:
                    s = DeviceReset()
                    s.post(imei)
                    resetlist = admin.get('resetlist', [])
                    data = {
                        'imei': imei,
                        'time': datetime.datetime.now(),
                    }
                    resetlist.append(data)
                    admindb.users.update_one({'username': username}, {'$set': {'resetlist': resetlist}})
                    flash(u'解绑成功')
        else:
            flash(u'%s 不存在' % imei)


class MultiReset():

    def multi_reset(self, imei_list, username):
        miss_num = 0
        none_num = 0
        sucess_num = 0
        miss_list = []
        none_list = []
        admin = admindb.users.find_one({"username": username})
        num = admin['resetnum']
        for imei in imei_list:
            if devicedb.device.find({"_id": imei}).count() > 0:
                device = DeviceModel.mustFindOne(imei)
                if device.get('token') is None:
                    miss_list.append(imei)
                    miss_num += 1
                else:
                    if admin['permissions'] == 'admin':
                        if num < 50:
                            s = DeviceReset()
                            s.post(imei)
                            sucess_num += 1
                            resetlist = admin.get('resetlist', [])
                            data = {
                                'imei': imei,
                                'time': datetime.datetime.now(),
                            }
                            resetlist.append(data)
                            admindb.users.update_one({'username': username}, {'$set': {'resetlist': resetlist}})
                            num += 1
                            admindb.users.update_one({'username': username}, {'$set': {'resetnum': num}})

                    else:
                        s = DeviceReset()
                        s.post(imei)
                        sucess_num += 1
                        resetlist = admin.get('resetlist', [])
                        data = {
                            'imei': imei,
                            'time': datetime.datetime.now(),
                        }
                        resetlist.append(data)
                        admindb.users.update_one({'username': username}, {'$set': {'resetlist': resetlist}})
            else:
                none_list.append(imei)
                none_num += 1
        all_msg = (u'成功解绑%s个imei,imei不存在的有%s个,手表未开机，不需要恢复出厂设置的有%s个' %
                      (sucess_num, none_num, miss_num))
        none_msg = (u'不存在的imei如下: %s' % none_list)
        miss_msg = (u'手表未开机，不需要恢复出厂设置的imei如下: %s' % miss_list)
        if num == 50:
            flash(u'今天已解绑50次,请明天再执行')
        if none_num != 0 and miss_num != 0:
            flash(u'%s' % all_msg)
            flash(u'%s' % none_msg)
            flash(u'%s' % miss_msg)
        if none_num == 0 and miss_num != 0:
            flash(u'成功解绑%s个imei,手表未开机，不需要恢复出厂设置的有%s个' %
                      (sucess_num, miss_num))
            flash(u'%s' % miss_msg)
        if none_num != 0 and miss_num == 0:
            flash(u'成功解绑%s个imei,imei不存在的有%s个' %
                      (sucess_num, none_num))
            flash(u'%s' % none_msg)
        if none_num == 0 and miss_num == 0:
            flash(u'成功解绑%s个imei' % sucess_num)


class AddDevice():
    def post(self, imeilist, vendor):
        sucess_num = 0
        miss_num = 0
        none_num = 0
        miss_list = []
        none_list = []
        for imei in imeilist:
            imei = str(imei)
            data = {
                '_id': imei,
                'manualImport': 1,
                'v': int(vendor),
            }
            deviceDB = devicedb['device'].find_one({'_id': imei})
            if len(imei) == 15 or len(imei) == 14:
                if deviceDB is None:
                    devicedb['device'].insert(data)
                    sucess_num += 1
                else:
                    devicedb['device'].update({'_id': imei}, {'$set': {'manualImport': 1}})
                    miss_num += 1
                    miss_list.append(imei)
            else:
                none_num += 1
                none_list.append(imei)
        if miss_num != 0 and none_num != 0:
            flash(u'成功导入%d个imei, %d个导入不成功' % (sucess_num, none_num + miss_num))
            flash(u'已存的数据库的imei:%s' % miss_list)
            flash(u'不是14或15位号码的:%s' % none_list)
        if miss_num == 0 and none_num != 0:
            flash(u'成功导入%d个imei, %d个导入不成功' % (sucess_num, none_num))
            flash(u'不是14或15位号码的:%s' % none_list)
        if miss_num != 0 and none_num == 0:
            flash(u'成功导入%d个imei, %d个导入不成功' % (sucess_num, miss_num))
            flash(u'已存的数据库的imei:%s' % miss_list)
        if miss_num == 0 and none_num == 0:
            flash(u'成功导入%d个imei' % sucess_num)


class CreateUser():

    def create_admin(self, username, password):
        nowtime = datetime.datetime.now()
        permissions = 'admin'
        userid = b2a_hex(urandom(12))
        if username.strip() == '' or password.strip() == '':
            flash('账号和密码不能为空', 'danger')
        else:
            if admindb.users.find_one({"username": username}) is None:
                admindb.users.insert_one({
                    '_id': userid,
                    'username': username,
                    'password': password,
                    'permissions': permissions,
                    'resetnum': 0,
                    'resetlist': [],
                    'maketime': nowtime,
                    'lasttime': nowtime
                })
                flash('建立账号成功','info')
            else:
                flash('用户名已存在','danger')


class DeleteUser():

    def delete_admin(self, username):
        info = admindb.users.find_one({"username": username})
        if info['permissions'] == 'superadmin':
            flash('你不能删除你自己账号!', 'info')
        else:
            admindb.users.delete_one({"username": username})
            flash('删除账号成功', 'danger')


