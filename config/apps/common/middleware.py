class DummyMiddleware:
    """
    Dummy middleware that does nothing.
    It just passes request and response unchanged.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # request pass করে
        response = self.get_response(request)
        # response pass করে
        return response
