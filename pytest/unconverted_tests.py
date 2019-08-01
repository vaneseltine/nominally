# -*- coding: utf-8 -*-
from __future__ import unicode_literals

"""
Run this file to run the tests.

``python tests.py``

Or install nose and run nosetests.

``pip install nose``

then:

``nosetests``

Post a ticket and/or clone and fix it. Pull requests with tests gladly accepted.
https://github.com/derek73/python-nameparser/issues
https://github.com/derek73/python-nameparser/pulls
"""

import logging

try:
    import dill
except ImportError:
    dill = False

from nameparser import HumanName
from nameparser.util import u
from nameparser.config import Constants

log = logging.getLogger("HumanName")

import unittest

try:
    pytest.mark.xfail
except AttributeError:
    # Python 2.6 backport
    import unittest2 as unittest


class HumanNameTestBase(unittest.TestCase):
    def m(self, actual, expected, hn):
        """assertEquals with a better message and awareness of hn.C.empty_attribute_default"""
        expected = expected or hn.C.empty_attribute_default
        try:
            self.assertEqual(
                actual,
                expected,
                "'%s' != '%s' for '%s'\n%r" % (actual, expected, hn.original, hn),
            )
        except UnicodeDecodeError:
            self.assertEquals(actual, expected)


# class MaidenNameTestCase(HumanNameTestBase):
#
#     def test_parenthesis_and_quotes_together(self):
#         hn = HumanName("Jennifer 'Jen' Jones (Duff)")
#         assert hn.first == "Jennifer"
#         assert hn.last == "Jones"
#         assert hn.nickname == "Jen"
#         assert hn.maiden == "Duff"
#
#     def test_maiden_name_with_nee(self):
#         # https://en.wiktionary.org/wiki/née
#         hn = HumanName("Mary Toogood nee Johnson")
#         assert hn.first == "Mary"
#         assert hn.last == "Toogood"
#         assert hn.maiden == "Johnson"
#
#     def test_maiden_name_with_accented_nee(self):
#         # https://en.wiktionary.org/wiki/née
#         hn = HumanName("Mary Toogood née Johnson")
#         assert hn.first == "Mary"
#         assert hn.last == "Toogood"
#         assert hn.maiden == "Johnson"
#
#     def test_maiden_name_with_nee_and_comma(self):
#         # https://en.wiktionary.org/wiki/née
#         hn = HumanName("Mary Toogood, née Johnson")
#         assert hn.first == "Mary"
#         assert hn.last == "Toogood"
#         assert hn.maiden == "Johnson"
#
#     def test_maiden_name_with_nee_with_parenthesis(self):
#         hn = HumanName("Mary Toogood (nee Johnson)")
#         assert hn.first == "Mary"
#         assert hn.last == "Toogood"
#         assert hn.maiden == "Johnson"
#
#     def test_maiden_name_with_parenthesis(self):
#         hn = HumanName("Mary Toogood (Johnson)")
#         assert hn.first == "Mary"
#         assert hn.last == "Toogood"
#         assert hn.maiden == "Johnson"
#


class HumanNameVariationTests(HumanNameTestBase):
    # test automated variations of names in TEST_NAMES.
    # Helps test that the 3 code trees work the same

    TEST_NAMES = (
        "John Doe",
        "John Doe, Jr.",
        "John Doe III",
        "Doe, John",
        "Doe, John, Jr.",
        "Doe, John III",
        "John A. Doe",
        "John A. Doe, Jr.",
        "John A. Doe III",
        "Doe, John A.",
        "Doe, John A., Jr.",
        "Doe, John A. III",
        "John A. Kenneth Doe",
        "John A. Kenneth Doe, Jr.",
        "John A. Kenneth Doe III",
        "Doe, John A. Kenneth",
        "Doe, John A. Kenneth, Jr.",
        "Doe, John A. Kenneth III",
        "Dr. John Doe",
        "Dr. John Doe, Jr.",
        "Dr. John Doe III",
        "Doe, Dr. John",
        "Doe, Dr. John, Jr.",
        "Doe, Dr. John III",
        "Dr. John A. Doe",
        "Dr. John A. Doe, Jr.",
        "Dr. John A. Doe III",
        "Doe, Dr. John A.",
        "Doe, Dr. John A. Jr.",
        "Doe, Dr. John A. III",
        "Dr. John A. Kenneth Doe",
        "Dr. John A. Kenneth Doe, Jr.",
        "Dr. John A. Kenneth Doe III",
        "Doe, Dr. John A. Kenneth",
        "Doe, Dr. John A. Kenneth Jr.",
        "Doe, Dr. John A. Kenneth III",
        "Juan de la Vega",
        "Juan de la Vega, Jr.",
        "Juan de la Vega III",
        "de la Vega, Juan",
        "de la Vega, Juan, Jr.",
        "de la Vega, Juan III",
        "Juan Velasquez y Garcia",
        "Juan Velasquez y Garcia, Jr.",
        "Juan Velasquez y Garcia III",
        "Velasquez y Garcia, Juan",
        "Velasquez y Garcia, Juan, Jr.",
        "Velasquez y Garcia, Juan III",
        "Dr. Juan de la Vega",
        "Dr. Juan de la Vega, Jr.",
        "Dr. Juan de la Vega III",
        "de la Vega, Dr. Juan",
        "de la Vega, Dr. Juan, Jr.",
        "de la Vega, Dr. Juan III",
        "Dr. Juan Velasquez y Garcia",
        "Dr. Juan Velasquez y Garcia, Jr.",
        "Dr. Juan Velasquez y Garcia III",
        "Velasquez y Garcia, Dr. Juan",
        "Velasquez y Garcia, Dr. Juan, Jr.",
        "Velasquez y Garcia, Dr. Juan III",
        "Juan Q. de la Vega",
        "Juan Q. de la Vega, Jr.",
        "Juan Q. de la Vega III",
        "de la Vega, Juan Q.",
        "de la Vega, Juan Q., Jr.",
        "de la Vega, Juan Q. III",
        "Juan Q. Velasquez y Garcia",
        "Juan Q. Velasquez y Garcia, Jr.",
        "Juan Q. Velasquez y Garcia III",
        "Velasquez y Garcia, Juan Q.",
        "Velasquez y Garcia, Juan Q., Jr.",
        "Velasquez y Garcia, Juan Q. III",
        "Dr. Juan Q. de la Vega",
        "Dr. Juan Q. de la Vega, Jr.",
        "Dr. Juan Q. de la Vega III",
        "de la Vega, Dr. Juan Q.",
        "de la Vega, Dr. Juan Q., Jr.",
        "de la Vega, Dr. Juan Q. III",
        "Dr. Juan Q. Velasquez y Garcia",
        "Dr. Juan Q. Velasquez y Garcia, Jr.",
        "Dr. Juan Q. Velasquez y Garcia III",
        "Velasquez y Garcia, Dr. Juan Q.",
        "Velasquez y Garcia, Dr. Juan Q., Jr.",
        "Velasquez y Garcia, Dr. Juan Q. III",
        "Juan Q. Xavier de la Vega",
        "Juan Q. Xavier de la Vega, Jr.",
        "Juan Q. Xavier de la Vega III",
        "de la Vega, Juan Q. Xavier",
        "de la Vega, Juan Q. Xavier, Jr.",
        "de la Vega, Juan Q. Xavier III",
        "Juan Q. Xavier Velasquez y Garcia",
        "Juan Q. Xavier Velasquez y Garcia, Jr.",
        "Juan Q. Xavier Velasquez y Garcia III",
        "Velasquez y Garcia, Juan Q. Xavier",
        "Velasquez y Garcia, Juan Q. Xavier, Jr.",
        "Velasquez y Garcia, Juan Q. Xavier III",
        "Dr. Juan Q. Xavier de la Vega",
        "Dr. Juan Q. Xavier de la Vega, Jr.",
        "Dr. Juan Q. Xavier de la Vega III",
        "de la Vega, Dr. Juan Q. Xavier",
        "de la Vega, Dr. Juan Q. Xavier, Jr.",
        "de la Vega, Dr. Juan Q. Xavier III",
        "Dr. Juan Q. Xavier Velasquez y Garcia",
        "Dr. Juan Q. Xavier Velasquez y Garcia, Jr.",
        "Dr. Juan Q. Xavier Velasquez y Garcia III",
        "Velasquez y Garcia, Dr. Juan Q. Xavier",
        "Velasquez y Garcia, Dr. Juan Q. Xavier, Jr.",
        "Velasquez y Garcia, Dr. Juan Q. Xavier III",
        "John Doe, CLU, CFP, LUTC",
        "John P. Doe, CLU, CFP, LUTC",
        "Dr. John P. Doe-Ray, CLU, CFP, LUTC",
        "Doe-Ray, Dr. John P., CLU, CFP, LUTC",
        "Hon. Barrington P. Doe-Ray, Jr.",
        "Doe-Ray, Hon. Barrington P. Jr.",
        "Doe-Ray, Hon. Barrington P. Jr., CFP, LUTC",
        "Jose Aznar y Lopez",
        "John E Smith",
        "John e Smith",
        "John and Jane Smith",
        "Rev. John A. Kenneth Doe",
        "Donovan McNabb-Smith",
        "Rev John A. Kenneth Doe",
        "Doe, Rev. John A. Jr.",
        "Buca di Beppo",
        "Lt. Gen. John A. Kenneth Doe, Jr.",
        "Doe, Lt. Gen. John A. Kenneth IV",
        "Lt. Gen. John A. Kenneth Doe IV",
        "Mr. and Mrs. John Smith",
        "John Jones (Google Docs)",
        "john e jones",
        "john e jones, III",
        "jones, john e",
        "E.T. Smith",
        "E.T. Smith, II",
        "Smith, E.T., Jr.",
        "A.B. Vajpayee",
        "Rt. Hon. Paul E. Mary",
        "Maid Marion",
        "Amy E. Maid",
        "Jane Doctor",
        "Doctor, Jane E.",
        "dr. ben alex johnson III",
        "Lord of the Universe and Supreme King of the World Lisa Simpson",
        "Benjamin (Ben) Franklin",
        'Benjamin "Ben" Franklin',
        "Brian O'connor",
        "Sir Gerald",
        "Magistrate Judge John F. Forster, Jr",
        # "Magistrate Judge Joaquin V.E. Manibusan, Jr", Intials seem to mess this up
        "Magistrate-Judge Elizabeth Todd Campbell",
        "Mag-Judge Harwell G Davis, III",
        "Mag. Judge Byron G. Cudmore",
        "Chief Judge J. Leon Holmes",
        "Chief Judge Sharon Lovelace Blackburn",
        "Judge James M. Moody",
        "Judge G. Thomas Eisele",
        # "Judge Callie V. S. Granade",
        "Judge C Lynwood Smith, Jr",
        "Senior Judge Charles R. Butler, Jr",
        "Senior Judge Harold D. Vietor",
        "Senior Judge Virgil Pittman",
        "Honorable Terry F. Moorer",
        "Honorable W. Harold Albritton, III",
        "Honorable Judge W. Harold Albritton, III",
        "Honorable Judge Terry F. Moorer",
        "Honorable Judge Susan Russ Walker",
        "Hon. Marian W. Payson",
        "Hon. Charles J. Siragusa",
        "US Magistrate Judge T Michael Putnam",
        "Designated Judge David A. Ezra",
        "Sr US District Judge Richard G Kopf",
        "U.S. District Judge Marc Thomas Treadwell",
        "Dra. Andréia da Silva",
        "Srta. Andréia da Silva",
    )

    def test_variations_of_TEST_NAMES(self):
        for name in self.TEST_NAMES:
            hn = HumanName(name)
            if len(hn.suffix_list) > 1:
                hn = HumanName(
                    "{title} {first} {middle} {last} {suffix}".format(
                        **hn.as_dict()
                    ).split(",")[0]
                )
            # format strings below require empty string
            hn.C.empty_attribute_default = ""
            hn_dict = hn.as_dict()
            nocomma = HumanName(
                "{title} {first} {middle} {last} {suffix}".format(**hn_dict)
            )
            lastnamecomma = HumanName(
                "{last}, {title} {first} {middle} {suffix}".format(**hn_dict)
            )
            if hn.suffix:
                suffixcomma = HumanName(
                    "{title} {first} {middle} {last}, {suffix}".format(**hn_dict)
                )
            if hn.nickname:
                nocomma = HumanName(
                    "{title} {first} {middle} {last} {suffix} ({nickname})".format(
                        **hn_dict
                    )
                )
                lastnamecomma = HumanName(
                    "{last}, {title} {first} {middle} {suffix} ({nickname})".format(
                        **hn_dict
                    )
                )
                if hn.suffix:
                    suffixcomma = HumanName(
                        "{title} {first} {middle} {last}, {suffix} ({nickname})".format(
                            **hn_dict
                        )
                    )
            for attr in hn._members:
                assert getattr(hn == attr), getattr(nocomma, attr)
                assert getattr(hn == attr), getattr(lastnamecomma, attr)
                if hn.suffix:
                    assert getattr(hn == attr), getattr(suffixcomma, attr)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        log.setLevel(logging.ERROR)
        log.addHandler(logging.StreamHandler())
        name_string = sys.argv[1]
        hn_instance = HumanName(name_string, encoding=sys.stdout.encoding)
        print((repr(hn_instance)))
        hn_instance.capitalize()
        print((repr(hn_instance)))
    else:
        print("-" * 80)
        print("Running tests")
        unittest.main(exit=False)
        print("-" * 80)
        print("Running tests with empty_attribute_default = None")
        from nameparser.config import CONSTANTS

        CONSTANTS.empty_attribute_default = None
        unittest.main()
