import json
import requests
import settings


def import_guidebook_metrics_into_marketo(gb_metrics_event):
    # These are the fields we care about in Marketo
    FIELDS = ['id',
              'email',
              'updatedAt',
              'createdAt',
              'firstName',
              'lastName',
              ]

    marketo_rest_api_endpoint = settings.MARKETO_API_ENDPOINT
    marketo_client_id = settings.MARKETO_CLIENT_ID
    marketo_client_secret = settings.MARKETO_CLIENT_SECRET

    # Start with getting an access token
    auth_endpoint = "{}/identity/oauth/token?grant_type=client_credentials&client_id={}&client_secret={}".format(marketo_rest_api_endpoint, marketo_client_id, marketo_client_secret)
    response = requests.get(auth_endpoint)
    if response.status_code == 200:
        marketo_access_token = json.loads(response.text).get('access_token')
    else:
        raise Exception('Invalid Marketo Credentials')

    user_email = gb_metrics_event['properties']['email']
    guide_name = gb_metrics_event['properties']['guide_name']

    if user_email is None:
        # user_email is required.
        print u'Missing email for Account: {} - skipping...'.format(gb_metrics_event['properties']['user_id'])
        return

    # attempt to get Lead via email
    fields = ','.join(FIELDS)
    lead_endpoint = "{}/rest/v1/leads.json?access_token={}&filterType=email&filterValues={}&fields={}".format(marketo_rest_api_endpoint, marketo_access_token, user_email, fields)
    response = requests.get(lead_endpoint)
    marketo_lead_id = None
    if response.status_code == 200:
        try:
            marketo_lead_id = json.loads(response.text).get('result')[0]['id']
        except Exception:
            marketo_lead_id = None
    else:
        print u'Marketo GET Lead API failed'
        return

    # not found - create a Lead w/ that email
    if marketo_lead_id is None:
        # grab lead properties from event.  Be careful with null values
        lead_first_name = 'Unknown' if gb_metrics_event['properties']['first_name'] is None else gb_metrics_event['properties']['first_name']
        lead_last_name = 'Unknown' if gb_metrics_event['properties']['last_name'] is None else gb_metrics_event['properties']['last_name']
        company_name = guide_name if gb_metrics_event['properties']['company'] is None else gb_metrics_event['properties']['company']
        company_position = '' if gb_metrics_event['properties']['position'] is None else gb_metrics_event['properties']['position']

        lead_endpoint = "{}/rest/v1/leads.json?access_token={}".format(marketo_rest_api_endpoint, marketo_access_token)
        data = {
            "action": "createOnly",
            "lookupField": "email",
            "input": [{"email": user_email,
                       "firstName": lead_first_name,
                       "lastName": lead_last_name,
                       "company": company_name,
                       "title": company_position,
                       }]
        }
        try:
            response = requests.post(lead_endpoint, json=data)
        except Exception:
            print 'Marketo Create Lead API failed'
            return

        # refetch lead
        lead_endpoint = "{}/rest/v1/leads.json?access_token={}&filterType=email&filterValues={}&fields={}".format(marketo_rest_api_endpoint, marketo_access_token, user_email, fields)
        response = requests.get(lead_endpoint)
        marketo_lead_id = None
        try:
            marketo_lead_id = json.loads(response.text).get('result')[0]['id']
        except Exception:
            print 'Marketo GET Lead API failed'
            return
        print u'Created new Marketo Lead: {}'.format(user_email)

    activity_endpoint = "{}/rest/v1/activities/external.json?access_token={}".format(marketo_rest_api_endpoint, marketo_access_token)
    activity_id = settings.MARKETO_CUSTOM_ACTIVITY_ID
    attribute_value = u'{}: {}'.format(gb_metrics_event['properties'].get('guide_name'), gb_metrics_event['event'])
    activity_date = gb_metrics_event['properties']['time'][:19]  # truncate to match marketos date format

    input_data = [{
        "activityDate": activity_date,
        "activityTypeId": activity_id,
        "leadId": marketo_lead_id,
        "attributes": [],
        "primaryAttributeValue": attribute_value,
    }]

    data = {"input": input_data}
    response = requests.post(activity_endpoint, json=data)

    print u'Result {}: {}'.format(response.status_code, response.content)
