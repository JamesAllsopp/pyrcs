"""Test the module :py:mod:`pyrcs.other_assets.sig_box`."""

import collections

import pandas as pd
import pytest

from pyrcs.other_assets import SignalBoxes

sb = SignalBoxes()


# def test_collect_prefix_codes():
#     sb_a_codes = sb.collect_prefix_codes(initial='a', update=True, verbose=True)
#
#     assert isinstance(sb_a_codes, dict)
#     assert list(sb_a_codes.keys()) == ['A', 'Last updated date']
#
#     sb_a_codes_dat = sb_a_codes['A']
#     assert isinstance(sb_a_codes_dat, pd.DataFrame)


def test_collect_prefix_codes():
    sb_a_codes = sb.collect_prefix_codes(initial='a', update=True, verbose=True)

    assert isinstance(sb_a_codes, dict)
    assert list(sb_a_codes.keys()) == ['A', 'Last updated date']

    sb_a_codes_dat = sb_a_codes['A']
    assert isinstance(sb_a_codes_dat, pd.DataFrame)


def test_fetch_prefix_codes():
    sb_prefix_codes = sb.fetch_prefix_codes()

    assert isinstance(sb_prefix_codes, dict)
    assert list(sb_prefix_codes.keys()) == ['Signal boxes', 'Last updated date']

    sb_prefix_codes_dat = sb_prefix_codes[sb.KEY]
    assert isinstance(sb_prefix_codes_dat, pd.DataFrame)


def test_fetch_non_national_rail_codes():
    nnr_codes = sb.fetch_non_national_rail_codes(update=True, verbose=True)

    assert isinstance(nnr_codes, dict)
    assert list(nnr_codes.keys()) == ['Non-National Rail', 'Last updated date']

    nnr_codes_dat = nnr_codes[sb.KEY_TO_NON_NATIONAL_RAIL]
    assert isinstance(nnr_codes_dat, dict)

    sb_prefix_codes = sb.fetch_prefix_codes()
    assert isinstance(sb_prefix_codes, dict)

    lu_signals_codes = nnr_codes_dat['London Underground signals']
    assert isinstance(lu_signals_codes, dict)

    nnr_codes = sb.fetch_non_national_rail_codes()

    assert isinstance(nnr_codes, dict)
    assert list(nnr_codes.keys()) == ['Non-National Rail', 'Last updated date']

    nnr_codes_dat = nnr_codes[sb.KEY_TO_NON_NATIONAL_RAIL]
    assert isinstance(nnr_codes_dat, dict)

    sb_prefix_codes = sb.fetch_prefix_codes()
    assert isinstance(sb_prefix_codes, dict)

    lu_signals_codes = nnr_codes_dat['London Underground signals']
    assert isinstance(lu_signals_codes, dict)


def test_fetch_ireland_codes():
    ireland_sb_codes = sb.fetch_ireland_codes(update=True, verbose=True)

    assert isinstance(ireland_sb_codes, dict)
    assert list(ireland_sb_codes.keys()) == ['Ireland', 'Notes', 'Last updated date']
    ireland_sb_codes_dat = ireland_sb_codes[sb.KEY_TO_IRELAND]
    assert isinstance(ireland_sb_codes_dat, pd.DataFrame)

    ireland_sb_codes = sb.fetch_ireland_codes()

    assert isinstance(ireland_sb_codes, dict)
    assert list(ireland_sb_codes.keys()) == ['Ireland', 'Notes', 'Last updated date']
    ireland_sb_codes_dat = ireland_sb_codes[sb.KEY_TO_IRELAND]
    assert isinstance(ireland_sb_codes_dat, pd.DataFrame)


def test_fetch_wr_mas_dates():
    sb_wr_mas_dates = sb.fetch_wr_mas_dates(update=True, verbose=True)

    assert isinstance(sb_wr_mas_dates, dict)
    assert list(sb_wr_mas_dates.keys()) == ['WR MAS dates', 'Last updated date']
    sb_wr_mas_dates_dat = sb_wr_mas_dates[sb.KEY_TO_WRMASD]
    assert isinstance(sb_wr_mas_dates_dat, collections.defaultdict)

    sb_wr_mas_dates = sb.fetch_wr_mas_dates()

    assert isinstance(sb_wr_mas_dates, dict)
    assert list(sb_wr_mas_dates.keys()) == ['WR MAS dates', 'Last updated date']
    sb_wr_mas_dates_dat = sb_wr_mas_dates[sb.KEY_TO_WRMASD]
    assert isinstance(sb_wr_mas_dates_dat, collections.defaultdict)


def test_fetch_bell_codes():
    sb_bell_codes = sb.fetch_bell_codes(update=True, verbose=True)

    assert isinstance(sb_bell_codes, dict)
    assert list(sb_bell_codes.keys()) == ['Bell codes', 'Last updated date']
    sb_bell_codes_dat = sb_bell_codes[sb.KEY_TO_BELL_CODES]
    assert isinstance(sb_bell_codes_dat, collections.OrderedDict)
    sb_nr_bell_codes = sb_bell_codes_dat['Network Rail codes']
    assert isinstance(sb_nr_bell_codes, dict)

    sb_bell_codes = sb.fetch_bell_codes()

    assert isinstance(sb_bell_codes, dict)
    assert list(sb_bell_codes.keys()) == ['Bell codes', 'Last updated date']
    sb_bell_codes_dat = sb_bell_codes[sb.KEY_TO_BELL_CODES]
    assert isinstance(sb_bell_codes_dat, collections.OrderedDict)
    sb_nr_bell_codes = sb_bell_codes_dat['Network Rail codes']
    assert isinstance(sb_nr_bell_codes, dict)


if __name__ == '__main__':
    pytest.main()
