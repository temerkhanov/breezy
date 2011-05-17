# Copyright (C) 2011 Canonical Ltd
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA


"""Tests for the per file graph API."""


from bzrlib.tests.per_repository import TestCaseWithRepository


class TestPerFileGraph(TestCaseWithRepository):

    def test_file_graph(self):
        tree = self.make_branch_and_tree('.')
        self.build_tree_contents([("a", "contents")])
        tree.add(["a"], ["fileid"])
        revid1 = tree.commit("msg")
        self.build_tree_contents([("a", "new contents")])
        revid2 = tree.commit("msg")
        self.addCleanup(tree.lock_read().unlock)
        graph = tree.branch.repository.get_file_graph()
        self.assertEquals({
            ("fileid", revid2): (("fileid", revid1),), ("fileid", revid1):()},
            graph.get_parent_map([("fileid", revid2), ("fileid", revid1)]))
