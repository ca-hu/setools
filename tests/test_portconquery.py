# Copyright 2014, Tresys Technology, LLC
#
# SPDX-License-Identifier: GPL-2.0-only
#
import os
import unittest
from socket import IPPROTO_UDP

from setools import PortconQuery, PortconRange

from .policyrep.util import compile_policy


class PortconQueryTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.p = compile_policy("tests/portconquery.conf")

    @classmethod
    def tearDownClass(cls):
        os.unlink(cls.p.path)

    def test_000_unset(self):
        """Portcon query with no criteria"""
        # query with no parameters gets all ports.
        rules = sorted(self.p.portcons())

        q = PortconQuery(self.p)
        q_rules = sorted(q.results())

        self.assertListEqual(rules, q_rules)

    def test_001_protocol(self):
        """Portcon query with protocol match"""
        q = PortconQuery(self.p, protocol=IPPROTO_UDP)

        ports = sorted(p.ports for p in q.results())
        self.assertListEqual([PortconRange(1, 1)], ports)

    def test_010_user_exact(self):
        """Portcon query with context user exact match"""
        q = PortconQuery(self.p, user="user10", user_regex=False)

        ports = sorted(p.ports for p in q.results())
        self.assertListEqual([PortconRange(10, 10)], ports)

    def test_011_user_regex(self):
        """Portcon query with context user regex match"""
        q = PortconQuery(self.p, user="user11(a|b)", user_regex=True)

        ports = sorted(p.ports for p in q.results())
        self.assertListEqual([PortconRange(11, 11), PortconRange(11000, 11000)], ports)

    def test_020_role_exact(self):
        """Portcon query with context role exact match"""
        q = PortconQuery(self.p, role="role20_r", role_regex=False)

        ports = sorted(p.ports for p in q.results())
        self.assertListEqual([PortconRange(20, 20)], ports)

    def test_021_role_regex(self):
        """Portcon query with context role regex match"""
        q = PortconQuery(self.p, role="role21(a|c)_r", role_regex=True)

        ports = sorted(p.ports for p in q.results())
        self.assertListEqual([PortconRange(21, 21), PortconRange(21001, 21001)], ports)

    def test_030_type_exact(self):
        """Portcon query with context type exact match"""
        q = PortconQuery(self.p, type_="type30", type_regex=False)

        ports = sorted(p.ports for p in q.results())
        self.assertListEqual([PortconRange(30, 30)], ports)

    def test_031_type_regex(self):
        """Portcon query with context type regex match"""
        q = PortconQuery(self.p, type_="type31(b|c)", type_regex=True)

        ports = sorted(p.ports for p in q.results())
        self.assertListEqual([PortconRange(31000, 31000), PortconRange(31001, 31001)], ports)

    def test_040_range_exact(self):
        """Portcon query with context range exact match"""
        q = PortconQuery(self.p, range_="s0:c1 - s0:c0.c4")

        ports = sorted(p.ports for p in q.results())
        self.assertListEqual([PortconRange(40, 40)], ports)

    def test_041_range_overlap1(self):
        """Portcon query with context range overlap match (equal)"""
        q = PortconQuery(self.p, range_="s1:c1 - s1:c0.c4", range_overlap=True)

        ports = sorted(p.ports for p in q.results())
        self.assertListEqual([PortconRange(41, 41)], ports)

    def test_041_range_overlap2(self):
        """Portcon query with context range overlap match (subset)"""
        q = PortconQuery(self.p, range_="s1:c1,c2 - s1:c0.c3", range_overlap=True)

        ports = sorted(p.ports for p in q.results())
        self.assertListEqual([PortconRange(41, 41)], ports)

    def test_041_range_overlap3(self):
        """Portcon query with context range overlap match (superset)"""
        q = PortconQuery(self.p, range_="s1 - s1:c0.c4", range_overlap=True)

        ports = sorted(p.ports for p in q.results())
        self.assertListEqual([PortconRange(41, 41)], ports)

    def test_041_range_overlap4(self):
        """Portcon query with context range overlap match (overlap low level)"""
        q = PortconQuery(self.p, range_="s1 - s1:c1,c2", range_overlap=True)

        ports = sorted(p.ports for p in q.results())
        self.assertListEqual([PortconRange(41, 41)], ports)

    def test_041_range_overlap5(self):
        """Portcon query with context range overlap match (overlap high level)"""
        q = PortconQuery(self.p, range_="s1:c1,c2 - s1:c0.c4", range_overlap=True)

        ports = sorted(p.ports for p in q.results())
        self.assertListEqual([PortconRange(41, 41)], ports)

    def test_042_range_subset1(self):
        """Portcon query with context range subset match"""
        q = PortconQuery(self.p, range_="s2:c1,c2 - s2:c0.c3", range_overlap=True)

        ports = sorted(p.ports for p in q.results())
        self.assertListEqual([PortconRange(42, 42)], ports)

    def test_042_range_subset2(self):
        """Portcon query with context range subset match (equal)"""
        q = PortconQuery(self.p, range_="s2:c1 - s2:c1.c3", range_overlap=True)

        ports = sorted(p.ports for p in q.results())
        self.assertListEqual([PortconRange(42, 42)], ports)

    def test_043_range_superset1(self):
        """Portcon query with context range superset match"""
        q = PortconQuery(self.p, range_="s3 - s3:c0.c4", range_superset=True)

        ports = sorted(p.ports for p in q.results())
        self.assertListEqual([PortconRange(43, 43)], ports)

    def test_043_range_superset2(self):
        """Portcon query with context range superset match (equal)"""
        q = PortconQuery(self.p, range_="s3:c1 - s3:c1.c3", range_superset=True)

        ports = sorted(p.ports for p in q.results())
        self.assertListEqual([PortconRange(43, 43)], ports)

    def test_044_range_proper_subset1(self):
        """Portcon query with context range proper subset match"""
        q = PortconQuery(self.p, range_="s4:c1,c2", range_subset=True, range_proper=True)

        ports = sorted(p.ports for p in q.results())
        self.assertListEqual([PortconRange(44, 44)], ports)

    def test_044_range_proper_subset2(self):
        """Portcon query with context range proper subset match (equal)"""
        q = PortconQuery(self.p, range_="s4:c1 - s4:c1.c3", range_subset=True, range_proper=True)

        ports = sorted(p.ports for p in q.results())
        self.assertListEqual([], ports)

    def test_044_range_proper_subset3(self):
        """Portcon query with context range proper subset match (equal low only)"""
        q = PortconQuery(self.p, range_="s4:c1 - s4:c1.c2", range_subset=True, range_proper=True)

        ports = sorted(p.ports for p in q.results())
        self.assertListEqual([PortconRange(44, 44)], ports)

    def test_044_range_proper_subset4(self):
        """Portcon query with context range proper subset match (equal high only)"""
        q = PortconQuery(self.p, range_="s4:c1,c2 - s4:c1.c3", range_subset=True, range_proper=True)

        ports = sorted(p.ports for p in q.results())
        self.assertListEqual([PortconRange(44, 44)], ports)

    def test_045_range_proper_superset1(self):
        """Portcon query with context range proper superset match"""
        q = PortconQuery(self.p, range_="s5 - s5:c0.c4", range_superset=True, range_proper=True)

        ports = sorted(p.ports for p in q.results())
        self.assertListEqual([PortconRange(45, 45)], ports)

    def test_045_range_proper_superset2(self):
        """Portcon query with context range proper superset match (equal)"""
        q = PortconQuery(self.p, range_="s5:c1 - s5:c1.c3", range_superset=True, range_proper=True)

        ports = sorted(p.ports for p in q.results())
        self.assertListEqual([], ports)

    def test_045_range_proper_superset3(self):
        """Portcon query with context range proper superset match (equal low)"""
        q = PortconQuery(self.p, range_="s5:c1 - s5:c1.c4", range_superset=True, range_proper=True)

        ports = sorted(p.ports for p in q.results())
        self.assertListEqual([PortconRange(45, 45)], ports)

    def test_045_range_proper_superset4(self):
        """Portcon query with context range proper superset match (equal high)"""
        q = PortconQuery(self.p, range_="s5 - s5:c1.c3", range_superset=True, range_proper=True)

        ports = sorted(p.ports for p in q.results())
        self.assertListEqual([PortconRange(45, 45)], ports)

    def test_050_single_equal(self):
        """Portcon query with single port exact match"""
        q = PortconQuery(self.p, ports=(50, 50))

        ports = sorted(p.ports for p in q.results())
        self.assertListEqual([PortconRange(50, 50)], ports)

    def test_051_range_equal(self):
        """Portcon query with port range exact match"""
        q = PortconQuery(self.p, ports=(50100, 50110))

        ports = sorted(p.ports for p in q.results())
        self.assertListEqual([PortconRange(50100, 50110)], ports)

    def test_052_single_subset(self):
        """Portcon query with single port subset"""
        q = PortconQuery(self.p, ports=(50200, 50200), ports_subset=True)

        ports = sorted(p.ports for p in q.results())
        self.assertListEqual([PortconRange(50200, 50200)], ports)

    def test_053_range_subset(self):
        """Portcon query with range subset"""
        q = PortconQuery(self.p, ports=(50301, 50309), ports_subset=True)

        ports = sorted(p.ports for p in q.results())
        self.assertListEqual([PortconRange(50300, 50310)], ports)

    def test_053_range_subset_edge1(self):
        """Portcon query with range subset, equal edge case"""
        q = PortconQuery(self.p, ports=(50300, 50310), ports_subset=True)

        ports = sorted(p.ports for p in q.results())
        self.assertListEqual([PortconRange(50300, 50310)], ports)

    def test_054_single_proper_subset(self):
        """Portcon query with single port proper subset"""
        q = PortconQuery(
            self.p, ports=(50400, 50400), ports_subset=True, ports_proper=True)

        ports = sorted(p.ports for p in q.results())
        self.assertListEqual([], ports)

    def test_055_range_proper_subset(self):
        """Portcon query with range proper subset"""
        q = PortconQuery(
            self.p, ports=(50501, 50509), ports_subset=True, ports_proper=True)

        ports = sorted(p.ports for p in q.results())
        self.assertListEqual([PortconRange(50500, 50510)], ports)

    def test_055_range_proper_subset_edge1(self):
        """Portcon query with range proper subset, equal edge case"""
        q = PortconQuery(
            self.p, ports=(50500, 50510), ports_subset=True, ports_proper=True)

        ports = sorted(p.ports for p in q.results())
        self.assertListEqual([], ports)

    def test_055_range_proper_subset_edge2(self):
        """Portcon query with range proper subset, low equal edge case"""
        q = PortconQuery(
            self.p, ports=(50500, 50509), ports_subset=True, ports_proper=True)

        ports = sorted(p.ports for p in q.results())
        self.assertListEqual([PortconRange(50500, 50510)], ports)

    def test_055_range_proper_subset_edge3(self):
        """Portcon query with range proper subset, high equal edge case"""
        q = PortconQuery(
            self.p, ports=(50501, 50510), ports_subset=True, ports_proper=True)

        ports = sorted(p.ports for p in q.results())
        self.assertListEqual([PortconRange(50500, 50510)], ports)

    def test_056_single_superset(self):
        """Portcon query with single port superset"""
        q = PortconQuery(self.p, ports=(50600, 50602), ports_superset=True)

        ports = sorted(p.ports for p in q.results())
        self.assertListEqual([PortconRange(50601, 50601)], ports)

    def test_056_single_superset_edge1(self):
        """Portcon query with single port superset, equal edge case"""
        q = PortconQuery(self.p, ports=(50601, 50601), ports_superset=True)

        ports = sorted(p.ports for p in q.results())
        self.assertListEqual([PortconRange(50601, 50601)], ports)

    def test_057_range_superset(self):
        """Portcon query with range superset"""
        q = PortconQuery(self.p, ports=(50700, 50711), ports_superset=True)

        ports = sorted(p.ports for p in q.results())
        self.assertListEqual([PortconRange(50700, 50710)], ports)

    def test_057_range_superset_edge1(self):
        """Portcon query with range superset, equal edge case"""
        q = PortconQuery(self.p, ports=(50700, 50710), ports_superset=True)

        ports = sorted(p.ports for p in q.results())
        self.assertListEqual([PortconRange(50700, 50710)], ports)

    def test_058_single_proper_superset(self):
        """Portcon query with single port proper superset"""
        q = PortconQuery(
            self.p, ports=(50800, 50802), ports_superset=True, ports_proper=True)

        ports = sorted(p.ports for p in q.results())
        self.assertListEqual([PortconRange(50801, 50801)], ports)

    def test_058_single_proper_superset_edge1(self):
        """Portcon query with single port proper superset, equal edge case"""
        q = PortconQuery(
            self.p, ports=(50801, 50801), ports_superset=True, ports_proper=True)

        ports = sorted(p.ports for p in q.results())
        self.assertListEqual([], ports)

    def test_058_single_proper_superset_edge2(self):
        """Portcon query with single port proper superset, low equal edge case"""
        q = PortconQuery(
            self.p, ports=(50801, 50802), ports_superset=True, ports_proper=True)

        ports = sorted(p.ports for p in q.results())
        self.assertListEqual([PortconRange(50801, 50801)], ports)

    def test_058_single_proper_superset_edge3(self):
        """Portcon query with single port proper superset, high equal edge case"""
        q = PortconQuery(
            self.p, ports=(50800, 50801), ports_superset=True, ports_proper=True)

        ports = sorted(p.ports for p in q.results())
        self.assertListEqual([PortconRange(50801, 50801)], ports)

    def test_059_range_proper_superset(self):
        """Portcon query with range proper superset"""
        q = PortconQuery(
            self.p, ports=(50900, 50911), ports_superset=True, ports_proper=True)

        ports = sorted(p.ports for p in q.results())
        self.assertListEqual([PortconRange(50901, 50910)], ports)

    def test_059_range_proper_superset_edge1(self):
        """Portcon query with range proper superset, equal edge case"""
        q = PortconQuery(
            self.p, ports=(50901, 50910), ports_superset=True, ports_proper=True)

        ports = sorted(p.ports for p in q.results())
        self.assertListEqual([], ports)

    def test_059_range_proper_superset_edge2(self):
        """Portcon query with range proper superset, equal high port edge case"""
        q = PortconQuery(
            self.p, ports=(50900, 50910), ports_superset=True, ports_proper=True)

        ports = sorted(p.ports for p in q.results())
        self.assertListEqual([PortconRange(50901, 50910)], ports)

    def test_059_range_proper_superset_edge3(self):
        """Portcon query with range proper superset, equal low port edge case"""
        q = PortconQuery(
            self.p, ports=(50901, 50911), ports_superset=True, ports_proper=True)

        ports = sorted(p.ports for p in q.results())
        self.assertListEqual([PortconRange(50901, 50910)], ports)

    def test_060_single_overlap(self):
        """Portcon query with single overlap"""
        q = PortconQuery(self.p, ports=(60001, 60001), ports_overlap=True)

        ports = sorted(p.ports for p in q.results())
        self.assertListEqual([PortconRange(60001, 60001)], ports)

    def test_060_single_overlap_edge1(self):
        """Portcon query with single overlap, range match low"""
        q = PortconQuery(self.p, ports=(60001, 60002), ports_overlap=True)

        ports = sorted(p.ports for p in q.results())
        self.assertListEqual([PortconRange(60001, 60001)], ports)

    def test_060_single_overlap_edge2(self):
        """Portcon query with single overlap, range match high"""
        q = PortconQuery(self.p, ports=(60000, 60001), ports_overlap=True)

        ports = sorted(p.ports for p in q.results())
        self.assertListEqual([PortconRange(60001, 60001)], ports)

    def test_060_single_overlap_edge3(self):
        """Portcon query with single overlap, range match proper superset"""
        q = PortconQuery(self.p, ports=(60000, 60002), ports_overlap=True)

        ports = sorted(p.ports for p in q.results())
        self.assertListEqual([PortconRange(60001, 60001)], ports)

    def test_061_range_overlap_low_half(self):
        """Portcon query with range overlap, low half match"""
        q = PortconQuery(self.p, ports=(60100, 60105), ports_overlap=True)

        ports = sorted(p.ports for p in q.results())
        self.assertListEqual([PortconRange(60101, 60110)], ports)

    def test_062_range_overlap_high_half(self):
        """Portcon query with range overlap, high half match"""
        q = PortconQuery(self.p, ports=(60205, 60211), ports_overlap=True)

        ports = sorted(p.ports for p in q.results())
        self.assertListEqual([PortconRange(60200, 60210)], ports)

    def test_063_range_overlap_middle(self):
        """Portcon query with range overlap, middle match"""
        q = PortconQuery(self.p, ports=(60305, 60308), ports_overlap=True)

        ports = sorted(p.ports for p in q.results())
        self.assertListEqual([PortconRange(60300, 60310)], ports)

    def test_064_range_overlap_equal(self):
        """Portcon query with range overlap, equal match"""
        q = PortconQuery(self.p, ports=(60400, 60410), ports_overlap=True)

        ports = sorted(p.ports for p in q.results())
        self.assertListEqual([PortconRange(60400, 60410)], ports)

    def test_065_range_overlap_superset(self):
        """Portcon query with range overlap, superset match"""
        q = PortconQuery(self.p, ports=(60500, 60510), ports_overlap=True)

        ports = sorted(p.ports for p in q.results())
        self.assertListEqual([PortconRange(60501, 60509)], ports)
