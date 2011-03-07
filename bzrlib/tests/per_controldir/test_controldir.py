# Copyright (C) 2006-2011 Canonical Ltd
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

"""Tests for control directory implementations - tests a controldir format."""

from itertools import izip

import bzrlib.branch
from bzrlib import (
    bzrdir,
    check,
    controldir,
    errors,
    gpg,
    osutils,
    repository,
    transport,
    ui,
    urlutils,
    workingtree,
    )
import bzrlib.revision
from bzrlib.tests import (
    fixtures,
    ChrootedTestCase,
    TestNotApplicable,
    TestSkipped,
    )
from bzrlib.tests.per_controldir import TestCaseWithControlDir
from bzrlib.transport.local import LocalTransport
from bzrlib.ui import (
    CannedInputUIFactory,
    )
from bzrlib.remote import (
    RemoteBzrDir,
    RemoteRepository,
    )


class AnonymousTestBranchFormat(bzrlib.branch.BranchFormat):
    """An anonymous branch format (does not have a format string)"""

    def get_format_string(self):
        raise NotImplementedError(self.get_format_string)


class IdentifiableTestBranchFormat(bzrlib.branch.BranchFormat):
    """An identifable branch format (has a format string)"""

    def get_format_string(self):
        return "I have an identity"


class AnonymousTestRepositoryFormat(repository.RepositoryFormat):
    """An anonymous branch format (does not have a format string)"""

    def get_format_string(self):
        raise NotImplementedError(self.get_format_string)


class IdentifiableTestRepositoryFormat(repository.RepositoryFormat):
    """An identifable branch format (has a format string)"""

    def get_format_string(self):
        return "I have an identity"


class AnonymousTestWorkingTreeFormat(workingtree.WorkingTreeFormat):
    """An anonymous branch format (does not have a format string)"""

    def get_format_string(self):
        raise NotImplementedError(self.get_format_string)


class IdentifiableTestWorkingTreeFormat(workingtree.WorkingTreeFormat):
    """An identifable branch format (has a format string)"""

    def get_format_string(self):
        return "I have an identity"


class TestControlDir(TestCaseWithControlDir):

    def skipIfNoWorkingTree(self, a_bzrdir):
        """Raises TestSkipped if a_bzrdir doesn't have a working tree.

        If the bzrdir does have a workingtree, this is a no-op.
        """
        try:
            a_bzrdir.open_workingtree()
        except (errors.NotLocalUrl, errors.NoWorkingTree):
            raise TestSkipped("bzrdir on transport %r has no working tree"
                              % a_bzrdir.transport)

    def openWorkingTreeIfLocal(self, a_bzrdir):
        """If a_bzrdir is on a local transport, call open_workingtree() on it.
        """
        if not isinstance(a_bzrdir.root_transport, LocalTransport):
            # it's not local, but that's ok
            return
        a_bzrdir.open_workingtree()

    def createWorkingTreeOrSkip(self, a_bzrdir):
        """Create a working tree on a_bzrdir, or raise TestSkipped.

        A simple wrapper for create_workingtree that translates NotLocalUrl into
        TestSkipped.  Returns the newly created working tree.
        """
        try:
            return a_bzrdir.create_workingtree()
        except (errors.NotLocalUrl, errors.UnsupportedOperation):
            raise TestSkipped("cannot make working tree with transport %r"
                              % a_bzrdir.transport)

    def sproutOrSkip(self, from_bzrdir, to_url, revision_id=None,
                     force_new_repo=False, accelerator_tree=None,
                     create_tree_if_local=True):
        """Sprout from_bzrdir into to_url, or raise TestSkipped.

        A simple wrapper for from_bzrdir.sprout that translates NotLocalUrl into
        TestSkipped.  Returns the newly sprouted bzrdir.
        """
        to_transport = transport.get_transport(to_url)
        if not isinstance(to_transport, LocalTransport):
            raise TestSkipped('Cannot sprout to remote bzrdirs.')
        target = from_bzrdir.sprout(to_url, revision_id=revision_id,
                                    force_new_repo=force_new_repo,
                                    possible_transports=[to_transport],
                                    accelerator_tree=accelerator_tree,
                                    create_tree_if_local=create_tree_if_local)
        return target

    def test_create_null_workingtree(self):
        dir = self.make_bzrdir('dir1')
        dir.create_repository()
        dir.create_branch()
        try:
            wt = dir.create_workingtree(revision_id=bzrlib.revision.NULL_REVISION)
        except (errors.NotLocalUrl, errors.UnsupportedOperation):
            raise TestSkipped("cannot make working tree with transport %r"
                              % dir.transport)
        self.assertEqual([], wt.get_parent_ids())

    def test_destroy_workingtree(self):
        tree = self.make_branch_and_tree('tree')
        self.build_tree(['tree/file'])
        tree.add('file')
        tree.commit('first commit')
        bzrdir = tree.bzrdir
        try:
            bzrdir.destroy_workingtree()
        except errors.UnsupportedOperation:
            raise TestSkipped('Format does not support destroying tree')
        self.failIfExists('tree/file')
        self.assertRaises(errors.NoWorkingTree, bzrdir.open_workingtree)
        bzrdir.create_workingtree()
        self.failUnlessExists('tree/file')
        bzrdir.destroy_workingtree_metadata()
        self.failUnlessExists('tree/file')
        self.assertRaises(errors.NoWorkingTree, bzrdir.open_workingtree)

    def test_destroy_branch(self):
        branch = self.make_branch('branch')
        bzrdir = branch.bzrdir
        try:
            bzrdir.destroy_branch()
        except (errors.UnsupportedOperation, errors.TransportNotPossible):
            raise TestNotApplicable('Format does not support destroying branch')
        self.assertRaises(errors.NotBranchError, bzrdir.open_branch)
        bzrdir.create_branch()
        bzrdir.open_branch()

    def test_destroy_repository(self):
        repo = self.make_repository('repository')
        bzrdir = repo.bzrdir
        try:
            bzrdir.destroy_repository()
        except (errors.UnsupportedOperation, errors.TransportNotPossible):
            raise TestNotApplicable('Format does not support destroying'
                                    ' repository')
        self.assertRaises(errors.NoRepositoryPresent, bzrdir.open_repository)
        bzrdir.create_repository()
        bzrdir.open_repository()

    def test_open_workingtree_raises_no_working_tree(self):
        """ControlDir.open_workingtree() should raise NoWorkingTree (rather than
        e.g. NotLocalUrl) if there is no working tree.
        """
        dir = self.make_bzrdir('source')
        vfs_dir = bzrdir.BzrDir.open(self.get_vfs_only_url('source'))
        if vfs_dir.has_workingtree():
            # This ControlDir format doesn't support ControlDirs without
            # working trees, so this test is irrelevant.
            return
        self.assertRaises(errors.NoWorkingTree, dir.open_workingtree)

    def test_clone_bzrdir_repository_under_shared(self):
        tree = self.make_branch_and_tree('commit_tree')
        self.build_tree(['foo'], transport=tree.bzrdir.transport.clone('..'))
        tree.add('foo')
        tree.commit('revision 1', rev_id='1')
        dir = self.make_bzrdir('source')
        repo = dir.create_repository()
        repo.fetch(tree.branch.repository)
        self.assertTrue(repo.has_revision('1'))
        try:
            self.make_repository('target', shared=True)
        except errors.IncompatibleFormat:
            return
        target = dir.clone(self.get_url('target/child'))
        self.assertNotEqual(dir.transport.base, target.transport.base)
        self.assertRaises(errors.NoRepositoryPresent, target.open_repository)

    def test_clone_bzrdir_repository_branch_both_under_shared(self):
        # Create a shared repository
        try:
            shared_repo = self.make_repository('shared', shared=True)
        except errors.IncompatibleFormat:
            return
        # Make a branch, 'commit_tree', and working tree outside of the shared
        # repository, and commit some revisions to it.
        tree = self.make_branch_and_tree('commit_tree')
        self.build_tree(['foo'], transport=tree.bzrdir.root_transport)
        tree.add('foo')
        tree.commit('revision 1', rev_id='1')
        tree.bzrdir.open_branch().set_revision_history([])
        tree.set_parent_trees([])
        tree.commit('revision 2', rev_id='2')
        # Copy the content (i.e. revisions) from the 'commit_tree' branch's
        # repository into the shared repository.
        tree.branch.repository.copy_content_into(shared_repo)
        # Make a branch 'source' inside the shared repository.
        dir = self.make_bzrdir('shared/source')
        dir.create_branch()
        # Clone 'source' to 'target', also inside the shared repository.
        target = dir.clone(self.get_url('shared/target'))
        # 'source', 'target', and the shared repo all have distinct bzrdirs.
        self.assertNotEqual(dir.transport.base, target.transport.base)
        self.assertNotEqual(dir.transport.base, shared_repo.bzrdir.transport.base)
        # The shared repository will contain revisions from the 'commit_tree'
        # repository, even revisions that are not part of the history of the
        # 'commit_tree' branch.
        self.assertTrue(shared_repo.has_revision('1'))

    def test_clone_bzrdir_repository_branch_only_source_under_shared(self):
        try:
            shared_repo = self.make_repository('shared', shared=True)
        except errors.IncompatibleFormat:
            return
        tree = self.make_branch_and_tree('commit_tree')
        self.build_tree(['commit_tree/foo'])
        tree.add('foo')
        tree.commit('revision 1', rev_id='1')
        tree.branch.bzrdir.open_branch().set_revision_history([])
        tree.set_parent_trees([])
        tree.commit('revision 2', rev_id='2')
        tree.branch.repository.copy_content_into(shared_repo)
        if shared_repo.make_working_trees():
            shared_repo.set_make_working_trees(False)
            self.assertFalse(shared_repo.make_working_trees())
        self.assertTrue(shared_repo.has_revision('1'))
        dir = self.make_bzrdir('shared/source')
        dir.create_branch()
        target = dir.clone(self.get_url('target'))
        self.assertNotEqual(dir.transport.base, target.transport.base)
        self.assertNotEqual(dir.transport.base, shared_repo.bzrdir.transport.base)
        branch = target.open_branch()
        self.assertTrue(branch.repository.has_revision('1'))
        self.assertFalse(branch.repository.make_working_trees())
        self.assertTrue(branch.repository.is_shared())

    def test_clone_bzrdir_repository_revision(self):
        # test for revision limiting, [smoke test, not corner case checks].
        # make a repository with some revisions,
        # and clone it with a revision limit.
        #
        tree = self.make_branch_and_tree('commit_tree')
        self.build_tree(['commit_tree/foo'])
        tree.add('foo')
        tree.commit('revision 1', rev_id='1')
        tree.branch.bzrdir.open_branch().set_revision_history([])
        tree.set_parent_trees([])
        tree.commit('revision 2', rev_id='2')
        source = self.make_repository('source')
        tree.branch.repository.copy_content_into(source)
        dir = source.bzrdir
        target = dir.clone(self.get_url('target'), revision_id='2')
        raise TestSkipped('revision limiting not strict yet')

    def test_clone_bzrdir_branch_and_repo_fixed_user_id(self):
        # Bug #430868 is about an email containing '.sig'
        self.overrideEnv('BZR_EMAIL', 'murphy@host.sighup.org')
        tree = self.make_branch_and_tree('commit_tree')
        self.build_tree(['commit_tree/foo'])
        tree.add('foo')
        rev1 = tree.commit('revision 1')
        tree_repo = tree.branch.repository
        tree_repo.lock_write()
        tree_repo.start_write_group()
        tree_repo.sign_revision(rev1, gpg.LoopbackGPGStrategy(None))
        tree_repo.commit_write_group()
        tree_repo.unlock()
        target = self.make_branch('target')
        tree.branch.repository.copy_content_into(target.repository)
        tree.branch.copy_content_into(target)
        self.assertTrue(target.repository.has_revision(rev1))
        self.assertEqual(
            tree_repo.get_signature_text(rev1),
            target.repository.get_signature_text(rev1))

    def test_clone_bzrdir_branch_and_repo_into_shared_repo(self):
        # by default cloning into a shared repo uses the shared repo.
        tree = self.make_branch_and_tree('commit_tree')
        self.build_tree(['commit_tree/foo'])
        tree.add('foo')
        tree.commit('revision 1')
        source = self.make_branch('source')
        tree.branch.repository.copy_content_into(source.repository)
        tree.branch.copy_content_into(source)
        try:
            self.make_repository('target', shared=True)
        except errors.IncompatibleFormat:
            return
        dir = source.bzrdir
        target = dir.clone(self.get_url('target/child'))
        self.assertNotEqual(dir.transport.base, target.transport.base)
        self.assertRaises(errors.NoRepositoryPresent, target.open_repository)
        self.assertEqual(source.revision_history(),
                         target.open_branch().revision_history())

    def test_clone_bzrdir_branch_revision(self):
        # test for revision limiting, [smoke test, not corner case checks].
        # make a branch with some revisions,
        # and clone it with a revision limit.
        #
        tree = self.make_branch_and_tree('commit_tree')
        self.build_tree(['commit_tree/foo'])
        tree.add('foo')
        tree.commit('revision 1', rev_id='1')
        tree.commit('revision 2', rev_id='2', allow_pointless=True)
        source = self.make_branch('source')
        tree.branch.repository.copy_content_into(source.repository)
        tree.branch.copy_content_into(source)
        dir = source.bzrdir
        target = dir.clone(self.get_url('target'), revision_id='1')
        self.assertEqual('1', target.open_branch().last_revision())

    def test_clone_on_transport_preserves_repo_format(self):
        if self.bzrdir_format == bzrdir.format_registry.make_bzrdir('default'):
            format = 'knit'
        else:
            format = None
        source_branch = self.make_branch('source', format=format)
        # Ensure no format data is cached
        a_dir = bzrlib.branch.Branch.open_from_transport(
            self.get_transport('source')).bzrdir
        target_transport = self.get_transport('target')
        target_bzrdir = a_dir.clone_on_transport(target_transport)
        target_repo = target_bzrdir.open_repository()
        source_branch = bzrlib.branch.Branch.open(
            self.get_vfs_only_url('source'))
        if isinstance(target_repo, RemoteRepository):
            target_repo._ensure_real()
            target_repo = target_repo._real_repository
        self.assertEqual(target_repo._format, source_branch.repository._format)

    def test_clone_bzrdir_tree_revision(self):
        # test for revision limiting, [smoke test, not corner case checks].
        # make a tree with a revision with a last-revision
        # and clone it with a revision limit.
        # This smoke test just checks the revision-id is right. Tree specific
        # tests will check corner cases.
        tree = self.make_branch_and_tree('source')
        self.build_tree(['source/foo'])
        tree.add('foo')
        tree.commit('revision 1', rev_id='1')
        tree.commit('revision 2', rev_id='2', allow_pointless=True)
        dir = tree.bzrdir
        target = dir.clone(self.get_url('target'), revision_id='1')
        self.skipIfNoWorkingTree(target)
        self.assertEqual(['1'], target.open_workingtree().get_parent_ids())

    def test_clone_bzrdir_into_notrees_repo(self):
        """Cloning into a no-trees repo should not create a working tree"""
        tree = self.make_branch_and_tree('source')
        self.build_tree(['source/foo'])
        tree.add('foo')
        tree.commit('revision 1')

        try:
            repo = self.make_repository('repo', shared=True)
        except errors.IncompatibleFormat:
            raise TestNotApplicable('must support shared repositories')
        if repo.make_working_trees():
            repo.set_make_working_trees(False)
            self.assertFalse(repo.make_working_trees())

        dir = tree.bzrdir
        a_dir = dir.clone(self.get_url('repo/a'))
        a_dir.open_branch()
        self.assertRaises(errors.NoWorkingTree, a_dir.open_workingtree)

    def test_clone_respects_stacked(self):
        branch = self.make_branch('parent')
        child_transport = self.get_transport('child')
        child = branch.bzrdir.clone_on_transport(child_transport,
                                                 stacked_on=branch.base)
        self.assertEqual(child.open_branch().get_stacked_on_url(), branch.base)

    def test_get_branch_reference_on_reference(self):
        """get_branch_reference should return the right url."""
        referenced_branch = self.make_branch('referenced')
        dir = self.make_bzrdir('source')
        try:
            reference = bzrlib.branch.BranchReferenceFormat().initialize(dir,
                target_branch=referenced_branch)
        except errors.IncompatibleFormat:
            # this is ok too, not all formats have to support references.
            return
        self.assertEqual(referenced_branch.bzrdir.root_transport.abspath('') + '/',
            dir.get_branch_reference())

    def test_get_branch_reference_on_non_reference(self):
        """get_branch_reference should return None for non-reference branches."""
        branch = self.make_branch('referenced')
        self.assertEqual(None, branch.bzrdir.get_branch_reference())

    def test_get_branch_reference_no_branch(self):
        """get_branch_reference should not mask NotBranchErrors."""
        dir = self.make_bzrdir('source')
        if dir.has_branch():
            # this format does not support branchless bzrdirs.
            return
        self.assertRaises(errors.NotBranchError, dir.get_branch_reference)

    def test_sprout_bzrdir_empty(self):
        dir = self.make_bzrdir('source')
        target = dir.sprout(self.get_url('target'))
        self.assertNotEqual(dir.transport.base, target.transport.base)
        # creates a new repository branch and tree
        target.open_repository()
        target.open_branch()
        self.openWorkingTreeIfLocal(target)

    def test_sprout_bzrdir_empty_under_shared_repo(self):
        # sprouting an empty dir into a repo uses the repo
        dir = self.make_bzrdir('source')
        try:
            self.make_repository('target', shared=True)
        except errors.IncompatibleFormat:
            return
        target = dir.sprout(self.get_url('target/child'))
        self.assertRaises(errors.NoRepositoryPresent, target.open_repository)
        target.open_branch()
        try:
            target.open_workingtree()
        except errors.NoWorkingTree:
            # Some bzrdirs can never have working trees.
            self.assertFalse(target._format.supports_workingtrees)

    def test_sprout_bzrdir_empty_under_shared_repo_force_new(self):
        # the force_new_repo parameter should force use of a new repo in an empty
        # bzrdir's sprout logic
        dir = self.make_bzrdir('source')
        try:
            self.make_repository('target', shared=True)
        except errors.IncompatibleFormat:
            return
        target = dir.sprout(self.get_url('target/child'), force_new_repo=True)
        target.open_repository()
        target.open_branch()
        self.openWorkingTreeIfLocal(target)

    def test_sprout_bzrdir_with_repository_to_shared(self):
        tree = self.make_branch_and_tree('commit_tree')
        self.build_tree(['commit_tree/foo'])
        tree.add('foo')
        tree.commit('revision 1', rev_id='1')
        tree.bzrdir.open_branch().set_revision_history([])
        tree.set_parent_trees([])
        tree.commit('revision 2', rev_id='2')
        source = self.make_repository('source')
        tree.branch.repository.copy_content_into(source)
        dir = source.bzrdir
        try:
            shared_repo = self.make_repository('target', shared=True)
        except errors.IncompatibleFormat:
            return
        target = dir.sprout(self.get_url('target/child'))
        self.assertNotEqual(dir.transport.base, target.transport.base)
        self.assertTrue(shared_repo.has_revision('1'))

    def test_sprout_bzrdir_repository_branch_both_under_shared(self):
        try:
            shared_repo = self.make_repository('shared', shared=True)
        except errors.IncompatibleFormat:
            return
        tree = self.make_branch_and_tree('commit_tree')
        self.build_tree(['commit_tree/foo'])
        tree.add('foo')
        tree.commit('revision 1', rev_id='1')
        tree.bzrdir.open_branch().set_revision_history([])
        tree.set_parent_trees([])
        tree.commit('revision 2', rev_id='2')
        tree.branch.repository.copy_content_into(shared_repo)
        dir = self.make_bzrdir('shared/source')
        dir.create_branch()
        target = dir.sprout(self.get_url('shared/target'))
        self.assertNotEqual(dir.transport.base, target.transport.base)
        self.assertNotEqual(dir.transport.base, shared_repo.bzrdir.transport.base)
        self.assertTrue(shared_repo.has_revision('1'))

    def test_sprout_bzrdir_repository_branch_only_source_under_shared(self):
        try:
            shared_repo = self.make_repository('shared', shared=True)
        except errors.IncompatibleFormat:
            return
        tree = self.make_branch_and_tree('commit_tree')
        self.build_tree(['commit_tree/foo'])
        tree.add('foo')
        tree.commit('revision 1', rev_id='1')
        tree.bzrdir.open_branch().set_revision_history([])
        tree.set_parent_trees([])
        tree.commit('revision 2', rev_id='2')
        tree.branch.repository.copy_content_into(shared_repo)
        if shared_repo.make_working_trees():
            shared_repo.set_make_working_trees(False)
            self.assertFalse(shared_repo.make_working_trees())
        self.assertTrue(shared_repo.has_revision('1'))
        dir = self.make_bzrdir('shared/source')
        dir.create_branch()
        target = dir.sprout(self.get_url('target'))
        self.assertNotEqual(dir.transport.base, target.transport.base)
        self.assertNotEqual(dir.transport.base, shared_repo.bzrdir.transport.base)
        branch = target.open_branch()
        # The sprouted bzrdir has a branch, so only revisions referenced by
        # that branch are copied, rather than the whole repository.  It's an
        # empty branch, so none are copied.
        self.assertEqual([], branch.repository.all_revision_ids())
        if branch.bzrdir._format.supports_workingtrees:
            self.assertTrue(branch.repository.make_working_trees())
        self.assertFalse(branch.repository.is_shared())

    def test_sprout_bzrdir_repository_under_shared_force_new_repo(self):
        tree = self.make_branch_and_tree('commit_tree')
        self.build_tree(['commit_tree/foo'])
        tree.add('foo')
        tree.commit('revision 1', rev_id='1')
        tree.bzrdir.open_branch().set_revision_history([])
        tree.set_parent_trees([])
        tree.commit('revision 2', rev_id='2')
        source = self.make_repository('source')
        tree.branch.repository.copy_content_into(source)
        dir = source.bzrdir
        try:
            shared_repo = self.make_repository('target', shared=True)
        except errors.IncompatibleFormat:
            return
        target = dir.sprout(self.get_url('target/child'), force_new_repo=True)
        self.assertNotEqual(dir.transport.base, target.transport.base)
        self.assertFalse(shared_repo.has_revision('1'))

    def test_sprout_bzrdir_repository_revision(self):
        # test for revision limiting, [smoke test, not corner case checks].
        # make a repository with some revisions,
        # and sprout it with a revision limit.
        #
        tree = self.make_branch_and_tree('commit_tree')
        self.build_tree(['commit_tree/foo'])
        tree.add('foo')
        tree.commit('revision 1', rev_id='1')
        tree.bzrdir.open_branch().set_revision_history([])
        tree.set_parent_trees([])
        tree.commit('revision 2', rev_id='2')
        source = self.make_repository('source')
        tree.branch.repository.copy_content_into(source)
        dir = source.bzrdir
        target = self.sproutOrSkip(dir, self.get_url('target'), revision_id='2')
        raise TestSkipped('revision limiting not strict yet')

    def test_sprout_bzrdir_branch_and_repo_shared(self):
        # sprouting a branch with a repo into a shared repo uses the shared
        # repo
        tree = self.make_branch_and_tree('commit_tree')
        self.build_tree(['commit_tree/foo'])
        tree.add('foo')
        tree.commit('revision 1', rev_id='1')
        source = self.make_branch('source')
        tree.branch.repository.copy_content_into(source.repository)
        tree.bzrdir.open_branch().copy_content_into(source)
        dir = source.bzrdir
        try:
            shared_repo = self.make_repository('target', shared=True)
        except errors.IncompatibleFormat:
            return
        target = dir.sprout(self.get_url('target/child'))
        self.assertTrue(shared_repo.has_revision('1'))

    def test_sprout_bzrdir_branch_and_repo_shared_force_new_repo(self):
        # sprouting a branch with a repo into a shared repo uses the shared
        # repo
        tree = self.make_branch_and_tree('commit_tree')
        self.build_tree(['commit_tree/foo'])
        tree.add('foo')
        tree.commit('revision 1', rev_id='1')
        source = self.make_branch('source')
        tree.branch.repository.copy_content_into(source.repository)
        tree.bzrdir.open_branch().copy_content_into(source)
        dir = source.bzrdir
        try:
            shared_repo = self.make_repository('target', shared=True)
        except errors.IncompatibleFormat:
            return
        target = dir.sprout(self.get_url('target/child'), force_new_repo=True)
        self.assertNotEqual(dir.transport.base, target.transport.base)
        self.assertFalse(shared_repo.has_revision('1'))

    def test_sprout_bzrdir_branch_reference(self):
        # sprouting should create a repository if needed and a sprouted branch.
        referenced_branch = self.make_branch('referenced')
        dir = self.make_bzrdir('source')
        try:
            reference = bzrlib.branch.BranchReferenceFormat().initialize(dir,
                target_branch=referenced_branch)
        except errors.IncompatibleFormat:
            # this is ok too, not all formats have to support references.
            return
        self.assertRaises(errors.NoRepositoryPresent, dir.open_repository)
        target = dir.sprout(self.get_url('target'))
        self.assertNotEqual(dir.transport.base, target.transport.base)
        # we want target to have a branch that is in-place.
        self.assertEqual(target, target.open_branch().bzrdir)
        # and as we dont support repositories being detached yet, a repo in
        # place
        target.open_repository()

    def test_sprout_bzrdir_branch_reference_shared(self):
        # sprouting should create a repository if needed and a sprouted branch.
        referenced_tree = self.make_branch_and_tree('referenced')
        referenced_tree.commit('1', rev_id='1', allow_pointless=True)
        dir = self.make_bzrdir('source')
        try:
            reference = bzrlib.branch.BranchReferenceFormat().initialize(dir,
                target_branch=referenced_tree.branch)
        except errors.IncompatibleFormat:
            # this is ok too, not all formats have to support references.
            return
        self.assertRaises(errors.NoRepositoryPresent, dir.open_repository)
        try:
            shared_repo = self.make_repository('target', shared=True)
        except errors.IncompatibleFormat:
            return
        target = dir.sprout(self.get_url('target/child'))
        self.assertNotEqual(dir.transport.base, target.transport.base)
        # we want target to have a branch that is in-place.
        self.assertEqual(target, target.open_branch().bzrdir)
        # and we want no repository as the target is shared
        self.assertRaises(errors.NoRepositoryPresent,
                          target.open_repository)
        # and we want revision '1' in the shared repo
        self.assertTrue(shared_repo.has_revision('1'))

    def test_sprout_bzrdir_branch_reference_shared_force_new_repo(self):
        # sprouting should create a repository if needed and a sprouted branch.
        referenced_tree = self.make_branch_and_tree('referenced')
        referenced_tree.commit('1', rev_id='1', allow_pointless=True)
        dir = self.make_bzrdir('source')
        try:
            reference = bzrlib.branch.BranchReferenceFormat().initialize(dir,
                target_branch=referenced_tree.branch)
        except errors.IncompatibleFormat:
            # this is ok too, not all formats have to support references.
            return
        self.assertRaises(errors.NoRepositoryPresent, dir.open_repository)
        try:
            shared_repo = self.make_repository('target', shared=True)
        except errors.IncompatibleFormat:
            return
        target = dir.sprout(self.get_url('target/child'), force_new_repo=True)
        self.assertNotEqual(dir.transport.base, target.transport.base)
        # we want target to have a branch that is in-place.
        self.assertEqual(target, target.open_branch().bzrdir)
        # and we want revision '1' in the new repo
        self.assertTrue(target.open_repository().has_revision('1'))
        # but not the shared one
        self.assertFalse(shared_repo.has_revision('1'))

    def test_sprout_bzrdir_branch_revision(self):
        # test for revision limiting, [smoke test, not corner case checks].
        # make a repository with some revisions,
        # and sprout it with a revision limit.
        #
        tree = self.make_branch_and_tree('commit_tree')
        self.build_tree(['commit_tree/foo'])
        tree.add('foo')
        tree.commit('revision 1', rev_id='1')
        tree.commit('revision 2', rev_id='2', allow_pointless=True)
        source = self.make_branch('source')
        tree.branch.repository.copy_content_into(source.repository)
        tree.bzrdir.open_branch().copy_content_into(source)
        dir = source.bzrdir
        target = dir.sprout(self.get_url('target'), revision_id='1')
        self.assertEqual('1', target.open_branch().last_revision())

    def test_sprout_bzrdir_branch_with_tags(self):
        # when sprouting a branch all revisions named in the tags are copied
        # too.
        builder = self.make_branch_builder('source')
        source = fixtures.build_branch_with_non_ancestral_rev(builder)
        try:
            source.tags.set_tag('tag-a', 'rev-2')
        except errors.TagsNotSupported:
            raise TestNotApplicable('Branch format does not support tags.')
        # Now source has a tag not in its ancestry.  Sprout its controldir.
        dir = source.bzrdir
        target = dir.sprout(self.get_url('target'))
        # The tag is present, and so is its revision.
        new_branch = target.open_branch()
        self.assertEqual('rev-2', new_branch.tags.lookup_tag('tag-a'))
        new_branch.repository.get_revision('rev-2')

    def test_sprout_bzrdir_branch_with_absent_tag(self):
        # tags referencing absent revisions are copied (and those absent
        # revisions do not prevent the sprout.)
        builder = self.make_branch_builder('source')
        builder.build_commit(message="Rev 1", rev_id='rev-1')
        source = builder.get_branch()
        try:
            source.tags.set_tag('tag-a', 'missing-rev')
        except errors.TagsNotSupported:
            raise TestNotApplicable('Branch format does not support tags.')
        # Now source has a tag pointing to an absent revision.  Sprout its
        # controldir.
        dir = source.bzrdir
        target = dir.sprout(self.get_url('target'))
        # The tag is present in the target
        new_branch = target.open_branch()
        self.assertEqual('missing-rev', new_branch.tags.lookup_tag('tag-a'))

    def test_sprout_bzrdir_passing_source_branch_with_absent_tag(self):
        # tags referencing absent revisions are copied (and those absent
        # revisions do not prevent the sprout.)
        builder = self.make_branch_builder('source')
        builder.build_commit(message="Rev 1", rev_id='rev-1')
        source = builder.get_branch()
        try:
            source.tags.set_tag('tag-a', 'missing-rev')
        except errors.TagsNotSupported:
            raise TestNotApplicable('Branch format does not support tags.')
        # Now source has a tag pointing to an absent revision.  Sprout its
        # controldir.
        dir = source.bzrdir
        target = dir.sprout(self.get_url('target'), source_branch=source)
        # The tag is present in the target
        new_branch = target.open_branch()
        self.assertEqual('missing-rev', new_branch.tags.lookup_tag('tag-a'))

    def test_sprout_bzrdir_passing_rev_not_source_branch_copies_tags(self):
        # dir.sprout(..., revision_id='rev1') copies rev1, and all the tags of
        # the branch at that bzrdir, the ancestry of all of those, but no other
        # revs (not even the tip of the source branch).
        builder = self.make_branch_builder('source')
        builder.build_commit(message="Base", rev_id='base-rev')
        # Make three parallel lines of ancestry off this base.
        source = builder.get_branch()
        builder.build_commit(message="Rev A1", rev_id='rev-a1')
        builder.build_commit(message="Rev A2", rev_id='rev-a2')
        builder.build_commit(message="Rev A3", rev_id='rev-a3')
        source.set_last_revision_info(1, 'base-rev')
        builder.build_commit(message="Rev B1", rev_id='rev-b1')
        builder.build_commit(message="Rev B2", rev_id='rev-b2')
        builder.build_commit(message="Rev B3", rev_id='rev-b3')
        source.set_last_revision_info(1, 'base-rev')
        builder.build_commit(message="Rev C1", rev_id='rev-c1')
        builder.build_commit(message="Rev C2", rev_id='rev-c2')
        builder.build_commit(message="Rev C3", rev_id='rev-c3')
        # Set the branch tip to A2
        source.set_last_revision_info(3, 'rev-a2')
        try:
            # Create a tag for B2, and for an absent rev
            source.tags.set_tag('tag-non-ancestry', 'rev-b2')
            source.tags.set_tag('tag-absent', 'absent-rev')
        except errors.TagsNotSupported:
            raise TestNotApplicable('Branch format does not support tags.')
        # And ask sprout for C2
        dir = source.bzrdir
        target = dir.sprout(self.get_url('target'), revision_id='rev-c2')
        # The tags are present
        new_branch = target.open_branch()
        self.assertEqual(
            {'tag-absent': 'absent-rev', 'tag-non-ancestry': 'rev-b2'},
            new_branch.tags.get_tag_dict())
        # And the revs for A2, B2 and C2's ancestries are present, but no
        # others.
        self.assertEqual(
            ['base-rev', 'rev-b1', 'rev-b2', 'rev-c1', 'rev-c2'],
            sorted(new_branch.repository.all_revision_ids()))

    def test_sprout_bzrdir_tree_branch_reference(self):
        # sprouting should create a repository if needed and a sprouted branch.
        # the tree state should not be copied.
        referenced_branch = self.make_branch('referencced')
        dir = self.make_bzrdir('source')
        try:
            reference = bzrlib.branch.BranchReferenceFormat().initialize(dir,
                target_branch=referenced_branch)
        except errors.IncompatibleFormat:
            # this is ok too, not all formats have to support references.
            return
        self.assertRaises(errors.NoRepositoryPresent, dir.open_repository)
        tree = self.createWorkingTreeOrSkip(dir)
        self.build_tree(['source/subdir/'])
        tree.add('subdir')
        target = dir.sprout(self.get_url('target'))
        self.assertNotEqual(dir.transport.base, target.transport.base)
        # we want target to have a branch that is in-place.
        self.assertEqual(target, target.open_branch().bzrdir)
        # and as we dont support repositories being detached yet, a repo in
        # place
        target.open_repository()
        result_tree = target.open_workingtree()
        self.assertFalse(result_tree.has_filename('subdir'))

    def test_sprout_bzrdir_tree_branch_reference_revision(self):
        # sprouting should create a repository if needed and a sprouted branch.
        # the tree state should not be copied but the revision changed,
        # and the likewise the new branch should be truncated too
        referenced_branch = self.make_branch('referencced')
        dir = self.make_bzrdir('source')
        try:
            reference = bzrlib.branch.BranchReferenceFormat().initialize(dir,
                target_branch=referenced_branch)
        except errors.IncompatibleFormat:
            # this is ok too, not all formats have to support references.
            return
        self.assertRaises(errors.NoRepositoryPresent, dir.open_repository)
        tree = self.createWorkingTreeOrSkip(dir)
        self.build_tree(['source/foo'])
        tree.add('foo')
        tree.commit('revision 1', rev_id='1')
        tree.commit('revision 2', rev_id='2', allow_pointless=True)
        target = dir.sprout(self.get_url('target'), revision_id='1')
        self.skipIfNoWorkingTree(target)
        self.assertNotEqual(dir.transport.base, target.transport.base)
        # we want target to have a branch that is in-place.
        self.assertEqual(target, target.open_branch().bzrdir)
        # and as we dont support repositories being detached yet, a repo in
        # place
        target.open_repository()
        # we trust that the working tree sprouting works via the other tests.
        self.assertEqual(['1'], target.open_workingtree().get_parent_ids())
        self.assertEqual('1', target.open_branch().last_revision())

    def test_sprout_bzrdir_tree_revision(self):
        # test for revision limiting, [smoke test, not corner case checks].
        # make a tree with a revision with a last-revision
        # and sprout it with a revision limit.
        # This smoke test just checks the revision-id is right. Tree specific
        # tests will check corner cases.
        tree = self.make_branch_and_tree('source')
        self.build_tree(['source/foo'])
        tree.add('foo')
        tree.commit('revision 1', rev_id='1')
        tree.commit('revision 2', rev_id='2', allow_pointless=True)
        dir = tree.bzrdir
        target = self.sproutOrSkip(dir, self.get_url('target'), revision_id='1')
        self.assertEqual(['1'], target.open_workingtree().get_parent_ids())

    def test_sprout_takes_accelerator(self):
        tree = self.make_branch_and_tree('source')
        self.build_tree(['source/foo'])
        tree.add('foo')
        tree.commit('revision 1', rev_id='1')
        tree.commit('revision 2', rev_id='2', allow_pointless=True)
        dir = tree.bzrdir
        target = self.sproutOrSkip(dir, self.get_url('target'),
                                   accelerator_tree=tree)
        self.assertEqual(['2'], target.open_workingtree().get_parent_ids())

    def test_sprout_branch_no_tree(self):
        tree = self.make_branch_and_tree('source')
        self.build_tree(['source/foo'])
        tree.add('foo')
        tree.commit('revision 1', rev_id='1')
        tree.commit('revision 2', rev_id='2', allow_pointless=True)
        dir = tree.bzrdir
        try:
            target = dir.sprout(self.get_url('target'),
                create_tree_if_local=False)
        except errors.MustHaveWorkingTree:
            raise TestNotApplicable("control dir format requires working tree")
        self.failIfExists('target/foo')
        self.assertEqual(tree.branch.last_revision(),
                         target.open_branch().last_revision())

    def test_sprout_with_revision_id_uses_default_stack_on(self):
        # Make a branch with three commits to stack on.
        builder = self.make_branch_builder('stack-on')
        builder.start_series()
        builder.build_commit(message='Rev 1.', rev_id='rev-1')
        builder.build_commit(message='Rev 2.', rev_id='rev-2')
        builder.build_commit(message='Rev 3.', rev_id='rev-3')
        builder.finish_series()
        stack_on = builder.get_branch()
        # Make a bzrdir with a default stacking policy to stack on that branch.
        config = self.make_bzrdir('policy-dir').get_config()
        try:
            config.set_default_stack_on(self.get_url('stack-on'))
        except errors.BzrError:
            raise TestNotApplicable('Only relevant for stackable formats.')
        # Sprout the stacked-on branch into the bzrdir.
        sprouted = stack_on.bzrdir.sprout(
            self.get_url('policy-dir/sprouted'), revision_id='rev-3')
        # Not all revisions are copied into the sprouted repository.
        repo = sprouted.open_repository()
        self.addCleanup(repo.lock_read().unlock)
        self.assertEqual(None, repo.get_parent_map(['rev-1']).get('rev-1'))

    def test_format_initialize_find_open(self):
        # loopback test to check the current format initializes to itself.
        if not self.bzrdir_format.is_supported():
            # unsupported formats are not loopback testable
            # because the default open will not open them and
            # they may not be initializable.
            return
        # for remote formats, there must be no prior assumption about the
        # network name to use - it's possible that this may somehow have got
        # in through an unisolated test though - see
        # <https://bugs.launchpad.net/bzr/+bug/504102>
        self.assertEquals(getattr(self.bzrdir_format,
            '_network_name', None),
            None)
        # supported formats must be able to init and open
        t = self.get_transport()
        readonly_t = self.get_readonly_transport()
        made_control = self.bzrdir_format.initialize(t.base)
        self.failUnless(isinstance(made_control, controldir.ControlDir))
        self.assertEqual(self.bzrdir_format,
                         controldir.ControlDirFormat.find_format(readonly_t))
        direct_opened_dir = self.bzrdir_format.open(readonly_t)
        opened_dir = bzrdir.BzrDir.open(t.base)
        self.assertEqual(made_control._format,
                         opened_dir._format)
        self.assertEqual(direct_opened_dir._format,
                         opened_dir._format)
        self.failUnless(isinstance(opened_dir, controldir.ControlDir))

    def test_format_initialize_on_transport_ex(self):
        t = self.get_transport('dir')
        self.assertInitializeEx(t)

    def test_format_initialize_on_transport_ex_use_existing_dir_True(self):
        t = self.get_transport('dir')
        t.ensure_base()
        self.assertInitializeEx(t, use_existing_dir=True)

    def test_format_initialize_on_transport_ex_use_existing_dir_False(self):
        if not self.bzrdir_format.is_supported():
            # Not initializable - not a failure either.
            return
        t = self.get_transport('dir')
        t.ensure_base()
        self.assertRaises(errors.FileExists,
            self.bzrdir_format.initialize_on_transport_ex, t,
            use_existing_dir=False)

    def test_format_initialize_on_transport_ex_create_prefix_True(self):
        t = self.get_transport('missing/dir')
        self.assertInitializeEx(t, create_prefix=True)

    def test_format_initialize_on_transport_ex_create_prefix_False(self):
        if not self.bzrdir_format.is_supported():
            # Not initializable - not a failure either.
            return
        t = self.get_transport('missing/dir')
        self.assertRaises(errors.NoSuchFile, self.assertInitializeEx, t,
            create_prefix=False)

    def test_format_initialize_on_transport_ex_force_new_repo_True(self):
        t = self.get_transport('repo')
        repo_fmt = bzrdir.format_registry.make_bzrdir('1.9')
        repo_name = repo_fmt.repository_format.network_name()
        repo = repo_fmt.initialize_on_transport_ex(t,
            repo_format_name=repo_name, shared_repo=True)[0]
        made_repo, control = self.assertInitializeEx(t.clone('branch'),
            force_new_repo=True, repo_format_name=repo_name)
        if control is None:
            # uninitialisable format
            return
        self.assertNotEqual(repo.bzrdir.root_transport.base,
            made_repo.bzrdir.root_transport.base)

    def test_format_initialize_on_transport_ex_force_new_repo_False(self):
        t = self.get_transport('repo')
        repo_fmt = bzrdir.format_registry.make_bzrdir('1.9')
        repo_name = repo_fmt.repository_format.network_name()
        repo = repo_fmt.initialize_on_transport_ex(t,
            repo_format_name=repo_name, shared_repo=True)[0]
        made_repo, control = self.assertInitializeEx(t.clone('branch'),
            force_new_repo=False, repo_format_name=repo_name)
        if control is None:
            # uninitialisable format
            return
        if not control._format.fixed_components:
            self.assertEqual(repo.bzrdir.root_transport.base,
                made_repo.bzrdir.root_transport.base)

    def test_format_initialize_on_transport_ex_stacked_on(self):
        # trunk is a stackable format.  Note that its in the same server area
        # which is what launchpad does, but not sufficient to exercise the
        # general case.
        trunk = self.make_branch('trunk', format='1.9')
        t = self.get_transport('stacked')
        old_fmt = bzrdir.format_registry.make_bzrdir('pack-0.92')
        repo_name = old_fmt.repository_format.network_name()
        # Should end up with a 1.9 format (stackable)
        repo, control = self.assertInitializeEx(t, need_meta=True,
            repo_format_name=repo_name, stacked_on='../trunk', stack_on_pwd=t.base)
        if control is None:
            # uninitialisable format
            return
        self.assertLength(1, repo._fallback_repositories)

    def test_format_initialize_on_transport_ex_default_stack_on(self):
        # When initialize_on_transport_ex uses a stacked-on branch because of
        # a stacking policy on the target, the location of the fallback
        # repository is the same as the external location of the stacked-on
        # branch.
        balloon = self.make_bzrdir('balloon')
        if isinstance(balloon._format, bzrdir.BzrDirMetaFormat1):
            stack_on = self.make_branch('stack-on', format='1.9')
        else:
            stack_on = self.make_branch('stack-on')
        config = self.make_bzrdir('.').get_config()
        try:
            config.set_default_stack_on('stack-on')
        except errors.BzrError:
            raise TestNotApplicable('Only relevant for stackable formats.')
        # Initialize a bzrdir subject to the policy.
        t = self.get_transport('stacked')
        repo_fmt = bzrdir.format_registry.make_bzrdir('1.9')
        repo_name = repo_fmt.repository_format.network_name()
        repo, control = self.assertInitializeEx(
            t, need_meta=True, repo_format_name=repo_name, stacked_on=None)
        # self.addCleanup(repo.unlock)
        if control is None:
            # uninitialisable format
            return
        # There's one fallback repo, with a public location.
        self.assertLength(1, repo._fallback_repositories)
        fallback_repo = repo._fallback_repositories[0]
        self.assertEqual(
            stack_on.base, fallback_repo.bzrdir.root_transport.base)
        # The bzrdir creates a branch in stacking-capable format.
        new_branch = control.create_branch()
        self.assertTrue(new_branch._format.supports_stacking())

    def test_format_initialize_on_transport_ex_repo_fmt_name_None(self):
        t = self.get_transport('dir')
        repo, control = self.assertInitializeEx(t)
        self.assertEqual(None, repo)

    def test_format_initialize_on_transport_ex_repo_fmt_name_followed(self):
        t = self.get_transport('dir')
        # 1.6 is likely to never be default
        fmt = bzrdir.format_registry.make_bzrdir('1.6')
        repo_name = fmt.repository_format.network_name()
        repo, control = self.assertInitializeEx(t, repo_format_name=repo_name)
        if control is None:
            # uninitialisable format
            return
        if self.bzrdir_format.fixed_components:
            # must stay with the all-in-one-format.
            repo_name = self.bzrdir_format.network_name()
        self.assertEqual(repo_name, repo._format.network_name())

    def assertInitializeEx(self, t, need_meta=False, **kwargs):
        """Execute initialize_on_transport_ex and check it succeeded correctly.

        This involves checking that the disk objects were created, open with
        the same format returned, and had the expected disk format.

        :param t: The transport to initialize on.
        :param **kwargs: Additional arguments to pass to
            initialize_on_transport_ex.
        :return: the resulting repo, control dir tuple.
        """
        if not self.bzrdir_format.is_supported():
            # Not initializable - not a failure either.
            return None, None
        repo, control, require_stacking, repo_policy = \
            self.bzrdir_format.initialize_on_transport_ex(t, **kwargs)
        if repo is not None:
            # Repositories are open write-locked
            self.assertTrue(repo.is_write_locked())
            self.addCleanup(repo.unlock)
        self.assertIsInstance(control, controldir.ControlDir)
        opened = bzrdir.BzrDir.open(t.base)
        expected_format = self.bzrdir_format
        if isinstance(expected_format, bzrdir.RemoteBzrDirFormat):
            # Current RemoteBzrDirFormat's do not reliably get network_name
            # set, so we skip a number of tests for RemoteBzrDirFormat's.
            self.assertIsInstance(control, RemoteBzrDir)
        else:
            if need_meta and expected_format.fixed_components:
                # Pre-metadir formats change when we are making something that
                # needs a metaformat, because clone is used for push.
                expected_format = bzrdir.BzrDirMetaFormat1()
            self.assertEqual(control._format.network_name(),
                expected_format.network_name())
            self.assertEqual(control._format.network_name(),
                opened._format.network_name())
        self.assertEqual(control.__class__, opened.__class__)
        return repo, control

    def test_format_network_name(self):
        # All control formats must have a network name.
        dir = self.make_bzrdir('.')
        format = dir._format
        # We want to test that the network_name matches the actual format on
        # disk. For local control dirsthat means that using network_name as a
        # key in the registry gives back the same format. For remote obects
        # we check that the network_name of the RemoteBzrDirFormat we have
        # locally matches the actual format present on disk.
        if isinstance(format, bzrdir.RemoteBzrDirFormat):
            dir._ensure_real()
            real_dir = dir._real_bzrdir
            network_name = format.network_name()
            self.assertEqual(real_dir._format.network_name(), network_name)
        else:
            registry = controldir.network_format_registry
            network_name = format.network_name()
            looked_up_format = registry.get(network_name)
            self.assertTrue(
                issubclass(format.__class__, looked_up_format.__class__))
        # The network name must be a byte string.
        self.assertIsInstance(network_name, str)

    def test_open_not_bzrdir(self):
        # test the formats specific behaviour for no-content or similar dirs.
        self.assertRaises(errors.NotBranchError,
                          self.bzrdir_format.open,
                          transport.get_transport(self.get_readonly_url()))

    def test_create_branch(self):
        # a bzrdir can construct a branch and repository for itself.
        if not self.bzrdir_format.is_supported():
            # unsupported formats are not loopback testable
            # because the default open will not open them and
            # they may not be initializable.
            return
        t = self.get_transport()
        made_control = self.bzrdir_format.initialize(t.base)
        made_repo = made_control.create_repository()
        made_branch = made_control.create_branch()
        self.failUnless(isinstance(made_branch, bzrlib.branch.Branch))
        self.assertEqual(made_control, made_branch.bzrdir)

    def test_open_branch(self):
        if not self.bzrdir_format.is_supported():
            # unsupported formats are not loopback testable
            # because the default open will not open them and
            # they may not be initializable.
            return
        t = self.get_transport()
        made_control = self.bzrdir_format.initialize(t.base)
        made_repo = made_control.create_repository()
        made_branch = made_control.create_branch()
        opened_branch = made_control.open_branch()
        self.assertEqual(made_control, opened_branch.bzrdir)
        self.failUnless(isinstance(opened_branch, made_branch.__class__))
        self.failUnless(isinstance(opened_branch._format, made_branch._format.__class__))

    def test_list_branches(self):
        if not self.bzrdir_format.is_supported():
            # unsupported formats are not loopback testable
            # because the default open will not open them and
            # they may not be initializable.
            return
        t = self.get_transport()
        made_control = self.bzrdir_format.initialize(t.base)
        made_repo = made_control.create_repository()
        made_branch = made_control.create_branch()
        branches = made_control.list_branches()
        self.assertEquals(1, len(branches))
        self.assertEquals(made_branch.base, branches[0].base)
        try:
            made_control.destroy_branch()
        except errors.UnsupportedOperation:
            pass # Not all bzrdirs support destroying directories
        else:
            self.assertEquals([], made_control.list_branches())

    def test_create_repository(self):
        # a bzrdir can construct a repository for itself.
        if not self.bzrdir_format.is_supported():
            # unsupported formats are not loopback testable
            # because the default open will not open them and
            # they may not be initializable.
            return
        t = self.get_transport()
        made_control = self.bzrdir_format.initialize(t.base)
        made_repo = made_control.create_repository()
        # Check that we have a repository object.
        made_repo.has_revision('foo')
        self.assertEqual(made_control, made_repo.bzrdir)

    def test_create_repository_shared(self):
        # a bzrdir can create a shared repository or
        # fail appropriately
        if not self.bzrdir_format.is_supported():
            # unsupported formats are not loopback testable
            # because the default open will not open them and
            # they may not be initializable.
            return
        t = self.get_transport()
        made_control = self.bzrdir_format.initialize(t.base)
        try:
            made_repo = made_control.create_repository(shared=True)
        except errors.IncompatibleFormat:
            # Old bzrdir formats don't support shared repositories
            # and should raise IncompatibleFormat
            return
        self.assertTrue(made_repo.is_shared())

    def test_create_repository_nonshared(self):
        # a bzrdir can create a non-shared repository
        if not self.bzrdir_format.is_supported():
            # unsupported formats are not loopback testable
            # because the default open will not open them and
            # they may not be initializable.
            return
        t = self.get_transport()
        made_control = self.bzrdir_format.initialize(t.base)
        made_repo = made_control.create_repository(shared=False)
        self.assertFalse(made_repo.is_shared())

    def test_open_repository(self):
        if not self.bzrdir_format.is_supported():
            # unsupported formats are not loopback testable
            # because the default open will not open them and
            # they may not be initializable.
            return
        t = self.get_transport()
        made_control = self.bzrdir_format.initialize(t.base)
        made_repo = made_control.create_repository()
        opened_repo = made_control.open_repository()
        self.assertEqual(made_control, opened_repo.bzrdir)
        self.failUnless(isinstance(opened_repo, made_repo.__class__))
        self.failUnless(isinstance(opened_repo._format, made_repo._format.__class__))

    def test_create_workingtree(self):
        # a bzrdir can construct a working tree for itself.
        if not self.bzrdir_format.is_supported():
            # unsupported formats are not loopback testable
            # because the default open will not open them and
            # they may not be initializable.
            return
        t = self.get_transport()
        made_control = self.bzrdir_format.initialize(t.base)
        made_repo = made_control.create_repository()
        made_branch = made_control.create_branch()
        made_tree = self.createWorkingTreeOrSkip(made_control)
        self.failUnless(isinstance(made_tree, workingtree.WorkingTree))
        self.assertEqual(made_control, made_tree.bzrdir)

    def test_create_workingtree_revision(self):
        # a bzrdir can construct a working tree for itself @ a specific revision.
        t = self.get_transport()
        source = self.make_branch_and_tree('source')
        source.commit('a', rev_id='a', allow_pointless=True)
        source.commit('b', rev_id='b', allow_pointless=True)
        t.mkdir('new')
        t_new = t.clone('new')
        made_control = self.bzrdir_format.initialize_on_transport(t_new)
        source.branch.repository.clone(made_control)
        source.branch.clone(made_control)
        try:
            made_tree = made_control.create_workingtree(revision_id='a')
        except (errors.NotLocalUrl, errors.UnsupportedOperation):
            raise TestSkipped("Can't make working tree on transport %r" % t)
        self.assertEqual(['a'], made_tree.get_parent_ids())

    def test_open_workingtree(self):
        if not self.bzrdir_format.is_supported():
            # unsupported formats are not loopback testable
            # because the default open will not open them and
            # they may not be initializable.
            return
        # this has to be tested with local access as we still support creating
        # format 6 bzrdirs
        t = self.get_transport()
        try:
            made_control = self.bzrdir_format.initialize(t.base)
            made_repo = made_control.create_repository()
            made_branch = made_control.create_branch()
            made_tree = made_control.create_workingtree()
        except (errors.NotLocalUrl, errors.UnsupportedOperation):
            raise TestSkipped("Can't initialize %r on transport %r"
                              % (self.bzrdir_format, t))
        opened_tree = made_control.open_workingtree()
        self.assertEqual(made_control, opened_tree.bzrdir)
        self.failUnless(isinstance(opened_tree, made_tree.__class__))
        self.failUnless(isinstance(opened_tree._format, made_tree._format.__class__))

    def test_get_branch_transport(self):
        dir = self.make_bzrdir('.')
        # without a format, get_branch_transport gives use a transport
        # which -may- point to an existing dir.
        self.assertTrue(isinstance(dir.get_branch_transport(None),
                                   transport.Transport))
        # with a given format, either the bzr dir supports identifiable
        # branches, or it supports anonymous branch formats, but not both.
        anonymous_format = AnonymousTestBranchFormat()
        identifiable_format = IdentifiableTestBranchFormat()
        try:
            found_transport = dir.get_branch_transport(anonymous_format)
            self.assertRaises(errors.IncompatibleFormat,
                              dir.get_branch_transport,
                              identifiable_format)
        except errors.IncompatibleFormat:
            found_transport = dir.get_branch_transport(identifiable_format)
        self.assertTrue(isinstance(found_transport, transport.Transport))
        # and the dir which has been initialized for us must exist.
        found_transport.list_dir('.')

    def test_get_repository_transport(self):
        dir = self.make_bzrdir('.')
        # without a format, get_repository_transport gives use a transport
        # which -may- point to an existing dir.
        self.assertTrue(isinstance(dir.get_repository_transport(None),
                                   transport.Transport))
        # with a given format, either the bzr dir supports identifiable
        # repositories, or it supports anonymous repository formats, but not both.
        anonymous_format = AnonymousTestRepositoryFormat()
        identifiable_format = IdentifiableTestRepositoryFormat()
        try:
            found_transport = dir.get_repository_transport(anonymous_format)
            self.assertRaises(errors.IncompatibleFormat,
                              dir.get_repository_transport,
                              identifiable_format)
        except errors.IncompatibleFormat:
            found_transport = dir.get_repository_transport(identifiable_format)
        self.assertTrue(isinstance(found_transport, transport.Transport))
        # and the dir which has been initialized for us must exist.
        found_transport.list_dir('.')

    def test_get_workingtree_transport(self):
        dir = self.make_bzrdir('.')
        # without a format, get_workingtree_transport gives use a transport
        # which -may- point to an existing dir.
        self.assertTrue(isinstance(dir.get_workingtree_transport(None),
                                   transport.Transport))
        # with a given format, either the bzr dir supports identifiable
        # trees, or it supports anonymous tree formats, but not both.
        anonymous_format = AnonymousTestWorkingTreeFormat()
        identifiable_format = IdentifiableTestWorkingTreeFormat()
        try:
            found_transport = dir.get_workingtree_transport(anonymous_format)
            self.assertRaises(errors.IncompatibleFormat,
                              dir.get_workingtree_transport,
                              identifiable_format)
        except errors.IncompatibleFormat:
            found_transport = dir.get_workingtree_transport(identifiable_format)
        self.assertTrue(isinstance(found_transport, transport.Transport))
        # and the dir which has been initialized for us must exist.
        found_transport.list_dir('.')

    def test_root_transport(self):
        dir = self.make_bzrdir('.')
        self.assertEqual(dir.root_transport.base,
                         self.get_transport().base)

    def test_find_repository_no_repo_under_standalone_branch(self):
        # finding a repo stops at standalone branches even if there is a
        # higher repository available.
        try:
            repo = self.make_repository('.', shared=True)
        except errors.IncompatibleFormat:
            # need a shared repository to test this.
            return
        url = self.get_url('intermediate')
        t = self.get_transport()
        t.mkdir('intermediate')
        t.mkdir('intermediate/child')
        made_control = self.bzrdir_format.initialize(url)
        made_control.create_repository()
        innermost_control = self.bzrdir_format.initialize(
            self.get_url('intermediate/child'))
        try:
            child_repo = innermost_control.open_repository()
            # if there is a repository, then the format cannot ever hit this
            # code path.
            return
        except errors.NoRepositoryPresent:
            pass
        self.assertRaises(errors.NoRepositoryPresent,
                          innermost_control.find_repository)

    def test_find_repository_containing_shared_repository(self):
        # find repo inside a shared repo with an empty control dir
        # returns the shared repo.
        try:
            repo = self.make_repository('.', shared=True)
        except errors.IncompatibleFormat:
            # need a shared repository to test this.
            return
        url = self.get_url('childbzrdir')
        self.get_transport().mkdir('childbzrdir')
        made_control = self.bzrdir_format.initialize(url)
        try:
            child_repo = made_control.open_repository()
            # if there is a repository, then the format cannot ever hit this
            # code path.
            return
        except errors.NoRepositoryPresent:
            pass
        found_repo = made_control.find_repository()
        self.assertEqual(repo.bzrdir.root_transport.base,
                         found_repo.bzrdir.root_transport.base)

    def test_find_repository_standalone_with_containing_shared_repository(self):
        # find repo inside a standalone repo inside a shared repo finds the standalone repo
        try:
            containing_repo = self.make_repository('.', shared=True)
        except errors.IncompatibleFormat:
            # need a shared repository to test this.
            return
        child_repo = self.make_repository('childrepo')
        opened_control = bzrdir.BzrDir.open(self.get_url('childrepo'))
        found_repo = opened_control.find_repository()
        self.assertEqual(child_repo.bzrdir.root_transport.base,
                         found_repo.bzrdir.root_transport.base)

    def test_find_repository_shared_within_shared_repository(self):
        # find repo at a shared repo inside a shared repo finds the inner repo
        try:
            containing_repo = self.make_repository('.', shared=True)
        except errors.IncompatibleFormat:
            # need a shared repository to test this.
            return
        url = self.get_url('childrepo')
        self.get_transport().mkdir('childrepo')
        child_control = self.bzrdir_format.initialize(url)
        child_repo = child_control.create_repository(shared=True)
        opened_control = bzrdir.BzrDir.open(self.get_url('childrepo'))
        found_repo = opened_control.find_repository()
        self.assertEqual(child_repo.bzrdir.root_transport.base,
                         found_repo.bzrdir.root_transport.base)
        self.assertNotEqual(child_repo.bzrdir.root_transport.base,
                            containing_repo.bzrdir.root_transport.base)

    def test_find_repository_with_nested_dirs_works(self):
        # find repo inside a bzrdir inside a bzrdir inside a shared repo
        # finds the outer shared repo.
        try:
            repo = self.make_repository('.', shared=True)
        except errors.IncompatibleFormat:
            # need a shared repository to test this.
            return
        url = self.get_url('intermediate')
        t = self.get_transport()
        t.mkdir('intermediate')
        t.mkdir('intermediate/child')
        made_control = self.bzrdir_format.initialize(url)
        try:
            child_repo = made_control.open_repository()
            # if there is a repository, then the format cannot ever hit this
            # code path.
            return
        except errors.NoRepositoryPresent:
            pass
        innermost_control = self.bzrdir_format.initialize(
            self.get_url('intermediate/child'))
        try:
            child_repo = innermost_control.open_repository()
            # if there is a repository, then the format cannot ever hit this
            # code path.
            return
        except errors.NoRepositoryPresent:
            pass
        found_repo = innermost_control.find_repository()
        self.assertEqual(repo.bzrdir.root_transport.base,
                         found_repo.bzrdir.root_transport.base)

    def test_can_and_needs_format_conversion(self):
        # check that we can ask an instance if its upgradable
        dir = self.make_bzrdir('.')
        if dir.can_convert_format():
            # if its default updatable there must be an updater
            # (we force the latest known format as downgrades may not be
            # available
            self.assertTrue(isinstance(dir._format.get_converter(
                format=dir._format), controldir.Converter))
        dir.needs_format_conversion(
            controldir.ControlDirFormat.get_default_format())

    def test_backup_copies_existing(self):
        tree = self.make_branch_and_tree('test')
        self.build_tree(['test/a'])
        tree.add(['a'], ['a-id'])
        tree.commit('some data to be copied.')
        old_url, new_url = tree.bzrdir.backup_bzrdir()
        old_path = urlutils.local_path_from_url(old_url)
        new_path = urlutils.local_path_from_url(new_url)
        self.failUnlessExists(old_path)
        self.failUnlessExists(new_path)
        for (((dir_relpath1, _), entries1),
             ((dir_relpath2, _), entries2)) in izip(
                osutils.walkdirs(old_path),
                osutils.walkdirs(new_path)):
            self.assertEquals(dir_relpath1, dir_relpath2)
            for f1, f2 in zip(entries1, entries2):
                self.assertEquals(f1[0], f2[0])
                self.assertEquals(f1[2], f2[2])
                if f1[2] == "file":
                    osutils.compare_files(open(f1[4]), open(f2[4]))

    def test_upgrade_new_instance(self):
        """Does an available updater work?"""
        dir = self.make_bzrdir('.')
        # for now, upgrade is not ready for partial bzrdirs.
        dir.create_repository()
        dir.create_branch()
        self.createWorkingTreeOrSkip(dir)
        if dir.can_convert_format():
            # if its default updatable there must be an updater
            # (we force the latest known format as downgrades may not be
            # available
            pb = ui.ui_factory.nested_progress_bar()
            try:
                dir._format.get_converter(format=dir._format).convert(dir, pb)
            finally:
                pb.finished()
            # and it should pass 'check' now.
            check.check_dwim(self.get_url('.'), False, True, True)

    def test_format_description(self):
        dir = self.make_bzrdir('.')
        text = dir._format.get_format_description()
        self.failUnless(len(text))


class TestBreakLock(TestCaseWithControlDir):

    def test_break_lock_empty(self):
        # break lock on an empty bzrdir should work silently.
        dir = self.make_bzrdir('.')
        try:
            dir.break_lock()
        except NotImplementedError:
            pass

    def test_break_lock_repository(self):
        # break lock with just a repo should unlock the repo.
        repo = self.make_repository('.')
        repo.lock_write()
        lock_repo = repo.bzrdir.open_repository()
        if not lock_repo.get_physical_lock_status():
            # This bzrdir's default repository does not physically lock things
            # and thus this interaction cannot be tested at the interface
            # level.
            repo.unlock()
            return
        # only one yes needed here: it should only be unlocking
        # the repo
        bzrlib.ui.ui_factory = CannedInputUIFactory([True])
        try:
            repo.bzrdir.break_lock()
        except NotImplementedError:
            # this bzrdir does not implement break_lock - so we cant test it.
            repo.unlock()
            return
        lock_repo.lock_write()
        lock_repo.unlock()
        self.assertRaises(errors.LockBroken, repo.unlock)

    def test_break_lock_branch(self):
        # break lock with just a repo should unlock the branch.
        # and not directly try the repository.
        # we test this by making a branch reference to a branch
        # and repository in another bzrdir
        # for pre-metadir formats this will fail, thats ok.
        master = self.make_branch('branch')
        thisdir = self.make_bzrdir('this')
        try:
            bzrlib.branch.BranchReferenceFormat().initialize(
                thisdir, target_branch=master)
        except errors.IncompatibleFormat:
            return
        unused_repo = thisdir.create_repository()
        master.lock_write()
        unused_repo.lock_write()
        try:
            # two yes's : branch and repository. If the repo in this
            # dir is inappropriately accessed, 3 will be needed, and
            # we'll see that because the stream will be fully consumed
            bzrlib.ui.ui_factory = CannedInputUIFactory([True, True, True])
            # determine if the repository will have been locked;
            this_repo_locked = \
                thisdir.open_repository().get_physical_lock_status()
            master.bzrdir.break_lock()
            if this_repo_locked:
                # only two ys should have been read
                self.assertEqual([True],
                    bzrlib.ui.ui_factory.responses)
            else:
                # only one y should have been read
                self.assertEqual([True, True],
                    bzrlib.ui.ui_factory.responses)
            # we should be able to lock a newly opened branch now
            branch = master.bzrdir.open_branch()
            branch.lock_write()
            branch.unlock()
            if this_repo_locked:
                # we should not be able to lock the repository in thisdir as
                # its still held by the explicit lock we took, and the break
                # lock should not have touched it.
                repo = thisdir.open_repository()
                self.assertRaises(errors.LockContention, repo.lock_write)
        finally:
            unused_repo.unlock()
        self.assertRaises(errors.LockBroken, master.unlock)

    def test_break_lock_tree(self):
        # break lock with a tree should unlock the tree but not try the
        # branch explicitly. However this is very hard to test for as we
        # dont have a tree reference class, nor is one needed;
        # the worst case if this code unlocks twice is an extra question
        # being asked.
        tree = self.make_branch_and_tree('.')
        tree.lock_write()
        # three yes's : tree, branch and repository.
        bzrlib.ui.ui_factory = CannedInputUIFactory([True, True, True])
        try:
            tree.bzrdir.break_lock()
        except (NotImplementedError, errors.LockActive):
            # bzrdir does not support break_lock
            # or one of the locked objects (currently only tree does this)
            # raised a LockActive because we do still have a live locked
            # object.
            tree.unlock()
            return
        self.assertEqual([True],
                bzrlib.ui.ui_factory.responses)
        lock_tree = tree.bzrdir.open_workingtree()
        lock_tree.lock_write()
        lock_tree.unlock()
        self.assertRaises(errors.LockBroken, tree.unlock)


class TestTransportConfig(TestCaseWithControlDir):

    def test_get_config(self):
        my_dir = self.make_bzrdir('.')
        config = my_dir.get_config()
        try:
            config.set_default_stack_on('http://example.com')
        except errors.BzrError, e:
            if 'Cannot set config' in str(e):
                self.assertFalse(
                    isinstance(my_dir, (bzrdir.BzrDirMeta1, RemoteBzrDir)),
                    "%r should support configs" % my_dir)
                raise TestNotApplicable(
                    'This BzrDir format does not support configs.')
            else:
                raise
        self.assertEqual('http://example.com', config.get_default_stack_on())
        my_dir2 = bzrdir.BzrDir.open(self.get_url('.'))
        config2 = my_dir2.get_config()
        self.assertEqual('http://example.com', config2.get_default_stack_on())


class ChrootedControlDirTests(ChrootedTestCase):

    def test_find_repository_no_repository(self):
        # loopback test to check the current format fails to find a
        # share repository correctly.
        if not self.bzrdir_format.is_supported():
            # unsupported formats are not loopback testable
            # because the default open will not open them and
            # they may not be initializable.
            return
        # supported formats must be able to init and open
        # - do the vfs initialisation over the basic vfs transport
        # XXX: TODO this should become a 'bzrdirlocation' api call.
        url = self.get_vfs_only_url('subdir')
        transport.get_transport(self.get_vfs_only_url()).mkdir('subdir')
        made_control = self.bzrdir_format.initialize(self.get_url('subdir'))
        try:
            repo = made_control.open_repository()
            # if there is a repository, then the format cannot ever hit this
            # code path.
            return
        except errors.NoRepositoryPresent:
            pass
        made_control = bzrdir.BzrDir.open(self.get_readonly_url('subdir'))
        self.assertRaises(errors.NoRepositoryPresent,
                          made_control.find_repository)


class TestControlDirControlComponent(TestCaseWithControlDir):
    """ControlDir implementations adequately implement ControlComponent."""

    def test_urls(self):
        bd = self.make_bzrdir('bd')
        self.assertIsInstance(bd.user_url, str)
        self.assertEqual(bd.user_url, bd.user_transport.base)
        # for all current bzrdir implementations the user dir must be 
        # above the control dir but we might need to relax that?
        self.assertEqual(bd.control_url.find(bd.user_url), 0)
        self.assertEqual(bd.control_url, bd.control_transport.base)