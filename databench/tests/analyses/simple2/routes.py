from tornado.web import RequestHandler


class PostHandler(RequestHandler):
    def post(self):
        self.write(self.get_argument('data', 'No data received'))


class GetHandler(RequestHandler):
    def get(self):
        self.write('done')


ROUTES = [
    ('post', PostHandler, {}),
    ('get', GetHandler, {}),
]
