"""Global fixtures for openevse integration."""

from collections.abc import Coroutine, Generator
import json
import os
from unittest import mock
from unittest.mock import patch
from typing import Any, cast

import openevsehttp.__main__ as main
import pytest
from aioresponses import aioresponses

from homeassistant.core import (
    HomeAssistant,
)
from homeassistant.setup import async_setup_component
from homeassistant.components.websocket_api.http import URL
from homeassistant.components.websocket_api.auth import (
    TYPE_AUTH,
    TYPE_AUTH_OK,
    TYPE_AUTH_REQUIRED,
)
from .typing import (
    ClientSessionGenerator,
    MockHAClientWebSocket,
    WebSocketGenerator,
)

from tests.const import CHARGER_DATA, FW_DATA, GETFW_DATA

pytest_plugins = "pytest_homeassistant_custom_component"

TEST_URL_GITHUB = (
    "https://api.github.com/repos/OpenEVSE/ESP32_WiFi_V4.x/releases/latest"
)
TEST_URL_STATUS = "http://openevse.test.tld/status"
TEST_URL_CONFIG = "http://openevse.test.tld/config"
TEST_URL_OVERRIDE = "http://openevse.test.tld/override"
TEST_URL_CLAIMS = "http://openevse.test.tld/claims"
TEST_URL_CLAIMS_TARGET = "http://openevse.test.tld/claims/target"
TEST_URL_RAPI = "http://openevse.test.tld/r"
TEST_URL_WS = "ws://openevse.test.tld/ws"
TEST_TLD = "openevse.test.tld"


# This fixture enables loading custom integrations in all tests.
# Remove to enable selective use of this fixture
@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable custom integration tests."""
    yield


# This fixture is used to prevent HomeAssistant from attempting to create and dismiss persistent
# notifications. These calls would fail without this fixture since the persistent_notification
# integration is never loaded during a test.
@pytest.fixture(name="skip_notifications", autouse=True)
def skip_notifications_fixture():
    """Skip notification calls."""
    with patch("homeassistant.components.persistent_notification.async_create"), patch(
        "homeassistant.components.persistent_notification.async_dismiss"
    ):
        yield


@pytest.fixture()
def mock_charger():
    """Mock charger data."""
    with patch(
        "custom_components.openevse.OpenEVSEUpdateCoordinator._async_update_data"
    ) as mock_value, patch(
        "custom_components.openevse.OpenEVSEFirmwareCheck._async_update_data"
    ) as mock_fw_value:
        mock_value.return_value = CHARGER_DATA
        mock_fw_value.return_value = FW_DATA
        yield


@pytest.fixture()
def mock_fw_get():
    """Mock charger fw data."""
    with patch("custom_components.openevse.get_firmware") as mock_value:
        mock_value.return_value = GETFW_DATA
        yield mock_value


@pytest.fixture()
def mock_ws_start():
    """Mock charger fw data."""
    with patch("custom_components.openevse.OpenEVSE.ws_start") as mock_value:
        mock_value.return_value = True
        yield mock_value


@pytest.fixture(name="test_charger")
def test_charger(mock_aioclient):
    """Load the charger data."""
    mock_aioclient.get(
        TEST_URL_STATUS,
        status=200,
        body=load_fixture("status.json"),
        repeat=True,
    )
    mock_aioclient.post(
        TEST_URL_STATUS,
        status=200,
        body='{ "msg": "OK" }',
        repeat=True,
    )
    mock_aioclient.get(
        TEST_URL_CONFIG,
        status=200,
        body=load_fixture("config.json"),
        repeat=True,
    )
    mock_aioclient.get(
        TEST_URL_WS,
        status=101,
        body=load_fixture("status.json"),
        repeat=True,
    )
    mock_aioclient.get(
        TEST_URL_GITHUB,
        status=200,
        body=load_fixture("github.json"),
        repeat=True,
    )
    mock_aioclient.post(
        TEST_URL_OVERRIDE,
        status=200,
        body='{ "msg": "OK" }',
        repeat=True,
    )
    mock_aioclient.patch(
        TEST_URL_OVERRIDE,
        status=200,
        body='{ "msg": "OK" }',
        repeat=True,
    )
    mock_aioclient.get(
        TEST_URL_OVERRIDE,
        status=200,
        body="{}",
        repeat=True,
    )
    mock_aioclient.get(
        TEST_URL_CLAIMS_TARGET,
        status=200,
        body='{"properties":{"state":"disabled","charge_current":28,"max_current":23,"auto_release":false},"claims":{"state":65540,"charge_current":65537,"max_current":65548}}',
        repeat=True,
    )
    return main.OpenEVSE(TEST_TLD)


@pytest.fixture(name="test_charger_services")
def test_charger_services(mock_aioclient):
    """Load the charger data."""
    mock_aioclient.get(
        TEST_URL_STATUS,
        status=200,
        body=load_fixture("status.json"),
        repeat=True,
    )
    mock_aioclient.post(
        TEST_URL_STATUS,
        status=200,
        body='{ "msg": "OK" }',
        repeat=True,
    )
    mock_aioclient.get(
        TEST_URL_CONFIG,
        status=200,
        body=load_fixture("config.json"),
        repeat=True,
    )
    mock_aioclient.get(
        TEST_URL_WS,
        status=101,
        body=load_fixture("status.json"),
        repeat=True,
    )
    mock_aioclient.get(
        TEST_URL_GITHUB,
        status=200,
        body=load_fixture("github.json"),
        repeat=True,
    )
    mock_aioclient.post(
        TEST_URL_OVERRIDE,
        status=200,
        body='{ "msg": "OK" }',
        repeat=True,
    )
    mock_aioclient.get(
        TEST_URL_CLAIMS_TARGET,
        status=200,
        body='{"properties":{"state":"disabled","charge_current":28,"max_current":23,"auto_release":false},"claims":{"state":65540,"charge_current":65537,"max_current":65548}}',
        repeat=True,
    )
    return main.OpenEVSE(TEST_TLD)


@pytest.fixture(name="test_charger_bad_serial")
def test_charger_bad_serial(mock_aioclient):
    """Load the charger data."""
    mock_aioclient.get(
        TEST_URL_STATUS,
        status=200,
        body=load_fixture("status.json"),
        repeat=True,
    )
    mock_aioclient.get(
        TEST_URL_CONFIG,
        status=200,
        body=load_fixture("config-no-serial.json"),
        repeat=True,
    )
    mock_aioclient.get(
        TEST_URL_WS,
        status=101,
        body=load_fixture("status.json"),
        repeat=True,
    )
    mock_aioclient.get(
        TEST_URL_GITHUB,
        status=200,
        body=load_fixture("github.json"),
        repeat=True,
    )
    mock_aioclient.get(
        TEST_URL_CLAIMS_TARGET,
        status=200,
        body='{"properties":{"state":"disabled","charge_current":28,"max_current":23,"auto_release":false},"claims":{"state":65540,"charge_current":65537,"max_current":65548}}',
        repeat=True,
    )
    mock_aioclient.get(
        TEST_URL_OVERRIDE,
        status=200,
        body="{}",
        repeat=True,
    )
    return main.OpenEVSE(TEST_TLD)


@pytest.fixture(name="test_charger_bad_post")
def test_charger_bad_post(mock_aioclient):
    """Load the charger data."""
    mock_aioclient.get(
        TEST_URL_STATUS,
        status=200,
        body=load_fixture("status.json"),
        repeat=True,
    )
    mock_aioclient.post(
        TEST_URL_STATUS,
        exception=TimeoutError,
        repeat=True,
    )
    mock_aioclient.get(
        TEST_URL_CONFIG,
        status=200,
        body=load_fixture("config.json"),
        repeat=True,
    )
    mock_aioclient.get(
        TEST_URL_WS,
        status=101,
        body=load_fixture("status.json"),
        repeat=True,
    )
    mock_aioclient.get(
        TEST_URL_GITHUB,
        status=200,
        body=load_fixture("github.json"),
        repeat=True,
    )
    mock_aioclient.get(
        TEST_URL_CLAIMS_TARGET,
        status=200,
        body='{"properties":{"state":"disabled","charge_current":28,"max_current":23,"auto_release":false},"claims":{"state":65540,"charge_current":65537,"max_current":65548}}',
        repeat=True,
    )
    mock_aioclient.get(
        TEST_URL_OVERRIDE,
        status=200,
        body="{}",
        repeat=True,
    )
    return main.OpenEVSE(TEST_TLD)


@pytest.fixture(name="test_charger_new")
def test_charger_new(mock_aioclient):
    """Load the charger data."""
    mock_aioclient.get(
        TEST_URL_STATUS,
        status=200,
        body=load_fixture("status-new.json"),
        repeat=True,
    )
    mock_aioclient.post(
        TEST_URL_STATUS,
        status=200,
        body='{ "msg": "OK" }',
        repeat=True,
    )
    mock_aioclient.get(
        TEST_URL_CONFIG,
        status=200,
        body=load_fixture("config.json"),
        repeat=True,
    )
    mock_aioclient.get(
        TEST_URL_WS,
        status=101,
        body=load_fixture("status-new.json"),
        repeat=True,
    )
    mock_aioclient.get(
        TEST_URL_GITHUB,
        status=200,
        body=load_fixture("github.json"),
        repeat=True,
    )
    mock_aioclient.post(
        TEST_URL_OVERRIDE,
        status=200,
        body='{ "msg": "OK" }',
        repeat=True,
    )
    mock_aioclient.get(
        TEST_URL_OVERRIDE,
        status=200,
        body="{}",
        repeat=True,
    )
    mock_aioclient.get(
        TEST_URL_CLAIMS_TARGET,
        status=200,
        body='{"properties":{"state":"disabled","charge_current":28,"max_current":23,"auto_release":false},"claims":{"state":65540,"charge_current":65537,"max_current":65548}}',
        repeat=True,
    )
    return main.OpenEVSE(TEST_TLD)


@pytest.fixture()
def mock_manager():
    """Mock manager."""
    with patch("custom_components.openevse.OpenEVSEManager") as mock_value:
        mock_value.url.return_value = "http://localhost"
        yield


@pytest.fixture
def mock_aioclient():
    """Fixture to mock aioclient calls."""
    with aioresponses(passthrough=["http://127.0.0.1"]) as m:
        yield m


def load_fixture(filename):
    """Load a fixture."""
    path = os.path.join(os.path.dirname(__file__), "fixtures", filename)
    with open(path, encoding="utf-8") as fptr:
        return fptr.read()


@pytest.fixture(name="test_charger_v2")
def test_charger_v2(mock_aioclient):
    """Load the charger data."""
    mock_aioclient.get(
        TEST_URL_STATUS,
        status=200,
        body=load_fixture("v2_status.json"),
        repeat=True,
    )
    mock_aioclient.post(
        TEST_URL_STATUS,
        status=200,
        body='{ "msg": "OK" }',
        repeat=True,
    )
    mock_aioclient.get(
        TEST_URL_CONFIG,
        status=200,
        body=load_fixture("v2_config.json"),
        repeat=True,
    )
    mock_aioclient.get(
        TEST_URL_WS,
        status=101,
        body=load_fixture("v2_status.json"),
        repeat=True,
    )
    mock_aioclient.get(
        TEST_URL_GITHUB,
        status=200,
        body=load_fixture("v2_github.json"),
        repeat=True,
    )
    mock_aioclient.post(
        TEST_URL_OVERRIDE,
        status=404,
        body="{}",
        repeat=True,
    )
    mock_aioclient.get(
        TEST_URL_OVERRIDE,
        status=404,
        body="{}",
        repeat=True,
    )
    mock_aioclient.get(
        TEST_URL_CLAIMS_TARGET,
        status=404,
        body="{}",
        repeat=True,
    )
    return main.OpenEVSE(TEST_TLD)


@pytest.fixture
def hass_ws_client(
    aiohttp_client: ClientSessionGenerator,
    hass_access_token: str,
    hass: HomeAssistant,
    socket_enabled: None,
) -> WebSocketGenerator:
    """Websocket client fixture connected to websocket server."""

    async def create_client(
        hass: HomeAssistant = hass, access_token: str | None = hass_access_token
    ) -> MockHAClientWebSocket:
        """Create a websocket client."""
        assert await async_setup_component(hass, "websocket_api", {})
        client = await aiohttp_client(hass.http.app)
        websocket = await client.ws_connect(URL)
        auth_resp = await websocket.receive_json()
        assert auth_resp["type"] == TYPE_AUTH_REQUIRED

        if access_token is None:
            await websocket.send_json({"type": TYPE_AUTH, "access_token": "incorrect"})
        else:
            await websocket.send_json({"type": TYPE_AUTH, "access_token": access_token})

        auth_ok = await websocket.receive_json()
        assert auth_ok["type"] == TYPE_AUTH_OK

        def _get_next_id() -> Generator[int]:
            i = 0
            while True:
                yield (i := i + 1)

        id_generator = _get_next_id()

        def _send_json_auto_id(data: dict[str, Any]) -> Coroutine[Any, Any, None]:
            data["id"] = next(id_generator)
            return websocket.send_json(data)

        async def _remove_device(device_id: str, config_entry_id: str) -> Any:
            await _send_json_auto_id(
                {
                    "type": "config/device_registry/remove_config_entry",
                    "config_entry_id": config_entry_id,
                    "device_id": device_id,
                }
            )
            return await websocket.receive_json()

        # wrap in client
        wrapped_websocket = cast(MockHAClientWebSocket, websocket)
        wrapped_websocket.client = client
        wrapped_websocket.send_json_auto_id = _send_json_auto_id
        wrapped_websocket.remove_device = _remove_device
        return wrapped_websocket

    return create_client
