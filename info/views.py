import math

from django.http import HttpResponse
from django.template import Context, loader

from info.models import Brother, Officer
from info import utility

max_brothers_per_page = 24
standard_brothers_per_page = 9
brothers_per_row = 3
max_pages_listed_on_screen = 5
officers_per_row = 2
exec_board_members_per_row_on_about_page = 3


def index(request):
    t = loader.get_template('about.html')
    officer_list = Officer.objects.filter().order_by('ordering')
    c = Context({'officer_list': officer_list})
    return HttpResponse(t.render(c))


def officers(request):
    officers = Officer.objects.filter().order_by('ordering')
    officers_matrix = utility.convert_array_to_YxZ(officers, officers_per_row)
    c = Context({'officer_list_list': officers_matrix})
    t = loader.get_template('officers_list.html')
    return HttpResponse(t.render(c))

def actives(request):
    return general_listing(request, False, False, 'Active Members')

def pledges(request):
    return general_listing(request, False, True, 'Pledges')

def alumni(request):
    return general_listing(request, True, False, 'Alumni')

def general_listing(request, isAlumniFilter, isPledgeFilter, name):
    brothers_count = get_brother_count(request)
    page_number = get_page_number(request)
    brothers_range_min = (page_number - 1) * brothers_count
    brothers_range_max = (page_number) * brothers_count
    brothers = Brother.objects.filter(isAlumni=isAlumniFilter, isPledge=isPledgeFilter).order_by('lastName', 'firstName', 'middleName')
    number_of_brothers = len(brothers)
    total_pages = int(math.ceil(number_of_brothers / float(brothers_count)))
    brothers = brothers[brothers_range_min:brothers_range_max]
    brother_list_list = utility.convert_array_to_YxZ(brothers, brothers_per_row) if len(brothers) > 0 else None
    page_numbers_list = calculate_page_range(total_pages, page_number)
    next_page = page_number + 1 if number_of_brothers > brothers_range_max else 0
    prev_page = page_number - 1
    context_dict = {'brotherType': name, 'brother_list_list' : brother_list_list, 'page_number' : page_number, 'prev_page': prev_page, 'next_page' : next_page, 'page_numbers' : page_numbers_list}
    if brothers_count != standard_brothers_per_page:
        context_dict['brothers_count'] = brothers_count
    c = Context(context_dict)
    t = loader.get_template('brothers_list.html')
    return HttpResponse(t.render(c))

def get_brother_count(request):
    brothers_count = request.GET.get('count','9')
    try:
        brothers_count = int(brothers_count)
        if brothers_count > max_brothers_per_page:
            brothers_count = max_brothers_per_page
    except:
        brothers_count = standard_brothers_per_page
    return brothers_count

def get_page_number(request):
    page_number = request.GET.get('page','1')
    try:
        page_number = int(page_number)
        if page_number < 1:
            page_number = 1
    except:
        page_number = 1
    return page_number

def calculate_page_range(total_pages, page_number):
    if total_pages == 1: # If there is only the one page, there is no need to display page numbers
        return []
    elif total_pages <= max_pages_listed_on_screen: # In this case, just display all of the available pages
        min_page_number_displayed = 1
        max_page_number_displayed = total_pages + 1
    elif page_number - max_pages_listed_on_screen / 2 <= 1: # We are near the beginning. In this case, display from page 1 to max_pages_listed_on_screen
        min_page_number_displayed = 1
        max_page_number_displayed = min_page_number_displayed + max_pages_listed_on_screen
    elif page_number + max_pages_listed_on_screen / 2 >= total_pages: # We are near the end. In this case, display from (end - max_pages_listed_on_screen) to end
        max_page_number_displayed = total_pages + 1
        min_page_number_displayed = max_page_number_displayed - max_pages_listed_on_screen
    else: # We are somewhere in the middle. In this case, just display some pages on either side
        min_page_number_displayed = page_number - max_pages_listed_on_screen / 2
        max_page_number_displayed = min_page_number_displayed + max_pages_listed_on_screen
    
    page_numbers_list = range(min_page_number_displayed,max_page_number_displayed)    
    return page_numbers_list
