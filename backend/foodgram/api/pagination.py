from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CommentPagination(PageNumberPagination):
    page_size = 4

    def get_paginated_response(self, data):
        return Response(
            {
                "count": len(data),
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "results": data,
            }
        )

class LimitPageNumberPagination(PageNumberPagination):
    page_size = 6
    page_size_query_param = 'limit'