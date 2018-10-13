import os
import shutil

import settings
from handlers.base import BaseHandler, TemplateRendering


class ModulesHandler(BaseHandler, TemplateRendering):
    def get(self):
        modules = []
        for x in os.walk(settings.modules):
            _, modules, _ = x
            break
        modules = [{'name': module} for module in modules]
        variables = {
            'modules': modules,
            'title': "Modules",
            'type': "modules"
        }
        self.write(self.render_template("modules/index.html", variables))


class ModuleHandler(BaseHandler, TemplateRendering):
    def post(self):
        file_info = self.request.files['filearg'][0]
        file_name = file_info['filename']
        file_name = file_name.replace(' ', '_')

        file_name_without_extn = os.path.splitext(file_name)[0]
        extn = os.path.splitext(file_name)[1]

        if extn == '.zip':
            save_dir = os.path.join(settings.modules, file_name)
            fh = open(save_dir, 'wb')
            fh.write(file_info['body'])

            os.system('unzip -j ' + save_dir + ' -d ' + os.path.join(settings.modules, file_name_without_extn))

            if os.path.exists(save_dir):
                os.remove(save_dir)

        self.redirect('/modules')

    def delete(self, module_name=None):
        module = os.path.join(settings.modules, module_name)
        if os.path.exists(module):
            shutil.rmtree(module)
            response = {'response': True}
        else:
            response = {'response': False}
        self.write(response)
