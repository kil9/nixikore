import unittest

from config import Session
from script import replace_literals, find_literals


class ScriptTestCase(unittest.TestCase):
    def setUp(self):
        self.session = Session()

    def tearDown(self):
        self.session.close()


    def test_replace_literals(self):
        script_in = '%{사람}'
        script = replace_literals(script_in, self.session)

        self.assertNotEqual(script, script_in)

    def test_replace_literals_unknown(self):
        script_in = '%{XXXX}'
        script = replace_literals(script_in, self.session)

        self.assertNotEqual('', script_in)

    def test_find_literals(self):
        script = '%{사람 %{사람} } %{랜덤} literals'
        literals = find_literals(script)

        self.assertEqual(literals, ['%{사람}', '%{랜덤}'])

    def test_find_literals_matchall(self):
        script = '%{{사람}} literals'
        literals = find_literals(script)

        self.assertEqual(literals, ['%{{사람}}'])
