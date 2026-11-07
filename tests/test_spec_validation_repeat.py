"""Repeated validation must not accumulate findings or mutate old results."""
import copy
import importlib.util
import os
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path(os.environ.get('SPEC_VALIDATOR_SOURCE', ROOT / 'engineering/spec-driven-workflow/scripts/spec_validator.py'))
spec = importlib.util.spec_from_file_location('spec_validator_repeat', SOURCE)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class RepeatValidationTests(unittest.TestCase):
    def test_repeated_result_matches_fresh_validator(self):
        content = '# Feature\n## Context\nReason\n## Functional Requirements\n- FR-1: system must work.\n'
        validator = module.SpecValidator(content, 'fixture.md')
        expected = module.SpecValidator(content, 'fixture.md').validate()
        for _ in range(4):
            self.assertEqual(validator.validate(), expected)

    def test_old_result_not_mutated_by_later_validation(self):
        validator = module.SpecValidator('# Feature\n## Context\nReason')
        first = validator.validate()
        snapshot = copy.deepcopy(first)
        second = validator.validate()
        self.assertEqual(first, snapshot)
        self.assertIsNot(first['findings'], second['findings'])
        self.assertIsNot(first['sections'], second['sections'])

    def test_caller_changes_to_prior_result_do_not_poison_next_run(self):
        content = '# Feature\n## Context\nReason'
        validator = module.SpecValidator(content)
        first = validator.validate()
        first['findings'].append({'severity': 'error', 'section': 'external', 'message': 'Injected'})
        first['sections']['external'] = {'score': 1000, 'max': 1000, 'present': True}
        self.assertEqual(validator.validate(), module.SpecValidator(content).validate())

    def test_prior_runs_do_not_suppress_placeholder_findings(self):
        content = '# Feature\n## Context\n[describe reason]\n'
        validator = module.SpecValidator(content)
        first = copy.deepcopy(validator.validate())
        for _ in range(3):
            result = validator.validate()
            self.assertEqual(result, first)
            self.assertEqual(sum(f['section'] == 'placeholders' for f in result['findings']), 1)


if __name__ == '__main__':
    unittest.main()
