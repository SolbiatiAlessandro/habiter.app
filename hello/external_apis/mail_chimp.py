import mailchimp3 
#{'lists': [{'id': '241345e94e', 'name': 'Habiter'}], 'total_items': 1}
#abbaee722c984352444f300463c523bc-us19
HABITER = '241345e94e'
API_KEY='abbaee722c984352444f300463c523bc-us19'
#Alessandro Solbiati
from enum import Enum
from django.http import HttpResponse, JsonResponse
from typing_extensions import TypedDict
import logging
logger = logging.getLogger(__name__)

class MailChimpsValues(Enum):
    SUCCESS ='Great! We just sent you an email with some questions.'
    NO_EMAIL = 'Looks like you did not input an email'
    INVALID_EMAIL = 'Looks like that email is invalid'
    UNKNOWN_FAILURE = 'Oopss.. something wrong with that email'
    ALREADY_SUBSCRIBED = 'Looks like you already subscribed with that email'

class MailChimpsResponse(TypedDict):
    result: str

def mailchimp_subscribe(request) -> MailChimpsResponse:
    """
    API endpoint:

    'result': MailChimpsValues
    """
    email: str = request.GET.get('email', None)
    if not email:
        return JsonResponse({'result':MailChimpsValues.NO_EMAIL.value})
    result: MailChimpsValues = add_new_email(email)
    # next line TypedDict not supported by linter
    response: MailChimpsResponse = {'result': result.value}
    return JsonResponse(response)

def add_new_email(email: str) -> MailChimpsValues:
    """
    """
    try:
        client = mailchimp3.MailChimp(mc_api=API_KEY)
        client.lists.members.create(HABITER, {
            'email_address': email,
            'status': 'subscribed',
        })
        return MailChimpsValues.SUCCESS
    except mailchimp3.mailchimpclient.MailChimpError as error:
        logger.error("!!!!!SUBSCRIBE ERROR!!!!!")
        logger.error(error)
        if error.args[0]['title'] == MailChimpsValues.INVALID_EMAIL.value:
            return MailChimpsValues.INVALID_EMAIL
        elif error.args[0]['title'] == MailChimpsValues.ALREADY_SUBSCRIBED.value:
            return MailChimpsValues.ALREADY_SUBSCRIBED
        return MailChimpsValues.UNKNOWN_FAILURE


def example():
    client = mailchimp3.MailChimp(mc_api=API_KEY)
    # returns all the lists (only name and id)
    all_lists = client.lists.all(get_all=True, fields="lists.name,lists.id")
    print(all_lists)

    # returns all members inside list HABITER
    print(client.lists.members.all(HABITER, get_all=True))

    # return the first 100 member's email addresses for the list with id 123456
    print(client.lists.members.all(HABITER, count=100, offset=0, fields="members.email_address"))

    # returns the list matching id HABITER
    print(client.lists.get(HABITER))

    # add John Doe with email john.doe@example.com to list matching id HABITER
    client.lists.members.create(HABITER, {
        'email_address': 'john.doe@example.com',
        'status': 'subscribed',
        'merge_fields': {
            'FNAME': 'John',
            'LNAME': 'Doe',
        },
    })

if __name__ == "__main__":
    print(add_new_email('john.doe@example.com'))
    print(add_new_email('alessandro.solbiati@gmail.com'))
