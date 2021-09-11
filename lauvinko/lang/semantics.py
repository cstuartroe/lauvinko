from typing import Set
from enum import Enum


class PrimaryTenseAspect(Enum):
    GENERAL = "general"
    NONPAST = "nonpast"
    PAST = "past"
    IMPERFECTIVE_NONPAST = "nonpast imperfective"
    IMPERFECTIVE_PAST = "past imperfective"
    PERFECTIVE = "perfective"
    INCEPTIVE = "inceptive"
    FREQUENTATIVE_NONPAST = "nonpast frequentative"
    FREQUENTATIVE_PAST = "nonpast frequentative"


class StemCategory:
    def __init__(self, title: str, primary_aspects: Set[PrimaryTenseAspect], citation_form: PrimaryTenseAspect):
        assert citation_form in primary_aspects

        if PrimaryTenseAspect.GENERAL in primary_aspects:
            assert PrimaryTenseAspect.NONPAST not in primary_aspects
            assert PrimaryTenseAspect.IMPERFECTIVE_NONPAST not in primary_aspects
            assert PrimaryTenseAspect.IMPERFECTIVE_PAST not in primary_aspects

        if len({PrimaryTenseAspect.NONPAST, PrimaryTenseAspect.PAST} & primary_aspects) > 0:
            assert PrimaryTenseAspect.IMPERFECTIVE_NONPAST not in primary_aspects
            assert PrimaryTenseAspect.IMPERFECTIVE_PAST not in primary_aspects

        self.title = title
        self.primary_aspects = primary_aspects
        self.citation_form = citation_form


class KasanicStemCategory(StemCategory, Enum):
    FIENTIVE = (
        "fientive",
        {
            PrimaryTenseAspect.IMPERFECTIVE_NONPAST,
            PrimaryTenseAspect.IMPERFECTIVE_PAST,
            PrimaryTenseAspect.PERFECTIVE,
            PrimaryTenseAspect.INCEPTIVE,
            PrimaryTenseAspect.FREQUENTATIVE_NONPAST,
            PrimaryTenseAspect.FREQUENTATIVE_PAST,
        },
        PrimaryTenseAspect.IMPERFECTIVE_PAST,
    )

    PUNCTUAL = (
        "punctual",
        {
            PrimaryTenseAspect.NONPAST,
            PrimaryTenseAspect.PAST,
            PrimaryTenseAspect.FREQUENTATIVE_NONPAST,
            PrimaryTenseAspect.FREQUENTATIVE_PAST,
        },
        PrimaryTenseAspect.NONPAST,
    )

    STATIVE = (
        "stative",
        {
            PrimaryTenseAspect.GENERAL,
            PrimaryTenseAspect.PAST,
            PrimaryTenseAspect.INCEPTIVE,
        },
        PrimaryTenseAspect.GENERAL,
    )

    UNINFLECTED = (
        "uninflected",
        {
            PrimaryTenseAspect.GENERAL,
        },
        PrimaryTenseAspect.GENERAL,
    )
