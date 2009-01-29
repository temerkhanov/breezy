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

"""An adapter between a Git control dir and a Bazaar BzrDir"""

import os

import bzrlib
from bzrlib.lazy_import import lazy_import
from bzrlib import (
    bzrdir,
    lockable_files,
    urlutils,
    )

lazy_import(globals(), """
from bzrlib.lockable_files import TransportLock
from bzrlib.plugins.git import (
    errors,
    branch,
    repository,
    workingtree,
    )
""")

from bzrlib.plugins.git import LocalGitBzrDirFormat



class GitLock(object):
    """A lock that thunks through to Git."""

    def lock_write(self, token=None):
        pass

    def lock_read(self):
        pass

    def unlock(self):
        pass

    def peek(self):
        pass

    def validate_token(self, token):
        pass


class GitLockableFiles(lockable_files.LockableFiles):
    """Git specific lockable files abstraction."""

    def __init__(self, transport, lock):
        self._lock = lock
        self._transaction = None
        self._lock_mode = None
        self._lock_count = 0
        self._transport = transport


class GitDir(bzrdir.BzrDir):
    """An adapter to the '.git' dir used by git."""

    def is_supported(self):
        return True

    def cloning_metadir(self, stacked=False):
        return bzrlib.bzrdir.format_registry.make_bzrdir("1.9-rich-root")


class LocalGitDir(GitDir):
    """An adapter to the '.git' dir used by git."""

    _gitrepository_class = repository.LocalGitRepository

    def __init__(self, transport, lockfiles, gitrepo, format):
        self._format = format
        self.root_transport = transport
        self._git = gitrepo
        if gitrepo.bare:
            self.transport = transport
        else:
            self.transport = transport.clone('.git')
        self._lockfiles = lockfiles

    def get_branch_transport(self, branch_format):
        if branch_format is None:
            return self.transport
        if isinstance(branch_format, LocalGitBzrDirFormat):
            return self.transport
        raise errors.bzr_errors.IncompatibleFormat(branch_format, self._format)

    get_repository_transport = get_branch_transport
    get_workingtree_transport = get_branch_transport

    def open_branch(self, ignored=None):
        """'create' a branch for this dir."""
        repo = self.open_repository()
        return branch.LocalGitBranch(self, repo, "HEAD", repo._git.head(), self._lockfiles)

    def open_repository(self, shared=False):
        """'open' a repository for this dir."""
        return self._gitrepository_class(self, self._lockfiles)

    def open_workingtree(self, recommend_upgrade=True):
        if (not self._git.bare and 
            os.path.exists(os.path.join(self._git.controldir(), "index"))):
            return workingtree.GitWorkingTree(self, self.open_repository(), 
                                                  self.open_branch())
        loc = urlutils.unescape_for_display(self.root_transport.base, 'ascii')
        raise errors.bzr_errors.NoWorkingTree(loc)

    def create_repository(self, shared=False):
        return self.open_repository()
