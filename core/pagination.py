from rest_framework.pagination import PageNumberPagination
from .responses import standard_response

class StandardPagination(PageNumberPagination):
    page_size = 20
    max_page_size = 100
    page_size_query_param = 'page_size'

    def get_paginated_response(self, data):
        return standard_response(
            success=True,
            data={
                'count': self.page.paginator.count,
                'next': self.get_next_link(),
                'previous': self.get_previous_link(),
                'results': data
            },
            message="OK"
        )
