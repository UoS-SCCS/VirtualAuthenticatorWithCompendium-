# Compendium Setup
Compendium is still in development and as such is not released on any standard Python repository. The wheel and requirements are included in the repository. To install do the following:

```pip install -r compendium_requirements.txt```

followed by

```pip install Compendium-0.1-py2.py3-none-any.whl```

## Current Status
Usage of Compendium is still in development, this is currently just a proof of concept. Currently the enrolment is limited to a single device and there is no current UI for removing/resetting.

### Manual Reset
Delete the following keys form prefs.json
* device_id
* encrypted_key
* verification_key

Delete authenticator encrypted store: auth_store.enc

Delete Public Key file of compendium ```~/.compendium/data/PROFILE/public_ids.json```

The public_ids.json is shared by all users of Compendium on a machine who aren't providing their own key store, so that will reset them as well. Device keys are stored in the system key ring under Compendium, although they don't need resetting.