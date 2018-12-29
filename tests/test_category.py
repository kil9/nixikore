import unittest

from category import Category


class ScriptTestCase(unittest.TestCase):
    def test_find_node(self):
        category = Category('data/category.yaml')
        self.assertEqual(None, category.find_node('no'))
        self.assertEqual({'name': '사람'}, category.find_node('사람'))

    def test_all_children(self):
        category = Category('data/category.yaml')
        node = category.find_node('동물')

        self.assertEqual(['동물', '사람', '펫'], category.all_children(node))
