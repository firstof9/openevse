"""Test config flow."""

from unittest.mock import patch

import pytest
from ipaddress import ip_address
from homeassistant.helpers.service_info.zeroconf import ZeroconfServiceInfo
from homeassistant import config_entries, data_entry_flow, setup
from homeassistant.const import CONF_HOST, CONF_NAME
from homeassistant.data_entry_flow import FlowResult, FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.openevse.const import DOMAIN
from tests.const import CONFIG_DATA

CHARGER_NAME = "openevse"

pytestmark = pytest.mark.asyncio


@pytest.mark.parametrize(
    "input,step_id,title,data",
    [
        (
            {
                "name": "openevse",
                "host": "openevse.test.tld",
                "username": "",
                "password": "",
                "grid": "",
                "solar": "",
                "voltage": "",
                "invert_grid": False,
            },
            "user",
            "openevse",
            {
                "name": "openevse",
                "host": "openevse.test.tld",
                "username": "",
                "password": "",
                "grid": "",
                "solar": "",
                "voltage": "",
                "invert_grid": False,
            },
        ),
    ],
)
async def test_form_user(
    input,
    step_id,
    title,
    data,
    hass,
    test_charger,
    mock_ws_start,
):
    """Test we get the form."""
    await setup.async_setup_component(hass, "persistent_notification", {})
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == step_id

    with patch(
        "custom_components.openevse.async_setup_entry",
        return_value=True,
    ) as mock_setup_entry, patch(
        "custom_components.openevse.OpenEVSE.update", return_value=True
    ), patch(
        "custom_components.openevse.OpenEVSE.ws_disconnect", return_value=True
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], input
        )

        assert result["type"] == FlowResultType.CREATE_ENTRY
        assert result["title"] == title
        assert result["data"] == data

        await hass.async_block_till_done()
        assert len(mock_setup_entry.mock_calls) == 1


@pytest.mark.parametrize(
    "input,step_id,title,data",
    [
        (
            {
                "name": "openevse",
                "host": "openevse.test.tld",
                "username": "",
                "password": "",
                "grid": "",
                "solar": "",
                "voltage": "",
                "invert_grid": False,
            },
            "user",
            "openevse",
            {
                "name": "openevse",
                "host": "openevse.test.tld",
                "username": "",
                "password": "",
                "grid": "",
                "solar": "",
                "voltage": "",
                "invert_grid": False,
            },
        ),
    ],
)
async def test_form_user_connection_error(
    input,
    step_id,
    title,
    data,
    hass,
):
    """Test we get the an error on form."""
    await setup.async_setup_component(hass, "persistent_notification", {})
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == step_id

    result = await hass.config_entries.flow.async_configure(result["flow_id"], input)

    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {"host": "communication"}
    await hass.async_block_till_done()


@pytest.mark.parametrize(
    "input,step_id,title,data",
    [
        (
            {
                "name": "openevse",
                "host": "openevse.test.tld",
                "username": "",
                "password": "",
                "grid": "sensor.grid_power",
                "solar": "",
                "voltage": "",
                "invert_grid": False,
            },
            "reconfigure",
            "openevse",
            {
                "name": "openevse",
                "host": "openevse.test.tld",
                "username": "",
                "password": "",
                "grid": "sensor.grid_power",
                "solar": "",
                "voltage": "",
                "invert_grid": False,
            },
        ),
    ],
)
async def test_form_reconfigure(
    input,
    step_id,
    title,
    data,
    hass,
    test_charger,
    mock_ws_start,
):
    """Test we get the form."""
    await setup.async_setup_component(hass, "persistent_notification", {})
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=CHARGER_NAME,
        data=CONFIG_DATA,
    )
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    reconfigure_result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={
            "source": config_entries.SOURCE_RECONFIGURE,
            "entry_id": entry.entry_id,
        },
    )
    assert reconfigure_result["type"] is FlowResultType.FORM
    assert reconfigure_result["step_id"] == step_id

    result = await hass.config_entries.flow.async_configure(
        reconfigure_result["flow_id"], input
    )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "reconfigure_successful"
    await hass.async_block_till_done()

    entry = hass.config_entries.async_entries(DOMAIN)[0]
    assert entry.data.copy() == data


@pytest.mark.parametrize(
    "input,step_id",
    [
        (
            {
                "name": "openevse",
                "host": "openevse.test2.tld",
                "username": "",
                "password": "",
                "grid": "sensor.grid_power",
                "solar": "",
                "voltage": "",
                "invert_grid": False,
            },
            "reconfigure",
        ),
    ],
)
async def test_form_reconfigure_connect_error(
    input,
    step_id,
    hass,
    test_charger,
    mock_ws_start,
):
    """Test we get the form."""
    await setup.async_setup_component(hass, "persistent_notification", {})
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=CHARGER_NAME,
        data=CONFIG_DATA,
    )
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    reconfigure_result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={
            "source": config_entries.SOURCE_RECONFIGURE,
            "entry_id": entry.entry_id,
        },
    )
    assert reconfigure_result["type"] is FlowResultType.FORM
    assert reconfigure_result["step_id"] == step_id

    result = await hass.config_entries.flow.async_configure(
        reconfigure_result["flow_id"], input
    )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"host": "communication"}
    await hass.async_block_till_done()


async def test_zeroconf_discovery(hass, mock_ws_start, mock_aioclient):
    """Test zeroconf discovery."""
    await setup.async_setup_component(hass, "persistent_notification", {})
    
    # Simulate a Zeroconf discovery packet
    discovery_info = ZeroconfServiceInfo(
        ip_address=ip_address("192.168.1.123"),
        ip_addresses=[ip_address("192.168.1.123")],
        hostname="openevse-1234.local.",
        name="openevse-1234._openevse._tcp.local.",
        port=80,
        properties={"id": "1234", "type": "openevse"},
        type="_openevse._tcp.local.",
    )

    # Mock setup and connection methods
    with patch(
        "custom_components.openevse.async_setup_entry",
        return_value=True,
    ) as mock_setup_entry, patch(
        "custom_components.openevse.OpenEVSE.update", return_value=True
    ), patch(
        "custom_components.openevse.OpenEVSE.ws_disconnect", return_value=True
    ):
        # Trigger the zeroconf step
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": config_entries.SOURCE_ZEROCONF},
            data=discovery_info,
        )

        # Should present a confirmation form
        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "discovery_confirm"
        assert result["description_placeholders"] == {"name": "OpenEVSE: openevse-1234"}

        # Confirm the discovery
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], user_input={}
        )

        # Should create the entry
        assert result["type"] == FlowResultType.CREATE_ENTRY
        assert result["title"] == "OpenEVSE: openevse-1234"
        assert result["data"][CONF_HOST] == "192.168.1.123"