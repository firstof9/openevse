"""Test config flow."""

from tests.const import CONFIG_DATA
from unittest.mock import patch
import pytest

from custom_components.openevse.const import DOMAIN

from homeassistant import config_entries, data_entry_flow, setup
from homeassistant.const import CONF_NAME
from pytest_homeassistant_custom_component.common import MockConfigEntry
from homeassistant.data_entry_flow import FlowResult, FlowResultType

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
                "invert": False,
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
                "invert": False,                
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
    ) as mock_setup_entry:
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], input
        )

        assert result["type"] == FlowResultType.CREATE_ENTRY
        assert result["title"] == title
        assert result["data"] == data

        await hass.async_block_till_done()
        assert len(mock_setup_entry.mock_calls) == 1


# @pytest.mark.parametrize(
#     "input,step_id,title,data",
#     [
#         (
#             {
#                 "name": "openevse_test",
#                 "host": "openevse.test.tld",
#                 "username": "",
#                 "password": "",
#             },
#             "init",
#             "openevse_test",
#             {
#                 "name": "openevse_test",
#                 "host": "openevse.test.tld",
#                 "username": "",
#                 "password": "",
#             },
#         ),
#     ],
# )
# async def test_options(
#     input,
#     step_id,
#     title,
#     data,
#     hass,
#     test_charger,
#     mock_ws_start,
# ):
#     """Test options flow."""
#     entry = MockConfigEntry(
#         domain=DOMAIN,
#         title=CHARGER_NAME,
#         data=CONFIG_DATA,
#     )

#     entry.add_to_hass(hass)
#     assert await hass.config_entries.async_setup(entry.entry_id)
#     await hass.async_block_till_done()

#     await setup.async_setup_component(hass, "persistent_notification", {})
#     result = await hass.config_entries.options.async_init(entry.entry_id)

#     assert result["type"] == FlowResultType.FORM
#     assert result["step_id"] == step_id

#     with patch(
#         "custom_components.openevse.async_setup_entry",
#         return_value=True,
#     ) as mock_setup_entry:
#         result = await hass.config_entries.options.async_configure(
#             result["flow_id"], input
#         )

#         assert result["type"] == FlowResultType.CREATE_ENTRY
#         assert result["title"] == ""
#         assert result["data"] == data

#         await hass.async_block_till_done()

#         assert data == entry.options.copy()
