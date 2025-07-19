#!/usr/bin/env python3
import unittest
import requests
from unittest.mock import patch,Mock
from utils import access_nested_map,get_json
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

class TestGetJson(unittest.TestCase):
    @patch(requests.get)
    def test_get_json(self,mock_get):
        mock_res = Mock()
        res_dict = {"payload": True}
        mock_res.json.return_value = res_dict

        mock_get.return_value = mock_res

        mock_get.assert_called_with("http://example.com")

        self.assertEqual(get_json("http://example.com"),res_dict)

