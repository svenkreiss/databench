from tornado.web import RequestHandler


class PostHandler(RequestHandler):
    def post(self):
        print(self.get_argument('data', 'No data received'))
        self.write('done')


class GetHandler(RequestHandler):
    def get(self):
        self.write('done')


ROUTES = [
    ('post', PostHandler, {}),
    ('get', GetHandler, {}),
]
