import time

from TikTokLive import TikTokLiveClient
from threading import Thread
from TikTokLive.types.events import CommentEvent, ConnectEvent, DisconnectEvent, GiftEvent
from module.log import get_logger
from module.app import TikTokDance
from redis_dict import RedisDict

log = get_logger(__name__)


class TikTok(Thread):
    def __init__(self, app: TikTokDance, emit):
        super().__init__()
        self.emit = emit
        self.config = RedisDict('config')
        self.room_id = self.config['room_id']
        self.client = TikTokLiveClient(unique_id=f'@{self.room_id}')
        # Define handling an event via a "callback"
        self.client.add_listener("comment", self.on_comment)
        self.client.add_listener("connect", self.on_connect)
        self.client.add_listener("disconnect", self.on_disconnect)
        self.client.add_listener("error", self.on_connect)
        self.client.add_listener("gift", self.on_gift)
        self.app = app

    async def update_available_gifts(self):
        await self.client.retrieve_available_gifts()
        self.app.update_available_gifts(gifts=self.client.available_gifts)

    async def on_connect(self, _: ConnectEvent):
        log.debug(f"Đã kết nối với room {self.room_id}")
        self.emit('tiktok_client_connect', {'success': True, 'msg': self.room_id})
        await self.client.retrieve_available_gifts()
        self.app.update_available_gifts(gifts=self.client.available_gifts)

    async def on_disconnect(self, event: DisconnectEvent):
        log.critical(f'Mất kết nối với room {self.room_id}')

    async def on_error(self, error: Exception):
        log.critical(f'Lỗi chưa rõ nguyên nhân: {error}')

    async def on_comment(self, event: CommentEvent):
        # log.debug(f"{event.user.nickname}: {event.comment}")
        pass

    async def on_gift(self, event: GiftEvent):
        self.app.on_gift(event)

    def run(self):
        from TikTokLive.types.errors import FailedFetchRoomInfo
        try:
            self.client.run()
        except FailedFetchRoomInfo:
            self.emit('tiktok_client_connect', {'success': False, 'msg': 'Room ID không hợp lệ'})
            log.critical('Room ID không hợp lệ')
        except Exception as e:
            if 'likely offline' in str(e):
                self.emit('tiktok_client_connect', {'success': False, 'msg': 'Live stream chưa bắt đầu'})
                log.critical(f'Live stream chưa bắt đầu')
            else:
                self.emit('tiktok_client_connect', {'success': False, 'msg': f'Lỗi chưa rõ nguyên nhân {e}'})
                log.critical(f'Lỗi chưa rõ nguyên nhân: {e}')
