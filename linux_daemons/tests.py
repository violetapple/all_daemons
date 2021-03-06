import sys
import os
import asyncio
sys.path.append("".join(x + '/' for x in
                (os.path.abspath(__file__).split('/')[:-2])))
from linux_daemons import views
import unittest


class TestDaemonController(unittest.TestCase):
    async def test_correct_start(self):
        await views.start_daemon()
        is_started = await views.is_daemon_running()
        self.assertTrue(is_started)

    async def test_correct_stop(self):
        await views.stop_daemon()
        is_started = await views.is_daemon_running()
        self.assertFalse(is_started)

    async def test_correct_restart(self):
        await views.restart_daemon()
        is_started = await views.is_daemon_running()
        self.assertTrue(is_started)

unittest.main()

