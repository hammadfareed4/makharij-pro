"""Live rule feedback may be corrected as later audio adds context."""

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.routers.live import _send_verdicts  # noqa: E402


class _Socket:
    def __init__(self):
        self.messages = []

    async def send_text(self, value):
        self.messages.append(json.loads(value))


def _payload(correct, rule):
    return [{
        "type": "ayah_result",
        "surah": 1,
        "ayah": 2,
        "words": [{
            "word_index": 1,
            "word": "لِلَّهِ",
            "correct": correct,
            "error_type": rule,
        }],
    }]


def test_changed_live_verdict_is_resent_but_identical_one_is_not():
    socket = _Socket()
    sent = {}

    asyncio.run(_send_verdicts(socket, _payload(False, "madd"), sent))
    asyncio.run(_send_verdicts(socket, _payload(False, "madd"), sent))
    asyncio.run(_send_verdicts(socket, _payload(False, "shaddah"), sent))
    asyncio.run(_send_verdicts(socket, _payload(True, None), sent))

    assert [m["words"][0]["error_type"] for m in socket.messages] == [
        "madd",
        "shaddah",
        None,
    ]
    assert socket.messages[-1]["words"][0]["correct"] is True
