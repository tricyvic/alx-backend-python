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
    @parameterized.expand([
        ("http://example.com",({"payload": True})),
        ("http://holberton.io",({"payload": False}))
    ])
    @patch('requests.get')
    def test_get_json(self,test_url,test_payload,mock_get):
        mock_res = Mock()
        res_dict = test_payload
        mock_res.json.return_value = res_dict

        mock_get.return_value = mock_res

        called = get_json(test_url)
        mock_get.assert_called_with(test_url)

        self.assertEqual(called,res_dict)

