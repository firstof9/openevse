"""Test config flow."""

from ipaddress import ip_address
from unittest.mock import patch

import pytest
from homeassistant import config_entries, setup
from homeassistant.const import CONF_HOST
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.helpers.service_info.zeroconf import ZeroconfServiceInfo
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
                "name": "OpenEVSE Charger",
                "host": "openevse.test.tld",
                "username": "",
                "password": "",
            },
            "user",
            "OpenEVSE Charger",
            {
                "name": "OpenEVSE Charger",
                "host": "openevse.test.tld",
                "username": "",
                "password": "",
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

    with (
        patch(
            "custom_components.openevse.async_setup_entry",
            return_value=True,
        ) as mock_setup_entry,
        patch("custom_components.openevse.OpenEVSE.update", return_value=True),
        patch("custom_components.openevse.OpenEVSE.ws_disconnect", return_value=True),
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
            },
            "user",
            "openevse",
            {
                "name": "openevse",
                "host": "openevse.test.tld",
                "username": "",
                "password": "",
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
                "name": "OpenEVSE Charger",
                "host": "openevse.test.tld",
                "username": "",
                "password": "",
            },
            "reconfigure",
            "openevse",
            {
                "name": "OpenEVSE Charger",
                "host": "openevse.test.tld",
                "username": "",
                "password": "",
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
        version=2,
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
        version=2,
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
    with (
        patch(
            "custom_components.openevse.async_setup_entry",
            return_value=True,
        ),
        patch("custom_components.openevse.OpenEVSE.update", return_value=True),
        patch("custom_components.openevse.OpenEVSE.ws_disconnect", return_value=True),
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


async def test_zeroconf_no_serial(hass):
    """Test zeroconf discovery with missing serial number."""
    discovery_info = ZeroconfServiceInfo(
        ip_address=ip_address("192.168.1.123"),
        ip_addresses=[ip_address("192.168.1.123"), ip_address("2001:db8::1")],
        hostname="openevse-1234.local.",
        name="openevse-1234._openevse._tcp.local.",
        port=80,
        properties={"type": "openevse"},  # Missing 'id'
        type="_openevse._tcp.local.",
    )

    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_ZEROCONF},
        data=discovery_info,
    )

    assert result["type"] == FlowResultType.ABORT
    assert result["reason"] == "invalid_discovery_parameters"


async def test_zeroconf_connection_error(hass):
    """Test zeroconf discovery with connection failure."""
    discovery_info = ZeroconfServiceInfo(
        ip_address=ip_address("192.168.1.123"),
        ip_addresses=[ip_address("192.168.1.123"), ip_address("2001:db8::1")],
        hostname="openevse-1234.local.",
        name="openevse-1234._openevse._tcp.local.",
        port=80,
        properties={"id": "1234", "type": "openevse"},
        type="_openevse._tcp.local.",
    )

    # Mock update to raise an exception (simulating connection failure)
    with (
        patch(
            "custom_components.openevse.OpenEVSE.update",
            side_effect=Exception("Connection failed"),
        ),
        patch("custom_components.openevse.OpenEVSE.ws_disconnect", return_value=True),
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": config_entries.SOURCE_ZEROCONF},
            data=discovery_info,
        )

        assert result["type"] == FlowResultType.ABORT
        assert result["reason"] == "unknown_error"


async def test_zeroconf_already_configured_host(hass):
    """Test zeroconf discovery aborts if host is already configured."""
    # Create an existing entry with the same host
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={**CONFIG_DATA, "host": "192.168.1.123"},
        version=2,
    )
    entry.add_to_hass(hass)

    discovery_info = ZeroconfServiceInfo(
        ip_address=ip_address("192.168.1.123"),
        ip_addresses=[ip_address("192.168.1.123"), ip_address("2001:db8::1")],
        hostname="openevse-1234.local.",
        name="openevse-1234._openevse._tcp.local.",
        port=80,
        properties={"id": "1234", "type": "openevse"},
        type="_openevse._tcp.local.",
    )

    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_ZEROCONF},
        data=discovery_info,
    )

    # Should abort because the host matches an existing entry
    assert result["type"] == FlowResultType.ABORT
    assert result["reason"] == "already_configured"


async def test_zeroconf_already_configured_unique_id(hass):
    """Test zeroconf discovery updates info if unique_id is already configured."""
    # Create an existing entry with the same unique_id but different IP
    entry = MockConfigEntry(
        domain=DOMAIN,
        unique_id="OpenEVSE: openevse-1234_1234",
        data={**CONFIG_DATA, "host": "192.168.1.50"},
        version=2,
    )
    entry.add_to_hass(hass)

    discovery_info = ZeroconfServiceInfo(
        ip_address=ip_address("192.168.1.123"),
        ip_addresses=[ip_address("192.168.1.123"), ip_address("2001:db8::1")],
        hostname="openevse-1234.local.",
        name="openevse-1234._openevse._tcp.local.",
        port=80,
        properties={"id": "1234", "type": "openevse"},
        type="_openevse._tcp.local.",
    )

    with (
        patch("custom_components.openevse.OpenEVSE.update", return_value=True),
        patch("custom_components.openevse.OpenEVSE.ws_disconnect", return_value=True),
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": config_entries.SOURCE_ZEROCONF},
            data=discovery_info,
        )

        # Should abort because unique_id matches, but it updates the config entry
        assert result["type"] == FlowResultType.ABORT
        assert result["reason"] == "already_configured"

        # Verify the entry IP was updated to the new discovery IP
        assert entry.data["host"] == "192.168.1.123"


async def test_options_flow(hass, test_charger, mock_ws_start):
    """Test options flow for sensor configuration."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=CHARGER_NAME,
        data=CONFIG_DATA,
        version=2,
    )
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "init"

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={
            "grid": "sensor.grid_usage",
            "solar": "",
            "voltage": "sensor.grid_voltage",
            "shaper": "sensor.shaper_power",
            "invert_grid": False,
        },
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"] == {
        "grid": "sensor.grid_usage",
        "solar": "",
        "voltage": "sensor.grid_voltage",
        "shaper": "sensor.shaper_power",
        "invert_grid": False,
    }


async def test_options_flow_defaults(hass, test_charger, mock_ws_start):
    """Test options flow shows existing values as defaults."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=CHARGER_NAME,
        data=CONFIG_DATA,
        options={
            "grid": "sensor.grid_usage",
            "solar": "",
            "voltage": "",
            "shaper": "",
            "invert_grid": True,
        },
        version=2,
    )
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "init"

    # Submit with updated values
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={
            "grid": "sensor.grid_usage",
            "solar": "sensor.solar_production",
            "voltage": "",
            "shaper": "",
            "invert_grid": True,
        },
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"]["solar"] == "sensor.solar_production"


async def test_options_flow_all_empty_entities(hass, test_charger, mock_ws_start):
    """Test options flow allows empty strings for all sensor entities."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=CHARGER_NAME,
        data=CONFIG_DATA,
        options={
            "grid": "sensor.grid_usage",
            "solar": "sensor.solar_production",
            "voltage": "sensor.grid_voltage",
            "shaper": "sensor.shaper_power",
            "invert_grid": True,
        },
        version=2,
    )
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "init"

    # Submit all as empty strings
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={
            "grid": "",
            "solar": "",
            "voltage": "",
            "shaper": "",
            "invert_grid": False,
        },
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"] == {
        "grid": "",
        "solar": "",
        "voltage": "",
        "shaper": "",
        "invert_grid": False,
    }


async def test_migrate_from_v1(hass, test_charger, mock_ws_start):
    """Test migration from config version 1 to version 2."""
    # Create a v1 entry with sensor fields in data
    v1_data = {
        "name": "openevse",
        "host": "openevse.test.tld",
        "username": "",
        "password": "",
        "grid": "sensor.grid_usage",
        "solar": "",
        "voltage": "sensor.grid_voltage",
        "invert_grid": False,
    }

    entry = MockConfigEntry(
        domain=DOMAIN,
        title=CHARGER_NAME,
        data=v1_data,
        version=1,
    )

    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    # Verify migration happened
    assert entry.version == 2

    # Verify sensor fields moved to options
    assert "grid" not in entry.data
    assert "solar" not in entry.data
    assert "voltage" not in entry.data
    assert "invert_grid" not in entry.data

    assert entry.options.get("grid") == "sensor.grid_usage"
    assert entry.options.get("voltage") == "sensor.grid_voltage"

    # Verify connection data is preserved
    assert entry.data.get("host") == "openevse.test.tld"
    assert entry.data.get("name") == "openevse"
