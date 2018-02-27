# About

This code provides an example of how to export Guidebook metrics data into Marketo.

It takes metrics data from the [Guidebook Webhooks API](https://developer.guidebook.com/#webhooks) and imports it into Marketo via the [Marketo REST API](http://developers.marketo.com/rest-api/).


# Sample Usage

Before testing out the code.  Please `pip install -r requirements.txt` to get the package dependencies.  We highly recommend you do this in an [virtualenv](https://virtualenv.pypa.io/en/stable/).

Update `settings.py` with your Marketo API credentials and configuration information. Then the following command will perform the import with the demo data in `sample_event.json`.

`python execute_integration`

# Customizing this Integration

This code is provided to Guidebook clients to customize for their own integrations.  Clients are welcome to take this integration code as a starting point and adapt it to their own needs.  Note that this implementation is very rudimentary and serves to illustrate how to translate one metrics event to a corresponding Activity in Marketo.  For a robust production implementation, we recommend queueing up events and performing bulk creations via Marketo API.