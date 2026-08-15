# Miracle Birds HubSpot App

This HubSpot Developer Platform project is linked to the authenticated HubSpot
account through the HubSpot CLI. The app uses OAuth and requests the same CRM
contact, company, and deal scopes used by the CRM integration service.

## Local commands

```bash
/home/aarush/.npm-global/bin/hs project validate
/home/aarush/.npm-global/bin/hs project upload --account miraclebirds
```

The production OAuth callback is:

```text
https://mb-backend-rnhn.onrender.com/api/v1/integrations/hubspot/callback
```

Local development can use a separate localhost callback in a local HubSpot app
profile. The deployed project must keep the public HTTPS callback above.

The webhook target must also be replaced with the deployed HTTPS URL before
activating HubSpot webhook subscriptions.
