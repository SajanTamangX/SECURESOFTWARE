from django.http import HttpResponseForbidden


class BlockCommonAttacksMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        suspicious = ["<script", "javascript:", "onerror", "onload"]
        query = request.GET.urlencode().lower()
        if any(x in query for x in suspicious):
            return HttpResponseForbidden("Potential XSS detected")
        return self.get_response(request)

