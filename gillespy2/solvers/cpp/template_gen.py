class TemplateGen:
    properties = { }

    def register(self, name, value):
        self.properties[name] = value

    def deregister_all(self):
        self.properties = { }

    def generate(self, template):
        template = self.expand_vals(template)
        template = self.expand_iter(template)

        return template

    def expand_vals(self, template):
        for key in self.properties:
            template = template.replace("__{0}__".format(key), "{0}".format(self.codeify(self.properties[key])))

        return template


    def expand_iter(self, template):
        # Parse the iteration header.
        header = template[:template.index(':')]
        collection = header[2:header.index('-')]
        iterator = header[header.index('-') + 2:-1]

        for x in self.properties[collection]:
            template


    def expand_exec(self):

    def codeify(self, value):
        val_type = type(value)

        if val_type is list:
            val_type = type(value[0])

            if val_type is str:
                return '"{0}"'.format('", "'.join(value))

            if val_type is int or float:
                return ', '.join(map(str, value))

        if val_type is str:
            return '"{0}"'.format(value)

        return '{0}'.format(value)
    
