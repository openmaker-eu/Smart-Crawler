import tornado.web
import tornado
from jinja2 import Environment, FileSystemLoader, TemplateNotFound

from settings import app_settings


class BaseHandler(tornado.web.RequestHandler):
    def data_received(self, chunk):
        pass


class JinjaCustomFilter:
    @classmethod
    def debug(cls, text):
        print(str(text))
        return

    @classmethod
    def repr(cls, text):
        return repr(text)


class TemplateRendering:
    @classmethod
    def render_template(cls, template_name, variables=None):
        if variables is None:
            variables = {}
        env = Environment(loader=FileSystemLoader(app_settings['template_path']))
        jcf = JinjaCustomFilter()
        env.filters['debug'] = jcf.debug
        env.filters['repr'] = jcf.repr
        try:
            template = env.get_template(template_name)
        except TemplateNotFound:
            raise TemplateNotFound(template_name)

        content = template.render(variables)
        return content


class StaticHandler(tornado.web.StaticFileHandler):
    def data_received(self, chunk):
        pass

    def set_default_headers(self):
        self.set_header('Access-Control-Allow-Origin', '*')
