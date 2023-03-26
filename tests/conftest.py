"""Global fixtures for openevse integration."""

from aioresponses import aioresponses
from unittest import mock
from unittest.mock import patch

import json
import os

import pytest
import openevsehttp.__main__ as main

from tests.const import CHARGER_DATA, GETFW_DATA, FW_DATA

pytest_plugins = "pytest_homeassistant_custom_component"

TEST_URL_GITHUB = (
    "https://api.github.com/repos/OpenEVSE/ESP32_WiFi_V4.x/releases/latest"
)
TEST_URL_STATUS = "http://openevse.test.tld/status"
TEST_URL_CONFIG = "http://openevse.test.tld/config"
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
    mock_aioclient.get(
        TEST_URL_CONFIG,
        status=200,
        body=load_fixture("config.json"),
        repeat=True,
    )
    mock_aioclient.get(
        TEST_URL_WS,
        status=200,
        body=load_fixture("status.json"),
        repeat=True,
    )
    mock_aioclient.get(
        TEST_URL_GITHUB,
        status=200,
        body=load_fixture("github.json"),
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
        status=200,
        body=load_fixture("status.json"),
        repeat=True,
    )
    mock_aioclient.get(
        TEST_URL_GITHUB,
        status=200,
        body=load_fixture("github.json"),
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
    with aioresponses() as m:
        yield m


def load_fixture(filename):
    """Load a fixture."""
    path = os.path.join(os.path.dirname(__file__), "fixtures", filename)
    with open(path, encoding="utf-8") as fptr:
        return fptr.read()
