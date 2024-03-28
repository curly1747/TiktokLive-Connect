import time

from TikTokLive import TikTokLiveClient
from threading import Thread
from TikTokLive.events.proto_events import CommentEvent, GiftEvent
from TikTokLive.events.custom_events import ConnectEvent, DisconnectEvent, UnknownEvent
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
        self.client.add_listener(CommentEvent, self.on_comment)
        self.client.add_listener(ConnectEvent, self.on_connect)
        self.client.add_listener(DisconnectEvent, self.on_disconnect)
        self.client.add_listener(UnknownEvent, self.on_connect)
        self.client.add_listener(GiftEvent, self.on_gift)
        self.app = app

    async def update_available_gifts(self):
        while not self.client.gift_info:
            time.sleep(.5)
        self.app.update_available_gifts(gifts=self.client.gift_info)

    async def on_connect(self, _: ConnectEvent):
        log.debug(f"Đã kết nối với room {self.room_id}")
        self.emit('tiktok_client_connect', {'success': True, 'msg': self.room_id})
        self.app.update_available_gifts(gifts=self.client.gift_info)

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
        from TikTokLive.client.errors import AlreadyConnectedError, UserOfflineError, InitialCursorMissingError, WebsocketURLMissingError

        msg = False
        try:
            self.client.run(fetch_gift_info=True)
        except AlreadyConnectedError:
            msg = 'Đã kết nối từ trước đó'
        except UserOfflineError:
            msg = 'Live stream chưa bắt đầu'
        except InitialCursorMissingError:
            msg = 'Cursor for connecting to TikTok is missing (blocked)'
        except WebsocketURLMissingError:
            msg = 'The websocket URL to connect to TikTok is missing (blocked)'
        except Exception as e:
            msg=f'Lỗi chưa rõ nguyên nhân {e}'
        finally:
            if msg:
                self.emit('tiktok_client_connect', {'success': False, 'msg': msg})
                log.critical(msg)
