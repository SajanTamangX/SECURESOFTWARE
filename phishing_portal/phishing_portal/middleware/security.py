from django.http import HttpResponseForbidden


class BlockCommonAttacksMiddleware:
    """
    Basic middleware to block obvious XSS attempts in query strings.
    Not comprehensive but catches the obvious stuff.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # List of suspicious patterns - could expand this later
        suspicious = ["<script", "javascript:", "onerror", "onload"]
        query = request.GET.urlencode().lower()
        if any(x in query for x in suspicious):
            return HttpResponseForbidden("Potential XSS detected")
        return self.get_response(request)

