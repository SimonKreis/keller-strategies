"""
The Canadian execution gap: how far each Canadian fund drifts from the US ETF it stands in for.

`common/ca_mapping.CA_MAPPING` maps every traded signal ticker to a Canadian-listed fund, and
its deviation register names the seven lines where the fund holds a different asset from the
one signalled. Naming is not measuring. This tool measures all twelve lines from the vendor:

    venv/Scripts/python.exe -m tools.ca_execution_gap
    venv/Scripts/python.exe -m tools.ca_execution_gap --no-save

WHAT IS COMPARED
----------------
Monthly total returns (Yahoo `Adj Close`) of the signal ETF against its Canadian image, IN USD.
A CAD unit class is converted with Yahoo's `CAD=X` on the fund's own trading days, so the
currency move -- which the backtest carries anyway, being in USD -- is taken out, and what
remains is the fund: its index, its MER, the 15% US withholding it cannot recover, its
tracking. The CAD class is measured wherever it exists, because it has the longer history;
the `.U` class is the same portfolio and the same MER, only quoted in another currency.

  corr    correlation of monthly returns over the common months
  TE      tracking error: standard deviation of the monthly return difference, annualised
  drift   annualised geometric return of the Canadian fund minus the US ETF's
  worst   the largest single-month difference, and when

THE YARDSTICK is the six like-for-like lines. Their drift is what the Canadian wrapper costs
on its own (MER, withholding, tracking). A deviation line is only worse than the wrapper by
the amount its drift and TE exceed theirs.

Their TE is also the noise floor, and it is not small: about 2-3% a year for funds holding
the same index. It is not the currency -- ZSP.U, quoted in USD, still tracks SPY at 1.5% --
but the month-end print of a thinly traded Canadian fund, which can be a stale last trade.
Measured 2026-10-04. So a TE is read against the yardstick, never against zero; the drift
is the robust figure.

What it does NOT measure: spreads and commissions (see `liquidity_flags`), conversion costs,
and the currency itself. A line with fewer than `MIN_MONTHS` common months -- ZCOM, launched
2025-10 -- is reported as too short, never as agreement.

Lives in `tools/`, not `tests/`, for the reason `tools/vendor_crosscheck.py` does: it opens
sockets, and `unittest discover` collects every `test_*.py`. The arithmetic is `measure_gap`,
a pure function the suite tests offline.
"""
import argparse
import contextlib
import datetime as _dt
import io
import json
import math
import os
import sys
import warnings

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common import ca_mapping as cam                          # noqa: E402

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#: Yahoo's USD/CAD: Canadian dollars per US dollar.
USDCAD_SYMBOL = 'CAD=X'

#: Below this many common months the answer is "too short to tell", never "agrees". The same
#: bar `tools/proxy_fidelity.measure` sets for a history donor.
MIN_MONTHS = 36

#: Yahoo's suffix per exchange, as `CANADIAN_EXCHANGES` spells them.
YAHOO_SUFFIX = {'TSX': '.TO', 'Cboe CA': '.NE'}


def measured_ticker(entry):
    """`(ticker, currency)` of the unit class this report measures for `entry`."""
    if entry.exec_ticker_cad:
        return entry.exec_ticker_cad, 'CAD'
    return entry.exec_ticker_usd, 'USD'


def yahoo_symbol(ticker, exchange):
    """`CGL.C` on the TSX is `CGL-C.TO` on Yahoo; `ZTL` on Cboe Canada is `ZTL.NE`."""
    return ticker.replace('.', '-') + YAHOO_SUFFIX[exchange]


def to_usd(cad_prices, usdcad):
    """A CAD price series in USD, at the rate of each of its own trading days (the last
    known rate when the FX series has no quote that day)."""
    fx = usdcad.reindex(usdcad.index.union(cad_prices.index)).ffill().reindex(cad_prices.index)
    return (cad_prices / fx).dropna()


def measure_gap(signal, executed, usdcad=None):
    """Gap of `executed` (a Canadian fund's daily prices) from `signal` (the US ETF's).

    `usdcad` is given when `executed` is quoted in CAD. Returns a dict, or None when fewer
    than `MIN_MONTHS` common months exist -- too short to say anything, and never to be read
    as agreement.
    """
    executed = executed.dropna()
    if usdcad is not None:
        executed = to_usd(executed, usdcad.dropna())
    s = signal.dropna().resample('ME').last()
    x = executed.resample('ME').last().iloc[1:]          # the fund's first month is partial
    idx = s.index.intersection(x.index)
    rs = s[idx].pct_change(fill_method=None)
    rx = x[idx].pct_change(fill_method=None)
    both = pd.DataFrame({'s': rs, 'x': rx}).dropna()
    if len(both) < MIN_MONTHS:
        return None
    years = len(both) / 12.0
    diff = both['x'] - both['s']
    worst = diff.abs().idxmax()
    return {'months': int(len(both)), 'from': str(both.index[0].date()),
            'corr': float(both['s'].corr(both['x'])),
            'te': float(diff.std() * math.sqrt(12)),
            'drift': float((1 + both['x']).prod() ** (1 / years)
                           - (1 + both['s']).prod() ** (1 / years)),
            'worst': float(diff[worst]), 'worst_month': '{:%Y-%m}'.format(worst)}


def _yahoo(symbols):
    import yfinance as yf
    with contextlib.redirect_stderr(io.StringIO()), warnings.catch_warnings():
        warnings.simplefilter('ignore')
        raw = yf.download(list(symbols), period='max', progress=False, auto_adjust=False,
                          group_by='column')
    adj = raw['Adj Close']
    return {s: adj[s].dropna() for s in symbols if s in adj.columns and adj[s].notna().any()}


def gap_report(data, mapping=None):
    """`{signal_ticker: row}` for every line of `mapping`. `data` maps Yahoo symbols to daily
    price series. A row carries the measurement, or the reason there is none."""
    mapping = cam.CA_MAPPING if mapping is None else mapping
    usdcad = data.get(USDCAD_SYMBOL)
    out = {}
    for key, entry in sorted(mapping.items()):
        ticker, currency = measured_ticker(entry)
        symbol = yahoo_symbol(ticker, entry.exchange)
        row = {'executed': ticker, 'symbol': symbol, 'currency': currency,
               'deviation': entry.deviation is not None, 'mer_pct': entry.mer_pct,
               'gap': None, 'status': None}
        if key not in data or symbol not in data or (currency == 'CAD' and usdcad is None):
            row['status'] = 'not_measured'
        else:
            row['gap'] = measure_gap(data[key], data[symbol],
                                     usdcad if currency == 'CAD' else None)
            row['status'] = 'measured' if row['gap'] else 'too_short'
        out[key] = row
    return out


def report_lines(rows):
    head = (f"{'signal':<7}{'executed':<10}{'from':>8}{'mo':>5}{'corr':>7}{'TE':>7}"
            f"{'drift':>8}{'MER':>7}   worst month")
    lines = []
    groups = (('LIKE-FOR-LIKE -- the yardstick: what the Canadian wrapper alone costs', False),
              ('DIFFERENT ASSET -- the deviation register', True))
    for title, deviation in groups:
        lines += ['', title, head, '-' * len(head)]
        for key, r in rows.items():
            if r['deviation'] != deviation:
                continue
            label = f"{key:<7}{r['executed']:<10}"
            g = r['gap']
            if r['status'] == 'not_measured':
                lines.append(label + 'NOT MEASURED: a vendor returned nothing')
            elif r['status'] == 'too_short':
                lines.append(label + f'fewer than {MIN_MONTHS} common months -- NOT agreement')
            else:
                mer = f"{r['mer_pct']:.2f}%" if r['mer_pct'] is not None else '-'
                lines.append(label + f"{g['from'][:7]:>8}{g['months']:>5}{g['corr']:>7.3f}"
                             f"{g['te']:>7.2%}{g['drift']:>+8.2%}{mer:>7}   "
                             f"{g['worst']:+.2%} {g['worst_month']}")
    lines += ['',
              '  In USD: currency taken out. Spreads, commissions and conversions are not in',
              '  these figures. Read a TE against the like-for-like lines, never against zero:',
              '  their TE is the noise of thin Canadian month-end prints.']
    return lines


def all_symbols(mapping=None):
    """Every Yahoo symbol the report needs: the signals, their images, and the FX rate."""
    mapping = cam.CA_MAPPING if mapping is None else mapping
    symbols = {USDCAD_SYMBOL}
    for key, entry in mapping.items():
        symbols |= {key, yahoo_symbol(measured_ticker(entry)[0], entry.exchange)}
    return sorted(symbols)


def main(argv=None, download=None):
    parser = argparse.ArgumentParser(description='Measure the Canadian execution gap.')
    parser.add_argument('--no-save', action='store_true')
    args = parser.parse_args(argv)
    download = download or _yahoo

    rows = gap_report(download(all_symbols()))

    print('CANADIAN EXECUTION GAP -- each Canadian fund against the US ETF it stands in for')
    print('\n'.join(report_lines(rows)))

    if not args.no_save:
        out_dir = os.path.join(ROOT_DIR, 'backtest_results')
        os.makedirs(out_dir, exist_ok=True)
        path = os.path.join(out_dir, 'ca_execution_gap_{}.json'.format(
            _dt.date.today().isoformat()))
        with open(path, 'w', encoding='utf-8') as fh:
            json.dump({'generated_at': _dt.datetime.now().isoformat(timespec='seconds'),
                       'min_months': MIN_MONTHS, 'rows': rows}, fh, indent=2, sort_keys=True)
        print(f'\nwritten: {path}')

    missing = [k for k, r in rows.items() if r['status'] == 'not_measured']
    if missing:
        print(f'\nNOT MEASURED: {", ".join(missing)}')
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
