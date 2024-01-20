import copy
import logging
from module.model import GiftConfig, Sound
from redis_dict import RedisDict
from TikTokLive.types.events import GiftEvent
from typing import Optional
from module.mixer import Mixer
from module.log import get_logger
import os
import json

log = get_logger(__name__)


class TikTokDance:
    def __init__(self, mixer):
        self.gift_config = RedisDict(namespace='gift_config')
        self.gifts: Optional[list[GiftConfig]] = list()
        self.mixer: Mixer = mixer
        self.config = RedisDict(namespace='config')
        self.pk = RedisDict(namespace='pk')
        self.pk_mode = False
        self.update_gift_config()

    def start_pk(self):
        self.mixer.channel_bg_music.pause()
        self.mixer.pause = True
        self.pk_mode = True

    def stop_pk(self):
        self.mixer.channel_bg_music.unpause()
        self.pk_mode = False
        self.mixer.emit('stop_pk', [self.pk['a_point'], self.pk['b_point']])

    def update_gift_config(self):
        if 'profile' not in self.config or not self.config['profile']:
            return

        name = self.config['profile']

        file_path = f'profile/{name}.json'

        is_valid = os.path.exists(file_path)
        if not is_valid:
            log.critical(f"Không tìm thấy profile '{name}'")
            return

        with open(file_path, mode='r', encoding='utf-8') as f:
            profile = json.load(f)

        self.gift_config.clear()
        for gift in profile['gift_config']:
            self.gift_config[gift['id']] = gift

        self.config['background_music'] = profile['background_music'] if 'background_music' in profile else ''

        self.config['cross_music'] = profile['cross_music'] if 'cross_music' in profile else ''

        self.prepare_gift_config()

        self.mixer.update_background_music()

        log.debug(f'Gift config updated')
        return

    def prepare_gift_config(self):

        for id, gc in self.gift_config.items():
            sounds = list()
            for path in gc['sounds']:
                sound = Sound(path=path)
                if sound.valid:
                    sounds.append(sound)
            gift = GiftConfig(
                id=gc['id'], name=gc['name'], thumbnail=gc['thumbnail'],
                types=gc['types'], sounds=sounds, price=gc['price']
            )
            self.gifts.append(gift)

    def add_pk_gift(self, gift_id, count):
        gift = None
        for gift in self.gifts:
            if gift_id == gift.id:
                gift = copy.deepcopy(gift)
                break
        if not gift:
            return

        valid = False
        for i in range(count):
            for team in ['a', 'b']:
                for id in self.pk[team]['gifts']:
                    if gift.id == id:
                        self.pk[f'{team}_point'] = self.pk[f'{team}_point'] + gift.price
                        valid = True

        if valid:
            self.mixer.emit('update_pk', [self.pk['a_point'], self.pk['b_point']])

    def add_queue(self, gift_id, count):
        if self.pk_mode:
            self.add_pk_gift(gift_id, count)
            return

        gift = None
        for gift in self.gifts:
            if gift_id == gift.id:
                gift = copy.deepcopy(gift)
                break
        if not gift:
            return

        for i in range(count):
            if not gift.types:
                self.mixer.add(gift)
            if "PRIORITY" in gift.types:
                self.mixer.add_priority(gift)
            if "RESCUE" in gift.types:
                self.mixer.reset()
            if "RESET" in gift.types:
                self.mixer.reset_all()
            if "FAST" in gift.types or "SLOW" in gift.types:
                self.mixer.add_speed(gift)

        self.mixer.emit('queue', self.mixer.queue_redis["queue"])
        self.mixer.emit('speed', self.mixer.queue_redis["speed"])

    def on_pk_gift(self, event: GiftEvent):
        count = 0
        log.debug(f'User {event.user.nickname} sent {count}x {event.gift.info.name}. {event.gift}')
        for gift in self.gifts:
            if event.gift.id == gift.id:
                count = event.gift.count
                gift = copy.deepcopy(gift)
                gift.user = event.user
                break

        valid = False
        for i in range(count):
            for team in ['a', 'b']:
                for id in self.pk[team]['gifts']:
                    if gift.id == id:
                        self.pk[f'{team}_point'] = self.pk[f'{team}_point'] + gift.price
                        self.mixer.emit('update_pk', [self.pk['a_point'], self.pk['b_point']])
                        valid = True

        if valid:
            self.mixer.emit('update_pk', [self.pk['a_point'], self.pk['b_point']])

    def on_gift(self, event: GiftEvent):
        if self.pk_mode:
            self.on_pk_gift(event)
            return

        count = 0
        if self.config['queue_type'] == "GIFT":
            if not event.gift.repeat_end:
                log.debug(f'User {event.user.nickname} sent {event.gift.info.name}. {event.gift}')
                for gift in self.gifts:
                    if event.gift.id == gift.id:
                        count = 1
                        gift = copy.deepcopy(gift)
                        gift.user = event.user
                        break
        else:
            if event.gift.repeat_end:
                log.debug(f'User {event.user.nickname} sent {count}x {event.gift.info.name}. {event.gift}')
                for gift in self.gifts:
                    if event.gift.id == gift.id:
                        count = event.gift.count
                        gift = copy.deepcopy(gift)
                        gift.user = event.user
                        break

        for i in range(count):
            if not gift.types:
                self.mixer.add(gift)
            if "PRIORITY" in gift.types:
                self.mixer.add_priority(gift)
            if "RESCUE" in gift.types:
                self.mixer.reset()
            if "RESET" in gift.types:
                self.mixer.reset_all()
            if "FAST" in gift.types or "SLOW" in gift.types:
                self.mixer.add_speed(gift)

        if count:
            self.mixer.emit('queue', self.mixer.queue_redis["queue"])
            self.mixer.emit('speed', self.mixer.queue_redis["speed"])

    def update_available_gifts(self, gifts):
        available_gifts = list()
        for i in gifts:
            gift = gifts[i]
            data = {'id': gift.id, 'price': gift.diamond_count, 'name': gift.name, 'thumbnail': gift.icon.urls[0]}
            available_gifts.append(data)
        self.config['available_gifts'] = available_gifts