"""Global fixtures for openevse integration."""

from unittest import mock
from unittest.mock import patch

import json

import pytest
from openevsehttp.__main__ import OpenEVSE

from tests.const import CHARGER_DATA, GETFW_DATA, FW_DATA

pytest_plugins = "pytest_homeassistant_custom_component"


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
def mock_library():
    """Mock library."""
    with patch("custom_components.openevse.OpenEVSE") as mock_value:
        mock_value.ws_start.return_value = True
        mock_value.url.return_value = "http://localhost"

        yield mock_value


@pytest.fixture()
def mock_manager():
    """Mock manager."""
    with patch("custom_components.openevse.OpenEVSEManager") as mock_value:
        mock_value.url.return_value = "http://localhost"
        yield
