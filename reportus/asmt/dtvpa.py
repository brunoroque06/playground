import dataclasses
import itertools
from datetime import date

import polars as pl
import streamlit as st
from dateutil.relativedelta import relativedelta

from asmt import dtvp, time


@dataclasses.dataclass(frozen=True)
class Data:
    std: pl.DataFrame
    sums: pl.DataFrame

    def get_std(self, i: str, age: relativedelta, r: int):
        return self.std.filter(
            (pl.col("id") == i)
            & (pl.col("age_min") <= age.years)
            & (pl.col("age_max") > age.years)
            & (pl.col("raw_min") <= r)
            & (pl.col("raw_max") >= r)
        )

    def get_sum(self, i: str, su: int):
        return self.sums.filter((pl.col("id") == i) & (pl.col("sum") == su))


@st.cache_data
def _load() -> Data:
    std = pl.read_csv("data/dtvpa-std.csv")
    sums = pl.read_csv("data/dtvpa-sum.csv")
    return Data(std, sums)


def validate():
    data = _load()
    ids = get_tests().keys()
    ages = range(11, 18)
    raws = range(0, 109)

    for i, a, r in itertools.product(ids, ages, raws):
        row = data.get_std(i, relativedelta(years=a), r)
        assert row.select("standard").item() > 0
        assert row.select("percentile").item() >= 0

    for i, su in itertools.chain(
        itertools.product(["sum3"], range(3, 61)),
        itertools.product(["sum6"], range(6, 116)),
    ):
        row = data.get_sum(i, su)
        assert row.select("index").item() > 0
        assert row.select("percentile").item() >= 0


def get_tests():
    return {
        "co": "Copying",
        "fg": "Figure-Ground",
        "vse": "Visual-Motor Search",
        "vc": "Visual Closure",
        "vsp": "Visual-Motor Speed",
        "fc": "Form Constancy",
    }


def report(asmt: date, sub: pl.DataFrame, comp: pl.DataFrame) -> str:
    return "\n".join(
        [
            f"Developmental Test of Visual Perception - Adolescent and Adult (DTVP-A) - ({time.format_date(asmt)})",
            "",
        ]
        + [
            f"{n}: PR {comp.filter(pl.col('id') == i).select('%ile').item()} - {dtvp.desc_index(comp.filter(pl.col('id') == i).select('index').item(), True)}"
            for n, i in [
                ("Visuomotorische Integration", "Visual-Motor Integration (VMII)"),
                (
                    "Motorik-Reduzierte Wahrnehmung",
                    "Motor-Reduced Visual Perception (MRPI)",
                ),
                ("Globale Visuelle Wahrnehmung", "General Visual Perception (GVPI)"),
            ]
        ]
        + [
            "",
            "Subtests:",
        ]
        + [
            f"{n}: PR {sub.filter(pl.col('id') == i).select('%ile').item()} - {dtvp.desc_sca(sub.filter(pl.col('id') == i).select('standard').item(), True)}"
            for n, i in [
                ("Abzeichnen", "co"),
                ("Figur-Grund", "fg"),
                ("Visuomotorisches Suchen", "vse"),
                ("Gesaltschliessen", "vc"),
                ("Visuomotorische Geschwindigkeit", "vsp"),
                ("Formkonstanz", "fc"),
            ]
        ]
    )


def process(
    age: relativedelta, raw: dict[str, int], asmt: date | None = None
) -> tuple[pl.DataFrame, pl.DataFrame, str]:
    if asmt is None:
        asmt = date.today()

    data = _load()

    tests = get_tests()

    def get_std(k: str, r: int):
        row = data.get_std(k, age, r)
        per = row.select("percentile").item()
        std = row.select("standard").item()
        return [
            dtvp.to_pr(per),
            std,
            dtvp.desc_sca(std),
        ]

    sub = pl.DataFrame(
        [[k, v, raw[k], *get_std(k, raw[k])] for k, v in tests.items()],
        schema=["id", "label", "raw", "%ile", "standard", "description"],
    )

    comps = [
        (
            "gvpi",
            "General Visual Perception (GVPI)",
            sub.select("standard").sum().item(),
            "sum6",
        ),
        (
            "mrpi",
            "Motor-Reduced Visual Perception (MRPI)",
            sub.filter(pl.col("id") == "fg").select("standard").item()
            + sub.filter(pl.col("id") == "vc").select("standard").item()
            + sub.filter(pl.col("id") == "fc").select("standard").item(),
            "sum3",
        ),
        (
            "vmii",
            "Visual-Motor Integration (VMII)",
            sub.filter(pl.col("id") == "co").select("standard").item()
            + sub.filter(pl.col("id") == "vse").select("standard").item()
            + sub.filter(pl.col("id") == "vsp").select("standard").item(),
            "sum3",
        ),
    ]

    def get_comp(i, su):
        row = data.get_sum(i, su)
        idx = row.select("index").item()
        return [idx, dtvp.to_pr(row.select("percentile").item()), dtvp.desc_index(idx)]

    comp = pl.DataFrame(
        [[l, su] + get_comp(i, su) for _, l, su, i in comps],
        schema=["id", "sum_standard", "index", "%ile", "description"],
    )

    return (
        sub.to_pandas().drop(columns=["id"]).set_index("label"),
        comp.to_pandas().set_index("id"),
        report(asmt, sub, comp),
    )
