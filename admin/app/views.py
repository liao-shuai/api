# -*- coding: utf-8 -*-

import os
import sys
import xlrd
import logging
import datetime
import json


from flask import Flask, abort, session
from flask import request, redirect, render_template, url_for, flash
from flask_login import LoginManager
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename

import config
from forms import LoginForm, OnedelForm, CreateUserForm
from models import User
from config import DATABASE as db

__current_dir = os.path.dirname(os.path.abspath(__file__))
sss_dir = os.path.dirname(__current_dir)
sys.path.append(os.path.dirname(sss_dir))

from admin.app.AdminReset import AddDevice, CreateUser, OneReset, MultiReset, DeleteUser


app = Flask(__name__)
UPLOAD_FOLDER = '/jy/mywear/admin/app/upload'
UPLOAD_FOLDER_XLS = UPLOAD_FOLDER + '/xls'
app.config.from_object(config)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['UPLOAD_FOLDER_XLS'] = UPLOAD_FOLDER_XLS
app.config['USERS_COLLECTION'] = db['users']
lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'

reload(sys)
sys.setdefaultencoding('utf8')

basedir = os.path.abspath(os.path.dirname(__file__))
ALLOWED_EXTENSIONS = set(['txt', 'xls', 'xlsx'])
userdb = db['users']


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/')
@login_required
def index():
    user = current_user.username
    info = db.users.find_one({"username": user})
    permissions = info['permissions']
    return render_template('index.html', permissions=permissions)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST' and form.validate_on_submit():
        user = app.config['USERS_COLLECTION'].find_one({"username": form.username.data})
        if user and user['password'] == form.password.data:
            user_obj = User(user['username'])
            login_user(user_obj)
            nowtime = datetime.datetime.now()
            if nowtime.month != user['lasttime'].month or nowtime.day != user['lasttime'].day:
                db.users.update_one({'username': form.username.data}, {'$set': {'resetnum': 0}})
            db.users.update_one({'username': form.username.data}, {'$set': {'lasttime': nowtime}})
            return redirect(request.args.get("next") or url_for("index"))
        else:
            flash(u'用户名或密码输入错误')
            return redirect(url_for("login"))
    return render_template('login.html', title='login', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/onedel', methods=['GET', 'POST'])
@login_required
def onedelete():
    form = OnedelForm()
    username = current_user.username
    info = db.users.find_one({"username": username})
    permissions = info['permissions']
    if request.method == 'POST':
        imei = form.imei.data.strip()
        onereset = OneReset()
        if len(imei) != 15:
            flash(u'解绑失败,请检查imei格式是否出错')
        else:
            onereset.one_reset(imei, username)
    return render_template('onedel.html', form=form, permissions=permissions)


@app.route('/multidel', methods=['GET', 'POST'])
@login_required
def multidelete():
    username = current_user.username
    info = db.users.find_one({"username": username})
    permissions = info['permissions']
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            with open(os.path.join(app.config['UPLOAD_FOLDER'], filename), 'r') as f:
                imei_list = []
                for line in f:
                    imei = line[:15].strip()
                    imei_list.append(imei)
                multreset = MultiReset()
                multreset.multi_reset(imei_list, username)

            return redirect(url_for('multidelete'))
        else:
            flash('请选择上传文件')
    return render_template('multidel.html', permissions=permissions)


@app.route('/addall/addimei', methods=['GET', 'POST'])
def addimei():
    if request.method == 'POST':
        vendor = request.values.get('vendor')
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER_XLS'], filename))
            with open(os.path.join(app.config['UPLOAD_FOLDER_XLS'], filename), 'r') as f:
                fname = f.name
                devicedata = xlrd.open_workbook(fname)
                table = devicedata.sheet_by_index(0)
                nrow = table.nrows
                imei_list = []
                for i in range(nrow):
                    k = table.row_values(i)
                    for j in k:
                        try:
                            imei = int(j)
                        except:
                            imei = str(j)
                        imei_list.append(imei)
                adddevice = AddDevice()
                adddevice.post(imei_list, vendor=vendor)
    return render_template('addimei.html')


@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    form = CreateUserForm()
    username = current_user.username
    info = db.users.find_one({"username": username})
    permissions = info['permissions']
    if request.method == 'GET':
        datas = db.users.find()
        return render_template('profile.html', datas=datas, form=form, permissions=permissions)


@app.route('/admin/create', methods=['POST'])
@login_required
def admin_create():
    if request.method == 'POST':
        form = CreateUserForm()
        username = form.username.data
        password = form.password.data
        create = CreateUser()
        create.create_admin(username, password)
        return redirect('admin')


@app.route('/admin/<user>delete', methods=['GET', 'POST'])
@login_required
def admin_delete(user):
    delete = DeleteUser()
    delete.delete_admin(user)
    return redirect('admin')


@app.route('/admin/<user>info', methods=['GET', 'POST'])
@login_required
def admin_info(user):
    username = current_user.username
    info = db.users.find_one({"username": username})
    permissions = info['permissions']
    user_info = db.users.find_one({"username": user})
    datas = user_info['resetlist']
    return render_template('user_info.html', datas=datas, user=user, permissions=permissions)


@lm.user_loader
def load_user(username):
    u = app.config['USERS_COLLECTION'].find_one({"username": username})
    if not u:
        return None
    return User(u['username'])

