from flask import Flask, render_template, request
from flaskwebgui import FlaskUI
from threading import Thread
from flask_socketio import SocketIO, emit
from redis_dict import RedisDict
import json
import os
from markupsafe import escape
from module.tiktok import TikTok
import time
import asyncio

app = Flask(__name__)
socketio = SocketIO(app)
gift_config_redis = RedisDict(namespace='gift_config')
config_redis = RedisDict(namespace='config')
pk_redis = RedisDict(namespace='pk')


def prepare_redis():
    global config_redis

    for config in ['background_music', 'profile', 'room_id']:
        if config not in config_redis:
            config_redis[config] = ''

    if 'available_gifts' not in config_redis:
        tt = TikTok(app.tiktok_dance, socketio.emit)
        asyncio.run(tt.update_available_gifts())

    for config in ['ended_at', 'duration', 'a_point', 'b_point']:
        if config not in pk_redis:
            pk_redis[config] = 0

    for config in ['name']:
        if config not in pk_redis:
            pk_redis[config] = ''

    for team in ['a', 'b']:
        if team not in pk_redis:
            pk_redis[team] = {'name': '', 'gifts': []}


def available_profile():
    default = config_redis['profile']
    profiles = list()
    for filename in os.scandir('profile'):
        if filename.is_file() and '.json' in filename.name:
            name = filename.name.split('.')[0]
            if name == default:
                profiles.insert(0, name)
            else:
                profiles.append(name)
    data = {
        'default': config_redis['profile'],
        'list': profiles
    }
    return data


@app.route("/")
def home():
    global gift_config_redis, config_redis
    name = config_redis['profile']

    file_path = f'profile/{name}.json'
    is_valid = os.path.exists(file_path)
    if not is_valid:
        profile = None
        config = None
    else:
        with open(file_path, mode='r', encoding='utf-8') as f:
            profile = json.load(f)
            config = profile['gift_config']

    connected = True
    if not app.tiktok_client or not app.tiktok_client.is_alive():
        connected = False

    return render_template('index.html',
                           gift_config=config, gifts=config_redis['available_gifts'], profile=name,
                           profiles=available_profile(), setting=profile, config=config_redis, connected=connected,
                           pause=not app.mixer.pause, queue=app.mixer.queue_redis['queue'],
                           speed=app.mixer.queue_redis['speed'])


@app.route("/embed")
def embed():
    global gift_config_redis, config_redis
    name = config_redis['profile']

    file_path = f'profile/{name}.json'
    is_valid = os.path.exists(file_path)
    if not is_valid:
        profile = None
        config = None
    else:
        with open(file_path, mode='r', encoding='utf-8') as f:
            profile = json.load(f)
            config = profile['gift_config']

    connected = True
    if not app.tiktok_client or not app.tiktok_client.is_alive():
        connected = False

    return render_template('embed.html',
                           gift_config=config, gifts=config_redis['available_gifts'], profile=name,
                           profiles=available_profile(), setting=profile, config=config_redis, connected=connected,
                           pause=not app.mixer.pause, queue=app.mixer.queue_redis['queue'],
                           speed=app.mixer.queue_redis['speed'])


@app.route("/pk_embed")
def pk_embed():
    global gift_config_redis, config_redis, pk_redis

    connected = True
    if not app.tiktok_client or not app.tiktok_client.is_alive():
        connected = False

    remain_time = pk_redis['ended_at'] - round(time.time())

    return render_template('pk_embed.html', pk_config=pk_redis, is_pk=remain_time > 0, remain_time=max(0, remain_time),
                           gifts=config_redis['available_gifts'],
                           profiles=available_profile(), connected=connected,
                           pause=not app.mixer.pause)


@app.route("/pk")
def pk():
    global gift_config_redis, config_redis, pk_redis

    connected = True
    if not app.tiktok_client or not app.tiktok_client.is_alive():
        connected = False

    remain_time = pk_redis['ended_at'] - round(time.time())

    return render_template('pk.html', pk_config=pk_redis, is_pk=remain_time > 0, remain_time=max(0, remain_time),
                           gifts=config_redis['available_gifts'],
                           profiles=available_profile(), connected=connected,
                           pause=not app.mixer.pause)


@app.route("/profile")
def profile():
    global config_redis
    return render_template('profile.html', profiles=available_profile(), gifts=config_redis['available_gifts'])


@app.route("/profile/<name>")
def profile_detail(name):
    global gift_config_redis, config_redis
    name = escape(name)

    file_path = f'profile/{name}.json'
    is_valid = os.path.exists(file_path)
    if not is_valid:
        return 404

    with open(file_path, mode='r', encoding='utf-8') as f:
        profile = json.load(f)
        config = profile['gift_config']

    return render_template('profile_detail.html',
                           gift_config=config, gifts=config_redis['available_gifts'], profile=name,
                           profiles=available_profile(), setting=profile
                           )


@socketio.on('create_profile')
def create_profile(name):
    if not name:
        emit('create_profile', {'success': False, 'msg': f"Tên không được để trống"})
        return False

    file_path = f'profile/{name}.json'

    if '/' in name:
        emit('create_profile', {'success': False, 'msg': f"Tên không được chứa ký tự '/'"})
        return False

    is_used = os.path.exists(file_path)
    if is_used:
        emit('create_profile', {'success': False, 'msg': f'Tên này đã được sử dụng'})
        return False

    data = {
        'background_music': '',
        'cross_sound': '',
        'gift_config': []
    }
    with open(file_path, mode='w+', encoding='utf-8') as f:
        json.dump(data, f)
    emit('create_profile', {'success': True, 'msg': f'{name}', 'location': f'/profile/{name}'})


@socketio.on('delete_profile')
def delete_profile(name):
    file_path = f'profile/{name}.json'

    is_valid = os.path.exists(file_path)
    if not is_valid:
        emit('delete_profile', {'success': False, 'msg': f'Profile này không tồn tại'})
        return

    os.remove(file_path)

    emit('delete_profile', {'success': True, 'msg': f'{name}', 'location': f'/profile'})


@socketio.on('reset_queue')
def reset_queue(name):
    app.mixer.reset_all()
    emit('queue', app.mixer.queue_redis["queue"])
    emit('speed', app.mixer.queue_redis["speed"])


@socketio.on('set_default_profile')
def set_default_profile(name):
    global config_redis
    file_path = f'profile/{name}.json'

    is_valid = os.path.exists(file_path)
    if not is_valid:
        emit('set_default_profile', {'success': False, 'msg': f'Profile này không tồn tại'})
        return

    config_redis['profile'] = name

    app.tiktok_dance.update_gift_config()

    emit('set_default_profile', {'success': True, 'msg': f'{name}', 'location': f'/profile/{name}'})


def verify_gift_data(data, event):
    global config_redis

    file_path = f'profile/{data["profile"]}.json'
    is_valid = os.path.exists(file_path)
    if not is_valid:
        emit(event, {'success': False, 'msg': f"Profile '{data['profile']}' không tồn tại"})
        return False, False, False

    if not data['name']:
        emit(event, {'success': False, 'msg': f"Tên quà không được để trống"})
        return False, False, False

    gift = None
    for g in config_redis['available_gifts']:
        if int(data['id']) == g['id']:
            gift = g
            break

    if not gift:
        emit(event, {'success': False, 'msg': f"Quà '{data['id']}' không tồn tại"})
        return False, False, False

    for type in data['types']:
        if type not in ['PRIORITY', 'RESET', 'RESCUE', 'FAST', 'SLOW']:
            emit(event, {'success': False, 'msg': f"Loại quà '{type}' không tồn tại"})
            return False, False, False

    sounds = list()
    for s in data['sounds']:
        if s:
            is_valid = os.path.exists(s)
            if not is_valid:
                emit(event, {'success': False, 'msg': f"Link nhạc '{s}' không tồn tại"})
                return False, False, False
            else:
                sounds.append(s)

    return True, gift, sounds


@socketio.on('edit_gift')
def edit_gift(data):
    file_path = f'profile/{data["profile"]}.json'

    valid, gift, sounds = verify_gift_data(data, event='edit_gift')
    if not valid:
        return

    with open(file_path, mode='r', encoding='utf-8') as f:
        profile = json.load(f)

    gift_config = i = None
    for i, gc in enumerate(profile['gift_config']):
        if gift['id'] == gc['id']:
            gift_config = gc
            break

    if not gift_config:
        emit('edit_gift', {'success': False, 'msg': f"Quà '{data['id']}' chưa có trong profile, không thể chỉnh sửa"})
        return

    profile['gift_config'][i] = {
        'id': gift['id'],
        'name': data['name'],
        'gift_name': gift['name'],
        'thumbnail': gift['thumbnail'],
        'price': gift['price'],
        'types': data['types'],
        'sounds': sounds
    }

    with open(file_path, mode='w+', encoding='utf-8') as f:
        json.dump(profile, f)

    if data["profile"] == config_redis['profile']:
        app.tiktok_dance.update_gift_config()

    emit('edit_gift', {'success': True, 'msg': profile['gift_config'][i], 'location': f'/profile/{data["profile"]}'})


@socketio.on('add_gift')
def add_gift(data):
    file_path = f'profile/{data["profile"]}.json'

    valid, gift, sounds = verify_gift_data(data, event='add_gift')
    if not valid:
        return

    with open(file_path, mode='r', encoding='utf-8') as f:
        profile = json.load(f)

    for gc in profile['gift_config']:
        if gift['id'] == gc['id']:
            emit('add_gift', {'success': False, 'msg': f"Quà '{gift['name']}' đã có trong profile"})
            return

    config = {
        'id': gift['id'],
        'name': data['name'],
        'gift_name': gift['name'],
        'thumbnail': gift['thumbnail'],
        'price': gift['price'],
        'types': data['types'],
        'sounds': sounds
    }

    profile['gift_config'].append(config)

    with open(file_path, mode='w+', encoding='utf-8') as f:
        json.dump(profile, f)

    if data["profile"] == config_redis['profile']:
        app.tiktok_dance.update_gift_config()

    emit('add_gift', {'success': True, 'msg': config, 'location': f'/profile/{data["profile"]}'})


@socketio.on('update_profile_setting')
def update_profile_setting(data):
    file_path = f'profile/{data["profile"]}.json'

    if not os.path.exists(file_path):
        emit('update_profile_setting', {'success': False, 'msg': f"Profile '{data['profile']}' không tồn tại"})
        return

    if data['background_music'] and not os.path.exists(data['background_music']):
        emit('update_profile_setting',
             {'success': False, 'msg': f"Link nhạc nền '{data['background_music']}' không tồn tại"})
        return

    if data['cross_music'] and not os.path.exists(data['cross_music']):
        emit('update_profile_setting',
             {'success': False, 'msg': f"Link nhạc chuyển'{data['cross_music']}' không tồn tại"})
        return

    with open(file_path, mode='r', encoding='utf-8') as f:
        profile = json.load(f)

    profile['background_music'] = data['background_music']
    profile['cross_music'] = data['cross_music']

    with open(file_path, mode='w', encoding='utf-8') as f:
        json.dump(profile, f)

    if data["profile"] == config_redis['profile']:
        app.tiktok_dance.update_gift_config()

    emit('update_profile_setting', {'success': True, 'msg': data})
    return


@socketio.on('delete_gift')
def delete_gift(data):
    event = 'delete_gift'

    file_path = f'profile/{data["profile"]}.json'

    if not os.path.exists(file_path):
        emit(event, {'success': False, 'msg': f"Profile '{data['profile']}' không tồn tại"})
        return

    with open(file_path, mode='r', encoding='utf-8') as f:
        profile = json.load(f)

    gift = None
    for g in config_redis['available_gifts']:
        if int(data['id']) == g['id']:
            gift = g
            break

    if not gift:
        emit(event, {'success': False, 'msg': f"Quà '{data['id']}' không tồn tại"})
        return False, False, False

    gift_config = profile['gift_config']
    profile['gift_config'] = list()

    for gc in gift_config:
        if gift['id'] != gc['id']:
            profile['gift_config'].append(gc)

    with open(file_path, mode='w', encoding='utf-8') as f:
        json.dump(profile, f)

    if data["profile"] == config_redis['profile']:
        app.tiktok_dance.update_gift_config()

    emit(event, {'success': True, 'msg': data})
    return


@socketio.on('update_app_setting')
def update_app_setting(data):
    event = 'update_app_setting'

    data['room_id'] = data['room_id'].replace('@', '')

    if not data['room_id']:
        emit(event,
             {'success': False, 'msg': f"Room ID không được để trống"})
        return

    if not data['play_delay']:
        data['play_delay'] = 0

    try:
        data['play_delay'] = float(data['play_delay'])
    except:
        emit(event,
             {'success': False, 'msg': f"Thời gian giờ chuyển bài phải là số"})
        return

    if not data['queue_type'] or data['queue_type'] not in ['GIFT', 'COMBO']:
        emit(event,
             {'success': False, 'msg': f"Quy tắc thêm danh sách chờ '{data['queue_type']}' không hợp lệ"})
        return

    config_redis['room_id'] = data['room_id']
    config_redis['play_delay'] = data['play_delay']
    config_redis['queue_type'] = data['queue_type']

    emit(event, {'success': True, 'msg': data})
    return


@socketio.on('tiktok_client_connect')
def tiktok_client_connect(data):
    event = 'tiktok_client_connect'

    if 'room_id' not in config_redis or not config_redis['room_id']:
        emit(event, {'success': False, 'msg': f"Chưa cài đặt room id"})

    if 'play_delay' not in config_redis:
        config_redis['play_delay'] = 0.0

    if 'queue_type' not in config_redis:
        config_redis['queue_type'] = "GIFT"

    app.tiktok_client = TikTok(app=app.tiktok_dance, emit=socketio.emit)
    app.tiktok_client.start()

    return


@socketio.on('pause')
def pause(data):
    event = 'pause'

    if data['state']:
        app.mixer.channel_bg_music.pause()
    else:
        app.mixer.channel_bg_music.unpause()

    app.mixer.pause = data['state']

    emit(event, {'success': True, 'msg': not data['state']})
    return


@socketio.on('queue')
def queue(data):
    emit('queue', app.mixer.queue_redis["queue"])
    emit('speed', app.mixer.queue_redis["speed"])
    return


@socketio.on('add_queue')
def add_queue(data):
    app.tiktok_dance.add_queue(data['gift'], data['quantity'])
    emit('queue', app.mixer.queue_redis["queue"])
    emit('speed', app.mixer.queue_redis["speed"])
    return


@socketio.on('pk_config')
def pk_config(data):
    global pk_redis

    event = 'pk_config'

    if not data['duration']:
        emit(event, {'success': False, 'msg': f"Vui lòng nhập thời gian vòng đấu"})
        return

    for team in ['a', 'b']:
        if not data[team]['name']:
            emit(event, {'success': False, 'msg': f"Vui lòng chọn tên team {team.upper()}"})
            return
        if not data[team]['gifts']:
            emit(event, {'success': False, 'msg': f"Vui lòng chọn quà team {team.upper()}"})
            return
        data[team]['thumbnails'] = list()
        for id in data[team]['gifts']:
            gift = None
            for g in config_redis['available_gifts']:
                if id == g['id']:
                    gift = g
                    break
            if not gift:
                emit(event, {'success': False, 'msg': f"Quà (ID: {id}) team {team.upper()} không hợp lệ"})
                return
            data[team]['thumbnails'].append(gift['thumbnail'])

    pk_redis['duration'] = data['duration']
    pk_redis['name'] = data['name']
    pk_redis['a'] = data['a']
    pk_redis['b'] = data['b']
    emit(event, {'success': True, 'msg': data})


@socketio.on('start_pk')
def start_pk(data):
    global pk_redis

    event = 'start_pk'

    if 'duration' not in pk_redis or not pk_redis['duration']:
        emit(event, {'success': False, 'msg': f"Vui lòng cài đặt thời gian vòng đấu"})
        return

    for team in ['a', 'b']:
        if team not in pk_redis or 'name' not in pk_redis[team] or not pk_redis[team]['name']:
            emit(event, {'success': False, 'msg': f"Vui lòng cài đặt tên team {team.upper()}"})
            return
        if team not in pk_redis or 'gifts' not in pk_redis[team] or not pk_redis[team]['gifts']:
            emit(event, {'success': False, 'msg': f"Vui lòng cài đặt quà team {team.upper()}"})
            return

    pk_redis['a_point'] = 0
    pk_redis['b_point'] = 0
    pk_redis['ended_at'] = round(time.time()) + pk_redis['duration'] * 60

    emit(event, {'success': True, 'msg': pk_redis['duration'] * 60})
    app.tiktok_dance.start_pk()
    Thread(target=stop_pk, args=()).start()


def stop_pk():
    time.sleep(pk_redis['duration'] * 60)
    app.tiktok_dance.stop_pk()


@socketio.on('update_remain_time')
def update_remain_time(data):
    event = 'update_remain_time'
    global pk_redis
    remain_time = pk_redis['ended_at'] - round(time.time())
    if remain_time < 0:
        remain_time = "Kết Thúc"
    emit(event, remain_time)


class Webapp(Thread):
    def __init__(self, tiktok_dance, mixer):
        super().__init__()
        global app
        self.flask = app
        app.tiktok_dance = tiktok_dance
        app.mixer = mixer
        app.mixer.emit = socketio.emit
        app.tiktok_client = None
        prepare_redis()

    @staticmethod
    def is_started():
        with app.test_request_context():
            return request.url_root

    @staticmethod
    def start_sever(**server_kwargs):
        server_kwargs["flask_socketio"].run(server_kwargs["app"], port=server_kwargs["port"],
                                            allow_unsafe_werkzeug=True)

    def run(self):
        import logging
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)
        FlaskUI(
            server=self.start_sever,
            server_kwargs={
                'allow_unsafe_werkzeug': True,
                'flask_socketio': socketio,
                'app': app,
                'port': 5000
            },
            width=1600,
            height=900
        ).run()
        # app.run(debug=True, use_reloader=False)
