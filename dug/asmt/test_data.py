import pandas as pd
from dateutil.relativedelta import relativedelta

from asmt import dtvp, dtvpa, mabc, time, spm


def test_dtvp_data():
    ra, rs, sp = dtvp.load()

    for i in ra.index.get_level_values(0).unique():
        raw = ra.loc[i]
        maxi = int(raw.index.max().left)
        for r in range(0, maxi + 2):
            for v in raw.loc[r]:
                assert not pd.isna(v)

    for i in rs.index.get_level_values(0).unique():
        for y in range(4, 13):
            for m in range(0, 12, 2):
                age = relativedelta(years=y, months=m)
                age_df = rs.loc[i].loc[time.delta_idx(age)]
                maxi = int(age_df.index.max().left)
                for r in range(0, maxi + 2):
                    for v in age_df.loc[r]:
                        assert not pd.isna(v)

    for i in sp.index.get_level_values(0).unique():
        scaled = sp.loc[i]
        mini = int(scaled.index.min())
        maxi = int(scaled.index.max())
        for r in range(mini, maxi + 1):
            for v in scaled.loc[r]:
                assert not pd.isna(v)


def test_dtvpa_data():
    std, sums = dtvpa.load()

    for i in std.index.get_level_values(0).unique():
        for y in range(11, 18):
            age = relativedelta(years=y)
            age_df = std.loc[i].loc[time.delta_idx(age)]
            maxi = int(age_df.index.max().left)
            for r in range(0, maxi + 2):
                for v in age_df.loc[r]:
                    assert not pd.isna(v)

    for i in sums.index.get_level_values(0).unique():
        idxs = sums.loc[i]
        mini = int(idxs.index.min())
        maxi = int(idxs.index.max())
        for r in range(mini, maxi + 1):
            for v in idxs.loc[r]:
                assert not pd.isna(v)


def test_mabc_data():
    map_i, map_t = mabc.load()

    for y in range(5, 16):
        age = relativedelta(years=y)
        age_df = map_i.loc[time.delta_idx(age)]
        for i in age_df.index.get_level_values(0).unique():
            maxi = int(age_df.loc[i].index.max().left)
            for r in range(0, maxi + 2):
                for v in age_df.loc[i].loc[r]:
                    assert not pd.isna(v)

    for i in map_t.index.get_level_values(0).unique():
        idxs = map_t.loc[i]
        maxi = int(idxs.index.max().left)
        for r in range(0, maxi + 2):
            for v in idxs.loc[r]:
                assert not pd.isna(v)


def test_spm_data():
    df = spm.load()

    for t in df.index.get_level_values(0).unique():
        for i in df.index.get_level_values(1).unique():
            raw = df.loc[t].loc[i]
            maxi = int(raw.index.max().left)
            for r in range(0, maxi + 2):
                for v in raw.loc[r]:
                    assert not pd.isna(v)
