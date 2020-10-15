class TemplateGen:
    properties = { }

    def register(self, name, value):
        self.properties[name] = value

    def deregister_all(self):
        self.properties = { }

    def generate(self, template):
        for key in self.properties:
            template = template.replace("__{0}__".format(key), "{0}".format(self.codeify(self.properties[key])))

        return template

    def codeify(self, value):
        val_type = type(value)

        if val_type is list:
            val_type = type(value[0])

            if val_type is int:
                return ', '.join(map(str, value))

            if val_type is str:
                return '"{0}"'.format('", "'.join(value))

        if val_type is str:
            return '"{0}"'.format(value)

        return '{0}'.format(value)
    
