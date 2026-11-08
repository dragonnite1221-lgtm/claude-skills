"""Unissued option pools must not retain part of exit proceeds."""
import importlib.util
import sys
import unittest
from dataclasses import asdict
from pathlib import Path

PATH = Path(__file__).resolve().parents[1] / 'c-level-advisor/cfo-advisor/scripts/fundraising_model.py'
SPEC = importlib.util.spec_from_file_location('exit_proceeds_allocation', PATH)
fund = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = fund
SPEC.loader.exec_module(fund)


def cap_table(pool=25):
    cap = fund.CapTable()
    cap.add_shareholder(fund.Shareholder('Founder', 'common', 80))
    cap.add_shareholder(fund.Shareholder('Investor', 'preferred', 20, invested=100))
    if pool:
        cap.add_shareholder(fund.Shareholder('Pool', 'option', pool, is_option_pool=True))
    return cap


class ExitAllocationTests(unittest.TestCase):
    def test_all_exit_value_reaches_participating_holders(self):
        rows = cap_table().analyze_exit(1000)
        self.assertEqual(sum(r.proceeds_common for r in rows), 1000)
        self.assertEqual(sum(r.ownership_pct for r in rows), 1)
        self.assertEqual([(r.shareholder, r.proceeds_common, r.moic) for r in rows],
                         [('Founder', 800, 0), ('Investor', 200, 2)])

    def test_pool_size_does_not_change_exit_allocations(self):
        expected = [asdict(r) for r in cap_table(0).analyze_exit(1000)]
        for shares in (0.01, 1, 25, 100, 1_000_000):
            with self.subTest(pool=shares):
                self.assertEqual([asdict(r) for r in cap_table(shares).analyze_exit(1000)], expected)

    def test_pool_flag_not_share_class_controls_participation(self):
        cap = cap_table()
        cap.add_shareholder(fund.Shareholder('Second pool', 'common', 500, is_option_pool=True))
        cap.add_shareholder(fund.Shareholder('Employee', 'option', 25))
        rows = cap.analyze_exit(1250)
        self.assertEqual({r.shareholder for r in rows}, {'Founder', 'Investor', 'Employee'})
        self.assertEqual(sum(r.proceeds_common for r in rows), 1250)
        self.assertEqual(next(r.proceeds_common for r in rows if r.shareholder == 'Employee'), 250)

    def test_no_pool_proportions_are_unchanged(self):
        rows = cap_table(0).analyze_exit(5000)
        self.assertEqual([r.proceeds_common for r in rows], [4000, 1000])
        self.assertEqual([r.ownership_pct for r in rows], [0.8, 0.2])

    def test_no_participating_shares_is_safe(self):
        empty = fund.CapTable()
        self.assertEqual(empty.analyze_exit(1000), [])
        empty.add_shareholder(fund.Shareholder('Pool', 'option', 100, is_option_pool=True))
        self.assertEqual(empty.analyze_exit(1000), [])
        empty.add_shareholder(fund.Shareholder('Zero', 'common', 0))
        row = empty.analyze_exit(1000)[0]
        self.assertEqual((row.proceeds_common, row.ownership_pct, row.moic), (0, 0, 0))

    def test_zero_exit_keeps_ownership_but_has_no_proceeds(self):
        rows = cap_table().analyze_exit(0)
        self.assertEqual([r.proceeds_common for r in rows], [0, 0])
        self.assertEqual(sum(r.ownership_pct for r in rows), 1)

    def test_exit_analysis_preserves_cap_table(self):
        cap = cap_table()
        before = [asdict(s) for s in cap.shareholders]
        snapshot = [asdict(s) for s in cap.snapshot()]
        cap.analyze_exit(1000)
        self.assertEqual([asdict(s) for s in cap.shareholders], before)
        self.assertEqual([asdict(s) for s in cap.snapshot()], snapshot)
        self.assertEqual(cap.total_shares(), 125)

    def test_sample_model_conserves_exit_proceeds(self):
        cap, rounds = fund.build_sample_model()
        for valuation in (0, 1_000_000, 250_000_000):
            with self.subTest(valuation=valuation):
                rows = cap.analyze_exit(valuation)
                self.assertAlmostEqual(sum(r.proceeds_common for r in rows), valuation)
                self.assertAlmostEqual(sum(r.ownership_pct for r in rows), 1)
        self.assertEqual(len(rounds), 5)


if __name__ == '__main__':
    unittest.main()
