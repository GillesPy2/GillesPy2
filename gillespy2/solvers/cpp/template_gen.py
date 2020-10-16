class TemplateGen:
    """
    TemplateGen is a simple C++ code generator that allows for python variables to be embedded
    naturally within template strings.

    Formatting example: 'const int &myVar& = _someVal_; 
    - The value of 'myVal' will be written to &myVar& with _no_formatting.
    - The value of 'someVal' will be written to _someVal_ with formatting.
    """

    properties = {}

    def register(self, name, value):
        """
        This function will register a new property into the generator. 
        :param name: The name of the property as it appears in the code to be processed.
        :param value: The value of the property -- this value will replace any instances of its name.
        """

        self.properties[name] = value
    

    def register_all(self, *args):
        """
        This function will register _all_ properties passed into it.
        :param *args: One or more tuples in (name, value) pairs. 
        """

        for arg in args:
            if type(arg) != tuple:
                continue

            self.register(arg[0], arg[1])


    def deregister_all(self):
        """
        Deregisters all registered properties.
        """

        self.properties = {}


    def generate(self, template):
        """
        Parse and generate a valid C++ string of code from the template.
        :param template: A string who's format markers will be replaced with registered property values.
        """

        for prop in self.properties:
            prop_val = self.properties[prop]

            template = template.replace('&{}&'.format(prop), self.__format_prop(prop_val))
            template = template.replace('_{}_'.format(prop), self.__format_val(prop_val))

        if not template.endswith("\n"):
            template += "\n"

        return template


    def __format_val(self, val):
        """
        Format the argument as a _value_. Automatically expand arrays, quote strings, etc.
        :param val: The value to format.
        """

        typeof = type(val)

        if typeof == list:
            return self.__format_list(val)

        if typeof == str:
            return '"{}"'.format(val)

        return '{}'.format(val)


    def __format_prop(self, val):
        """
        Format the argument as a property. This will _not_ expand arrays, quote strings, or do any 
        extranous processing of any kind. 
        :param val: The value to format.
        """

        return str(val)


    def __format_list(self, val):
        """
        Expands and formats a list as per its type. A string array will be expanded with quotes around
        each value, numbers will not, etc.
        """

        if type(val[0]) != str:
            return '{}'.format(', '.join(map(str, val)))

        return '"{}"'.format('", "'.join(val))
