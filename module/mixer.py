import os.path
import random
from threading import Thread
from typing import Optional
from module.model import GiftConfig
from module.log import get_logger
import time
from pygame.mixer import Sound
from pygame import error
from vlc import State, Media, MediaPlayer
from redis_dict import RedisDict

log = get_logger(__name__)


class Controller(Thread):
    def __init__(self, mixer):
        super().__init__()
        self.mixer = mixer
        self.queue_redis = RedisDict('queue')
        if 'speed' not in self.queue_redis:
            self.queue_redis['speed'] = list()
        self.current_speed: Optional[dict] = None

    def remove_top_queue(self) -> dict:
        current_queue = self.queue_redis['speed']
        if current_queue:
            speed = current_queue.pop(0)
            self.queue_redis['speed'] = current_queue
            return speed

    def set_speed(self, speed):
        is_valid = False
        if "FAST" in speed['types']:
            self.mixer.set_speed(1.0 + 0.25*speed['count'])
            is_valid = True
        elif "SLOW" in speed['types']:
            rate = 1
            for i in range(speed['count']):
                rate = rate * 0.75
            self.mixer.set_speed(rate)
            is_valid = True
        if is_valid:
            time.sleep(15)
            self.mixer.set_speed(1)
        self.remove_top_queue()
        self.mixer.emit('speed', self.queue_redis["speed"])


    def run(self):
        while True:
            if not self.mixer.pause and self.queue_redis['speed']:
                self.current_speed = self.queue_redis['speed'][0]
                self.set_speed(speed=self.current_speed)
            time.sleep(.1)


class Mixer(Thread):
    def __init__(self):
        super().__init__()
        import pygame

        self.config = RedisDict(namespace='config')
        self.queue_redis = RedisDict(namespace='queue')
        self.pk_redis = RedisDict(namespace='pk')
        if 'queue' not in self.queue_redis:
            self.queue_redis['queue'] = list()
        self.mixer = pygame.mixer
        self.mixer.init()
        self.channel_bg_music = self.mixer.Channel(0)
        self.channel_pk_music = self.mixer.Channel(1)
        self.channel_gift_music = MediaPlayer()
        self.pause = True
        self.current_gift: Optional[dict] = None
        self.current_background_music = None
        self.emit = None
        self.update_background_music()
        self.controller = Controller(mixer=self)
        self.controller.start()
        self.pk = False

    def start_pk(self):
        self.pk = 1

    def stop_pk(self):
        self.pk = False

    def ready(self):
        self.pause = False
        self.emit('toast')

    def update_background_music(self):
        if 'background_music' in self.config:
            if self.config['background_music'] and self.current_background_music != self.config['background_music']:
                self.current_background_music = self.config['background_music']
                self.channel_bg_music.play(Sound(self.current_background_music), loops=-1)

    def set_speed(self, rate):
        self.channel_gift_music.set_rate(rate)

    def add_speed(self, gift: GiftConfig, count):
        current_queue = self.queue_redis['speed']
        gift_dict = gift.dict()
        gift_dict['count'] = count
        current_queue.append(gift_dict)
        self.queue_redis['speed'] = current_queue
        log.info(f'Thêm {"FAST" if "FAST" in gift.types else "SLOW"}, vị trí {len(self.queue_redis["queue"])}')

    def add(self, gift: GiftConfig):
        current_queue = self.queue_redis['queue']
        current_queue.append(gift.dict())
        self.queue_redis['queue'] = current_queue
        log.info(f'Thêm {gift.name}, vị trí {len(self.queue_redis["queue"])}')

    def add_priority(self, gift: GiftConfig):
        gc: dict
        i = 0
        if self.queue_redis['queue']:
            for i, gc in enumerate(self.queue_redis['queue']):
                if 'PRIORITY' not in gc['types']:
                    self.queue_redis['queue'].insert(i, gift.dict())
                    current_queue = self.queue_redis['queue']
                    current_queue.insert(i, gift.dict())
                    self.queue_redis['queue'] = current_queue
                    break
                else:
                    if gift.price > gc['price']:
                        current_queue = self.queue_redis['queue']
                        current_queue.insert(i, gift.dict())
                        self.queue_redis['queue'] = current_queue
                        break
        else:
            current_queue = self.queue_redis['queue']
            current_queue.insert(i, gift.dict())
            self.queue_redis['queue'] = current_queue
        log.info(f'Thêm ưu tiên {gift.name}, vị trí {i + 1}')

    def reset(self):
        count = 0
        gift = self.current_gift
        current_queue = self.queue_redis['queue']
        for gc in current_queue[:]:
            if gc['id'] == gift['id']:
                current_queue.remove(gc)
                count += 1
        self.queue_redis['queue'] = current_queue
        log.info(f'Loại {gift["name"]} ra khỏi danh sách phát ({count} bài)')

    def reset_all(self):
        count = len(self.queue_redis['queue'])
        self.queue_redis['queue'] = list()
        self.queue_redis['speed'] = list()
        log.info(f'Loại toàn bộ danh sách phát ({count} bài)')

    def remove_top_queue(self) -> dict:
        current_queue = self.queue_redis['queue']
        if current_queue:
            gift = current_queue.pop(0)
            self.queue_redis['queue'] = current_queue
            return gift

    def play_and_wait(self, path):
        self.channel_gift_music.set_media(Media(path))
        self.channel_gift_music.play()
        while self.channel_gift_music.get_state() != State(6):
            time.sleep(.5)

    def socket_update_queue(self):
        self.emit('pause_state', self.pause)
        self.emit('queue', self.queue_redis["queue"])
        self.emit('speed', self.queue_redis["speed"])

    def play(self, gift: dict):
        self.socket_update_queue()

        sound = random.choice(gift['sound'])
        if sound:
            log.info(
                f'Đang phát {gift["name"]}, danh sách phát {len(self.queue_redis["queue"])} bài')
            self.channel_bg_music.pause()
            try:
                if self.config['cross_music'] and os.path.exists(self.config['cross_music']):
                    self.play_and_wait(self.config['cross_music'])

                self.play_and_wait(sound)
                self.remove_top_queue()

                self.socket_update_queue()

                time.sleep(self.config['play_delay'])
            except error:
                log.critical(f'Bỏ qua {gift["name"]}, file nhạc lỗi {sound}')

        else:
            log.critical(f'Bỏ qua {gift["name"]}, config nhạc lỗi {sound}')

    def run(self):
        while True:
            if not self.pause and self.queue_redis['queue']:
                self.current_gift = self.queue_redis['queue'][0]
                self.play(gift=self.current_gift)
            if not self.queue_redis['queue'] and not self.pause:
                self.channel_bg_music.unpause()
            if self.pk:
                sounds = self.pk_redis['sounds']
                if self.pk > len(sounds):
                    self.pk = 1
                self.channel_pk_music.play(Sound(sounds[self.pk-1]), loops=0)
                while self.channel_pk_music.get_busy():
                    time.sleep(.5)
                if self.pk:
                    self.pk += 1
            time.sleep(.1)
