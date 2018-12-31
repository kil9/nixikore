import unittest

from config import Session
from script import replace_literals, find_literals, compile_script


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

        self.assertEqual(script_in, script)

    def test_find_literals(self):
        script = '%{사람 %{사람} } %{랜덤} literals'
        literals = find_literals(script)
        self.assertEqual(literals, ['%{사람}', '%{랜덤}'])

        script = '%{1000-2030}'
        literals = find_literals(script)
        self.assertEqual(literals, ['%{1000-2030}'])

    def test_find_literals_matchall(self):
        script = '%{{사람}} literals'
        literals = find_literals(script)

        self.assertEqual(literals, ['%{{사람}}'])

    def test_particles(self):
        script = '%{{사람}}가 어쨌다고요'
        script = compile_script(script, self.session)
        print(script)
        self.assertFalse('(' in script)

        script = '서울 대표(%{1900-1901})'
        script = compile_script(script, self.session)
        self.assertEqual(script, '서울 대표(1900)')

        script = '서울 대표(%{1900-1901}-%{1949-1950})'
        script = compile_script(script, self.session)
        self.assertEqual(script, '서울 대표(1900-1949)')

        script = '서울 대표(%{장소})'
        script = compile_script(script, self.session)
        self.assertTrue(script.startswith('서울 대표('))
        self.assertTrue(script.endswith(')'))

    def test_numbered_literal(self):
        script = '%{사람}%{1}'
        script = compile_script(script, self.session)
        split = int(len(script)/2)
        self.assertEqual(script[:split], script[split:])

    def test_numbered_literal_particle(self):
        script = '%{{사람}} %{1}(이)라고'
        script = compile_script(script, self.session)
        self.assertFalse('(' in script)
