#!/usr/bin/env python3
import unittest
import requests
from unittest.mock import patch,Mock
from utils import access_nested_map,get_json,memoize
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

class TestMemoize(unittest.TestCase):
    """ test class to tes utils.memoize"""

    def test_memoize(self):
        """ Tests the function when calling a_property twice,
        the correct result is returned but a_method is only
        called once using assert_called_once
        """

        class TestClass:
            """ Test Class for wrapping with memoize """

            def a_method(self):
                return 42

            @memoize
            def a_property(self):
                return self.a_method()

        with patch.object(TestClass, 'a_method') as mock:
            test_class = TestClass()
            test_class.a_property()
            test_class.a_property()
            mock.assert_called_once()

