from typing import Optional
import random
from os.path import exists as path_exits
# from TikTokLive.types.objects import User
from TikTokLive.proto.custom_proto import ExtendedUser as User


class Sound:
    def __init__(self, path):
        self.path = path
        self.valid = path_exits(path)


class GiftConfig:
    def __init__(self, id, name, thumbnail, price, types, sounds):
        self.id = id
        self.name = name
        self.thumbnail = thumbnail
        self.price = price
        self.types: Optional[list[str]] = types
        self.sounds: Optional[list[Sound]] = sounds
        self.picked_sound = None
        self.user: Optional[User] = None

    def dict(self):
        data = {
            'id': self.id,
            'name': self.name,
            'thumbnail': self.thumbnail,
            'price': self.price,
            'types': self.types,
            'sound': self.path_list(),
            'user': self.user.nickname if self.user else '',
            'ava': self.user.avatar_thumb.url_list[0] if self.user else '/static/images/ava.jpg'
        }
        return data

    def path_list(self):
        sounds = []
        for sound in self.sounds:
            if path_exits(sound.path):
                sounds.append(sound.path)
        return sounds

    def pick_sound(self):
        if self.sounds:
            retry = 0
            while not self.picked_sound and retry <= 5:
                picked: Sound = random.choice(self.sounds)
                if picked and path_exits(picked.path):
                    self.picked_sound = picked
        return self.picked_sound

    def __str__(self):
        return f'<GiftConfig {self.id} {self.types}>'