import unittest
from unittest.case import expectedFailure
from gillespy2.solvers.cpp.template_gen import TemplateGen

class TestTemplateGen(unittest.TestCase):
    def test_int_format(self):
        gen = TemplateGen()
        gen.register_all(('varName', 'this_is_a_long_variable_name'), ('varValue', 2))

        template = 'const uint &varName& = _varValue_;'
        expected = 'const uint this_is_a_long_variable_name = 2;\n'

        self.assertEqual(gen.generate(template), expected)

    def test_str_format(self):
        gen = TemplateGen()
        gen.register_all(('varName', 'this_is_a_str_var'), ('varValue', 'Hello world!'))

        template = 'std::str &varName& = _varValue_;'
        expected = 'std::str this_is_a_str_var = "Hello world!";\n'

        self.assertEqual(gen.generate(template), expected)

    def test_int_array_format(self):
        gen = TemplateGen()
        gen.register_all(('varName', 'short_var_name'), ('varValue', [1, 2, 3, 4, 5, 6]))

        template = 'int &varName&[] = { _varValue_ };'
        expected = 'int short_var_name[] = { 1, 2, 3, 4, 5, 6 };\n'

        self.assertEqual(gen.generate(template), expected)

    def test_str_array_format(self):
        gen = TemplateGen()
        gen.register_all(('varName', 'some_str_array_var'), ('strArray', ['A', 'B', 'C', 'D']))

        template = 'std::str &varName&[] = { _strArray_ };'
        expected = 'std::str some_str_array_var[] = { "A", "B", "C", "D" };\n' 

        self.assertEqual(gen.generate(template), expected)

if __name__ == "__main__":
    unittest.main()
