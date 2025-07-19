#!/usr/bin/env python3
import unittest
from utils import access_nested_map
from parameterized import parameterized

class TestAccessNestedMap(unittest.TestCase):
    @parameterized.expand([
        ({"a": 1}, ("a",), 1),
        ({"a": {"b": 2}}, ("a", "b"), 2),
        ({"a": {"b": {"c": 3}}}, ("a", "b", "c"), 3),
    ])
    def test_access_nested_map(self, nested_map, path, expected):
        result = access_nested_map(nested_map, path)
        self.assertEqual(result, expected)
    
    @parameterized.expand([
        ({},("a",)),
        ({"a": 1},("a", "b")),
    ])
    def test_access_nested_map_exception(self, nested_map, path):
        with self.assertRaises(KeyError) as x:
            access_nested_map(nested_map, path)

