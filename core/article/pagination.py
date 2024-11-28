from rest_framework.pagination import PageNumberPagination

class CustomPagination(PageNumberPagination):
    page_size = 10  # Default number of articles per page
    page_size_query_param = 'page_size'  # Allows users to specify the page size via the query parameter, e.g.: ?page_size=20
    max_page_size = 50  # Limits the maximum number of articles per page to 50
