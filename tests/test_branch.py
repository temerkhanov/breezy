# Copyright (C) 2007 Canonical Ltd
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


"""Tests for interfacing with a Git Branch"""


import dulwich
from dulwich.repo import (
    Repo as GitRepo,
    )

import os

from bzrlib import (
    errors,
    revision,
    )
from bzrlib.branch import (
    Branch,
    )
from bzrlib.bzrdir import (
    BzrDir,
    )
from bzrlib.repository import (
    Repository,
    )

from bzrlib.plugins.git import (
    branch,
    tests,
    )
from bzrlib.plugins.git.mapping import (
    default_mapping,
    )


class TestGitBranch(tests.TestCaseInTempDir):

    _test_needs_features = [tests.GitCommandFeature]

    def test_open_existing(self):
        GitRepo.init('.')

        thebranch = Branch.open('.')
        self.assertIsInstance(thebranch, branch.GitBranch)

    def test_repr(self):
        GitRepo.init('.')
        thebranch = Branch.open('.')
        self.assertEquals("LocalGitBranch('file://%s/', 'HEAD')" % self.test_dir, repr(thebranch))

    def test_last_revision_is_null(self):
        GitRepo.init('.')

        thebranch = Branch.open('.')
        self.assertEqual(revision.NULL_REVISION, thebranch.last_revision())
        self.assertEqual((0, revision.NULL_REVISION),
                         thebranch.last_revision_info())

    def simple_commit_a(self):
        GitRepo.init('.')
        self.build_tree(['a'])
        tests.run_git('add', 'a')
        tests.run_git('commit', '-m', 'a')

    def test_last_revision_is_valid(self):
        self.simple_commit_a()
        head = tests.run_git('rev-parse', 'HEAD').strip()

        thebranch = Branch.open('.')
        self.assertEqual(default_mapping.revision_id_foreign_to_bzr(head),
                         thebranch.last_revision())

    def test_revision_history(self):
        self.simple_commit_a()
        reva = tests.run_git('rev-parse', 'HEAD').strip()
        self.build_tree(['b'])
        tests.run_git('add', 'b')
        tests.run_git('commit', '-m', 'b')
        revb = tests.run_git('rev-parse', 'HEAD').strip()

        thebranch = Branch.open('.')
        self.assertEqual([default_mapping.revision_id_foreign_to_bzr(r) for r in (reva, revb)],
                         thebranch.revision_history())

    def test_tag_annotated(self):
        self.simple_commit_a()
        reva = tests.run_git('rev-parse', 'HEAD').strip()
        tests.run_git('tag', '-a', '-m', 'add tag', 'foo')
        thebranch = Branch.open('.')
        self.assertEquals({"foo": default_mapping.revision_id_foreign_to_bzr(reva)},
                          thebranch.tags.get_tag_dict())

    def test_tag(self):
        self.simple_commit_a()
        reva = tests.run_git('rev-parse', 'HEAD').strip()
        tests.run_git('tag', '-m', 'add tag', 'foo')
        thebranch = Branch.open('.')
        self.assertEquals({"foo": default_mapping.revision_id_foreign_to_bzr(reva)},
                          thebranch.tags.get_tag_dict())

        

class TestWithGitBranch(tests.TestCaseWithTransport):

    def setUp(self):
        tests.TestCaseWithTransport.setUp(self)
        dulwich.repo.Repo.create(self.test_dir)
        self.git_branch = Branch.open(self.test_dir)

    def test_get_parent(self):
        self.assertIs(None, self.git_branch.get_parent())

    def test_get_stacked_on_url(self):
        self.assertRaises(errors.UnstackableBranchFormat, 
            self.git_branch.get_stacked_on_url)

    def test_get_physical_lock_status(self):
        self.assertFalse(self.git_branch.get_physical_lock_status())


class TestGitBranchFormat(tests.TestCase):

    def setUp(self):
        super(TestGitBranchFormat, self).setUp()
        self.format = branch.GitBranchFormat()

    def test_get_format_description(self):
        self.assertEquals("Git Branch", self.format.get_format_description())



class BranchTests(tests.TestCaseInTempDir):

    def make_onerev_branch(self):
        os.mkdir("d")
        os.chdir("d")
        GitRepo.init('.')
        bb = tests.GitBranchBuilder()
        bb.set_file("foobar", "foo\nbar\n", False)
        mark = bb.commit("Somebody <somebody@someorg.org>", "mymsg")
        gitsha = bb.finish()[mark]
        os.chdir("..")
        return "d", gitsha

    def clone_git_branch(self, from_url, to_url):
        from_dir = BzrDir.open(from_url)
        to_dir = from_dir.sprout(to_url)
        return to_dir.open_branch()

    def test_single_rev(self):
        path, gitsha = self.make_onerev_branch()
        oldrepo = Repository.open(path)
        revid = oldrepo.get_mapping().revision_id_foreign_to_bzr(gitsha)
        newbranch = self.clone_git_branch(path, "f")
        self.assertEquals([revid], newbranch.repository.all_revision_ids())

    def test_sprouted_tags(self):
        path, gitsha = self.make_onerev_branch()
        os.chdir(path)
        tests.run_git("tag", "lala")
        os.chdir(self.test_dir)
        oldrepo = Repository.open(path)
        revid = oldrepo.get_mapping().revision_id_foreign_to_bzr(gitsha)
        newbranch = self.clone_git_branch(path, "f")
        self.assertEquals({"lala": revid}, newbranch.tags.get_tag_dict())
        self.assertEquals([revid], newbranch.repository.all_revision_ids())
