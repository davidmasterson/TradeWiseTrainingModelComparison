import unittest
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime, timedelta
from WebsocketUtility.websocket_runner import (
    add_new_user,
    monitor_new_users,
    on_message_async,
    start_user_websocket,
    reconnect_user,
    websocket_tasks,
    start_event_loop
)  
import asyncio
from concurrent.futures import Executor
from database import user_DAOIMPL
import json, logging, websocket, alpaca_request_methods, threading


class TestWebSocketScript(unittest.TestCase):
    @patch("asyncio.get_event_loop")
    @patch("executor.submit")
    def test_add_new_user(self, mock_submit, mock_get_event_loop):
        """Test add_new_user function."""
        mock_loop = MagicMock()
        mock_get_event_loop.return_value = mock_loop

        add_new_user("test_user", 1, "alpaca_key", "alpaca_secret", "alpaca_endpoint")

        mock_submit.assert_called_once()
        mock_get_event_loop.assert_called_once()

    @patch("user_DAOIMPL.get_all_users")
    @patch("websocket_runner.add_new_user")
    @patch("asyncio.sleep", new_callable=AsyncMock)
    def test_monitor_new_users(self, mock_sleep, mock_add_new_user, mock_get_all_users):
        """Test monitor_new_users function."""
        mock_get_all_users.return_value = [
            {"id": 1, "user_name": "user1", "alpaca_key": "key1", "alpaca_secret": "secret1", "alpaca_endpoint": "endpoint1"}
        ]
        mock_add_new_user.return_value = None

        # Create a coroutine to run monitor_new_users
        async def run_monitor():
            await monitor_new_users(interval=1)

        with patch("websocket_runner.websocket_tasks", {}):
            asyncio.run(run_monitor())

        mock_get_all_users.assert_called_once()
        mock_add_new_user.assert_called_once_with("user1", 1, "key1", "secret1", "endpoint1")
        mock_sleep.assert_awaited()

    @patch("json.loads")
    @patch("logging.error")
    async def test_on_message_async_json_decode_error(self, mock_logging_error, mock_json_loads):
        """Test on_message_async with a JSON decode error."""
        mock_json_loads.side_effect = json.JSONDecodeError("msg", "doc", 0)
        mock_ws = MagicMock()

        await on_message_async(mock_ws, b'invalid_message', "test_user", 1)

        mock_logging_error.assert_called_once_with("JSON decoding failed for user test_user: msg: line 1 column 1 (char 0)")

    @patch("websocket.WebSocketApp")
    def test_start_user_websocket(self, mock_websocket_app):
        """Test start_user_websocket function."""
        mock_websocket = MagicMock()
        mock_websocket_app.return_value = mock_websocket

        start_user_websocket(
            username="test_user",
            user_id=1,
            alpaca_key="key",
            alpaca_secret="secret",
            alpaca_endpoint="https://api.alpaca.markets",
        )

        mock_websocket.run_forever.assert_called_once()

    @patch("user_DAOIMPL.get_user_by_user_id")
    @patch("websocket_runner.add_new_user")
    @patch("time.sleep", return_value=None)
    def test_reconnect_user(self, mock_sleep, mock_add_new_user, mock_get_user):
        """Test reconnect_user function."""
        mock_get_user.return_value = {
            "user_name": "test_user",
            "id": 1,
            "alpaca_key": "key",
            "alpaca_secret": "secret",
            "alpaca_endpoint": "endpoint",
        }

        with patch("websocket_tasks", {1: MagicMock()}):
            reconnect_user(user_id=1)

        mock_add_new_user.assert_called_once_with(
            username="test_user",
            user_id=1,
            alpaca_key="key",
            alpaca_secret="secret",
            alpaca_endpoint="endpoint",
            max_retries=3,
            delay=10,
        )
        mock_sleep.assert_called()

    @patch("alpaca_request_methods.create_alpaca_api")
    def test_start_event_loop(self, mock_create_alpaca_api):
        """Test starting event loop."""
        loop = asyncio.new_event_loop()

        def run_loop():
            start_event_loop(loop)

        thread = threading.Thread(target=run_loop)
        thread.start()
        loop.call_soon_threadsafe(loop.stop)
        thread.join()

        mock_create_alpaca_api.assert_not_called()


if __name__ == "__main__":
    unittest.main()
