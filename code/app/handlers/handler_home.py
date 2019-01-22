from handlers.base import BaseHandler, TemplateRendering


class HomeHandler(BaseHandler, TemplateRendering):
    def get(self):
        variables = {
            'title': "Smart Crawler",
        }
        self.write(self.render_template("home.html", variables))
