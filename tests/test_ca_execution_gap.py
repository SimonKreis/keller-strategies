"""
The Canadian execution-gap report, driven entirely offline.

`tools/ca_execution_gap.py` downloads from Yahoo, so it lives outside `tests/`. What can be
wrong without anybody noticing is the arithmetic and the scope, and both are pinned here
against series built by hand: a fund that IS its signal must show no gap, a known drag must
come back as that drag, a currency move must be taken out, and the report must cover every
line `common/ca_mapping.deviations()` names -- `TestTheDeviationRegisterIsComplete` says a
report that measures fewer lines is measuring the wrong thing.
"""
import os
import sys
import unittest
import unittest.mock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
import pandas as pd

from common import ca_mapping as cam
from tools import ca_execution_gap as gap


def _prices(n=1500, seed=3, start='2015-01-02'):
    idx = pd.bdate_range(start, periods=n)
    rng = np.random.default_rng(seed)
    return pd.Series(100 * np.cumprod(1 + rng.normal(0.0004, 0.01, n)), index=idx)


def _usdcad(index, seed=9):
    rng = np.random.default_rng(seed)
    return pd.Series(1.30 * np.cumprod(1 + rng.normal(0, 0.004, len(index))), index=index)


class TestTheArithmetic(unittest.TestCase):

    def test_a_fund_that_is_its_signal_shows_no_gap(self):
        s = _prices()
        g = gap.measure_gap(s, s * 0.2)                       # a different price level only
        self.assertAlmostEqual(g['drift'], 0.0, places=12)
        self.assertAlmostEqual(g['te'], 0.0, places=12)
        self.assertAlmostEqual(g['corr'], 1.0, places=12)

    def test_the_currency_is_taken_out(self):
        """A CAD class that is exactly the US fund times the exchange rate has no gap."""
        s = _prices()
        fx = _usdcad(s.index)
        g = gap.measure_gap(s, s * fx / 5, usdcad=fx)
        self.assertAlmostEqual(g['drift'], 0.0, places=10)
        self.assertAlmostEqual(g['te'], 0.0, places=10)

    def test_without_the_conversion_the_currency_would_be_read_as_a_gap(self):
        """The planted defect the previous test guards against."""
        s = _prices()
        fx = _usdcad(s.index)
        self.assertGreater(gap.measure_gap(s, s * fx)['te'], 0.01)

    def test_a_one_percent_annual_drag_comes_back_as_minus_one_percent(self):
        s = _prices()
        days = np.arange(len(s))
        drag = (1 - 0.01) ** (days / 252.0)
        g = gap.measure_gap(s, s * drag)
        # Geometric: the fund compounds at (1 + r)(1 - 1%), so its drift is -1% x (1 + r).
        years = g['months'] / 12.0
        monthly = s.resample('ME').last()
        window = monthly[monthly.index >= g['from']]
        r = (window.iloc[-1] / monthly[monthly.index < g['from']].iloc[-1]) ** (1 / years) - 1
        self.assertAlmostEqual(g['drift'], -0.01 * (1 + r), delta=0.0005)

    def test_the_funds_partial_first_month_is_not_compared(self):
        s = _prices()
        late = s[s.index >= '2016-03-15']
        g = gap.measure_gap(s, late)
        self.assertEqual(g['from'], '2016-05-31')        # April is the first whole return

    def test_too_short_is_none_never_agreement(self):
        s = _prices()
        recent = s[s.index >= s.index[-1] - pd.Timedelta(days=30 * (gap.MIN_MONTHS - 2))]
        self.assertIsNone(gap.measure_gap(s, recent))


class TestTheSymbols(unittest.TestCase):

    def test_yahoo_spells_unit_classes_with_a_dash(self):
        self.assertEqual(gap.yahoo_symbol('CGL.C', 'TSX'), 'CGL-C.TO')
        self.assertEqual(gap.yahoo_symbol('UBIL.U', 'TSX'), 'UBIL-U.TO')

    def test_cboe_canada_is_dot_ne(self):
        self.assertEqual(gap.yahoo_symbol('ZTL', 'Cboe CA'), 'ZTL.NE')

    def test_every_exchange_in_the_mapping_has_a_suffix(self):
        self.assertEqual(set(gap.YAHOO_SUFFIX), set(cam.CANADIAN_EXCHANGES))

    def test_the_cad_class_is_measured_where_it_exists(self):
        self.assertEqual(gap.measured_ticker(cam.CA_MAPPING['SPY']), ('ZSP', 'CAD'))
        self.assertEqual(gap.measured_ticker(cam.CA_MAPPING['BIL']), ('UBIL.U', 'USD'))


def _fake_download(symbols):
    """Every requested series, each Canadian fund being its signal plus currency."""
    base = _prices()
    fx = _usdcad(base.index)
    out = {gap.USDCAD_SYMBOL: fx}
    for key, entry in cam.CA_MAPPING.items():
        ticker, currency = gap.measured_ticker(entry)
        out[key] = base
        out[gap.yahoo_symbol(ticker, entry.exchange)] = base * fx if currency == 'CAD' else base
    return {s: out[s] for s in symbols if s in out}


class TestTheScope(unittest.TestCase):

    def test_every_line_of_the_mapping_is_reported(self):
        rows = gap.gap_report(_fake_download(gap.all_symbols()))
        self.assertEqual(sorted(rows), sorted(cam.CA_MAPPING))

    def test_every_deviation_is_measured(self):
        """The register in `ca_mapping` is the scope; this is the report covering it."""
        rows = gap.gap_report(_fake_download(gap.all_symbols()))
        for key in cam.deviations():
            self.assertTrue(rows[key]['deviation'], key)
            self.assertEqual(rows[key]['status'], 'measured', key)

    def test_a_missing_series_is_not_measured_and_exits_nonzero(self):
        def without_zsp(symbols):
            data = _fake_download(symbols)
            data.pop('ZSP.TO')
            return data

        with unittest.mock.patch('builtins.print') as printed:
            code = gap.main(['--no-save'], download=without_zsp)
        self.assertEqual(code, 1)
        text = '\n'.join(str(c.args[0]) for c in printed.call_args_list if c.args)
        self.assertIn('NOT MEASURED', text)

    def test_a_short_history_is_reported_as_not_agreement(self):
        data = _fake_download(gap.all_symbols())
        data['ZCOM.NE'] = data['ZCOM.NE'][-200:]
        rows = gap.gap_report(data)
        self.assertEqual(rows['DBC']['status'], 'too_short')
        text = '\n'.join(gap.report_lines(rows))
        self.assertIn('NOT agreement', text)

    def test_the_report_runs_offline_end_to_end(self):
        with unittest.mock.patch('builtins.print'):
            self.assertEqual(gap.main(['--no-save'], download=_fake_download), 0)


if __name__ == '__main__':
    unittest.main()
