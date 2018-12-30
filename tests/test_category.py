import unittest

from category import Category


class ScriptTestCase(unittest.TestCase):
    def test_find_node(self):
        category = Category('data/category.yaml')
        self.assertIsNone(category.find_node('no'))
        self.assertEqual({'name': '캐릭터'}, category.find_node('캐릭터'))

    def test_all_children(self):
        category = Category('data/category.yaml')
        node = category.find_node('문장')

        self.assertEqual(['문장', '명언'], category.all_children(node))
