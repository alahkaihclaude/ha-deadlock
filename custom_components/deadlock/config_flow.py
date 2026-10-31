import voluptuous as vol

from homeassistant.config_entries import ConfigFlow

from . import DOMAIN
from .matches import to_account_id


class DeadlockConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            account_id = to_account_id(user_input["account_id"])
            if account_id is None:
                errors["account_id"] = "invalid_id"
            else:
                await self.async_set_unique_id(str(account_id))
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=user_input["name"], data={"account_id": account_id}
                )

        schema = vol.Schema({vol.Required("name"): str, vol.Required("account_id"): str})
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)
