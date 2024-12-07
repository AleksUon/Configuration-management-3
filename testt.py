import unittest
import tempfile
from io import StringIO
from main import *


class TestConfigLanguage(unittest.TestCase):
    def test_evaluate_expression(self):
        constants = {"x": 10, "y": 20, "z": 5}
        self.assertEqual(evaluate_expression("!(x + y)", constants), 30)
        self.assertEqual(evaluate_expression("!(max(x, y, z))", constants), 20)
        with self.assertRaises(ValueError):
            evaluate_expression("x + y", constants)
        self.assertEqual(evaluate_expression("!(x - z)", constants), 5)

    def test_format_value(self):
        constants = {"x": 10, "y": 20}
        self.assertEqual(format_value("!(x + y)", constants), "30")
        self.assertEqual(format_value(42, constants), 42)
        self.assertEqual(format_value("Hello", constants), '@"Hello"')
        self.assertEqual(format_value(["Hello", 42], constants), '@"Hello" 42')

    def test_format_dict(self):
        data = {"key": "!(x + y)", "nested": {"subkey": "!(x - z)"}}
        constants = {"x": 10, "y": 20, "z": 5}
        result = format_dict(data, constants)
        self.assertIn("key := 30;", result)
        self.assertIn("nested := begin", result)
        self.assertIn("subkey := 5;", result)

    def test_yaml_to_custom_format(self):
        yaml_content = """
        constants:
          x: 10
          y: 20
          z: 5
        project:
          name: "Имя проекта"
          value1: "!(x + y)"
          value2: "!(max(x, y, z))"
          debug_message: "!(print('print работает'))"
          nested:
            calculated_value: "!(x - z)"
        """
        constants = {"x": 10, "y": 20, "z": 5}
        result = yaml_to_custom_format(yaml_content, constants)
        expected_output = """begin
 project := begin
 name := @"Имя проекта";
 value1 := 30;
 value2 := 20;
 debug_message := None;
 nested := begin
 calculated_value := 5;
end;
end;
end"""
        self.assertEqual(result.strip(), expected_output.strip())


if __name__ == "__main__":
    unittest.main()