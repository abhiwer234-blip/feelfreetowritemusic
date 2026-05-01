from collections import defaultdict, deque
from dataclasses import dataclass


@dataclass
class Track:
    title: str
    url: str
    duration: int | None
    file_path: str
    requested_by: str


class MusicQueue:
    def __init__(self) -> None:
        self._queues: dict[int, deque[Track]] = defaultdict(deque)
        self._current: dict[int, Track] = {}

    def add(self, chat_id: int, track: Track) -> int:
        self._queues[chat_id].append(track)
        return len(self._queues[chat_id])

    def pop_next(self, chat_id: int) -> Track | None:
        if not self._queues[chat_id]:
            self._current.pop(chat_id, None)
            return None
        track = self._queues[chat_id].popleft()
        self._current[chat_id] = track
        return track

    def current(self, chat_id: int) -> Track | None:
        return self._current.get(chat_id)

    def list(self, chat_id: int) -> list[Track]:
        return list(self._queues[chat_id])

    def clear(self, chat_id: int) -> None:
        self._queues[chat_id].clear()
        self._current.pop(chat_id, None)
