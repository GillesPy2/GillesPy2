class TemplateGen:
    properties = { }

    def register(self, name, value):
        self.properties[name] = value

    def deregister_all(self):
        self.properties = { }

    def generate(self, template):
        for prop in self.properties:
            prop_val = self.properties[prop]

            template = template.replace('&{}&'.format(prop), self._format_prop(prop_val))
            template = template.replace('__{}__'.format(prop), self._format_val(prop_val))

        return template

    def _format_val(self, val):
        typeof = type(val)

        if typeof == list:
            return self._format_list(val)

        if typeof == str:
            return '"{}"'.format(val)

        return '{}'.format(val)


    def _format_prop(self, val):
        return str(val)

    def _format_list(self, val):
        if type(val[0]) != str:
            return '{}'.format(', '.join(map(str, val)))

        return '"{}"'.format('", "'.join(val))
