from smart_crawler.handlers.base import BaseHandler, TemplateRendering


class JobHandler(BaseHandler, TemplateRendering):
    def get(self):
        self.write(self.render_template("index.html"))
