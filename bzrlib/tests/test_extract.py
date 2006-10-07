# Copyright (C) 2006 Canonical Ltd
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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

from bzrlib import (
    branch, 
    errors,
    )
from bzrlib.tests import TestCaseWithTransport


class TestExtract(TestCaseWithTransport):
    
    def test_extract(self):
        self.build_tree(['a/', 'a/b/', 'a/b/c', 'a/d'])
        wt = self.make_branch_and_tree('a')
        wt.add(['b', 'b/c', 'd'], ['b-id', 'c-id', 'd-id'])
        wt.commit('added files')
        b_wt = wt.extract('b-id')
        self.assertEqual('b-id', b_wt.get_root_id())
        self.assertEqual('c-id', b_wt.path2id('c'))
        self.assertEqual('c', b_wt.id2path('c-id'))
        self.assertRaises(errors.BzrError, wt.id2path, 'b-id')
        self.assertEqual(b_wt.basedir, wt.abspath('b'))
        self.assertEqual(wt.get_parent_ids(), b_wt.get_parent_ids())

    def test_extract_in_checkout(self):
        a_branch = self.make_branch('branch')
        self.build_tree(['a/', 'a/b/', 'a/b/c/', 'a/b/c/d'])
        wt = a_branch.create_checkout('a', lightweight=True)
        wt.add(['b', 'b/c', 'b/c/d'], ['b-id', 'c-id', 'd-id'])
        wt.commit('added files')
        b_wt = wt.extract('b-id')
        b_branch = branch.Branch.open('branch/b')
        b_branch_ref = branch.Branch.open('a/b')
        self.assertEqual(b_branch.base, b_branch_ref.base)

    def test_extract_in_deep_checkout(self):
        a_branch = self.make_branch('branch')
        self.build_tree(['a/', 'a/b/', 'a/b/c/', 'a/b/c/d/', 'a/b/c/d/e'])
        wt = a_branch.create_checkout('a', lightweight=True)
        wt.add(['b', 'b/c', 'b/c/d', 'b/c/d/e/'], ['b-id', 'c-id', 'd-id',
                'e-id'])
        wt.commit('added files')
        b_wt = wt.extract('d-id')
        b_branch = branch.Branch.open('branch/b/c/d')
        b_branch_ref = branch.Branch.open('a/b/c/d')
        self.assertEqual(b_branch.base, b_branch_ref.base)
