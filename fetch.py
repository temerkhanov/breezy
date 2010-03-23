# Copyright (C) 2008 Jelmer Vernooij <jelmer@samba.org>
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

from dulwich.objects import (
    Commit,
    Tag,
    S_ISGITLINK,
    )
from dulwich.object_store import (
    tree_lookup_path,
    )
import re
import stat

from bzrlib import (
    debug,
    lru_cache,
    osutils,
    trace,
    ui,
    urlutils,
    )
from bzrlib.errors import (
    BzrError,
    NoSuchId,
    )
from bzrlib.inventory import (
    Inventory,
    InventoryDirectory,
    InventoryFile,
    InventoryLink,
    TreeReference,
    )
from bzrlib.repository import (
    InterRepository,
    )
from bzrlib.revision import (
    NULL_REVISION,
    )
from bzrlib.tsort import (
    topo_sort,
    )
from bzrlib.versionedfile import (
    FulltextContentFactory,
    )

from bzrlib.plugins.git.mapping import (
    DEFAULT_FILE_MODE,
    inventory_to_tree_and_blobs,
    mode_is_executable,
    squash_revision,
    warn_unusual_mode,
    )
from bzrlib.plugins.git.object_store import (
    BazaarObjectStore,
    )
from bzrlib.plugins.git.remote import (
    RemoteGitRepository,
    )
from bzrlib.plugins.git.repository import (
    GitRepository,
    GitRepositoryFormat,
    LocalGitRepository,
    )


MAX_INV_CACHE_SIZE = 50 * 1024 * 1024


def import_git_blob(texts, mapping, path, hexsha, base_inv, base_ie, parent_id,
    revision_id, parent_invs, shagitmap, lookup_object, executable, symlink):
    """Import a git blob object into a bzr repository.

    :param texts: VersionedFiles to add to
    :param path: Path in the tree
    :param blob: A git blob
    :return: Inventory delta for this file
    """
    file_id = mapping.generate_file_id(path)
    if symlink:
        cls = InventoryLink
    else:
        cls = InventoryFile
    # We just have to hope this is indeed utf-8:
    ie = cls(file_id, urlutils.basename(path).decode("utf-8"), parent_id)
    ie.executable = executable
    # See if this has changed at all
    if base_ie is None:
        base_sha = None
    else:
        try:
            base_sha = shagitmap.lookup_blob(file_id, base_ie.revision)
        except KeyError:
            base_sha = None
        else:
            if (base_sha == hexsha and base_ie.executable == ie.executable
                and base_ie.kind == ie.kind):
                # If nothing has changed since the base revision, we're done
                return [], []
    if base_sha == hexsha and base_ie.kind == ie.kind:
        ie.text_size = base_ie.text_size
        ie.text_sha1 = base_ie.text_sha1
        ie.symlink_target = base_ie.symlink_target
        if ie.executable == base_ie.executable:
            ie.revision = base_ie.revision
        else:
            blob = lookup_object(hexsha)
    else:
        blob = lookup_object(hexsha)
        if ie.kind == "symlink":
            ie.revision = None
            ie.symlink_target = blob.data
            ie.text_size = None
            ie.text_sha1 = None
        else:
            ie.text_size = len(blob.data)
            ie.text_sha1 = osutils.sha_string(blob.data)
    # Check what revision we should store
    parent_keys = []
    for pinv in parent_invs:
        if pinv.revision_id == base_inv.revision_id:
            pie = base_ie
            if pie is None:
                continue
        else:
            try:
                pie = pinv[file_id]
            except NoSuchId:
                continue
        if pie.text_sha1 == ie.text_sha1 and pie.executable == ie.executable and pie.symlink_target == ie.symlink_target:
            # found a revision in one of the parents to use
            ie.revision = pie.revision
            break
        parent_keys.append((file_id, pie.revision))
    if ie.revision is None:
        # Need to store a new revision
        ie.revision = revision_id
        assert file_id is not None
        assert ie.revision is not None
        if ie.kind == 'symlink':
            data = ''
        else: 
            data = blob.data
        texts.insert_record_stream([FulltextContentFactory((file_id, ie.revision), tuple(parent_keys), ie.text_sha1, data)])
        shamap = [(hexsha, "blob", (ie.file_id, ie.revision))]
    else:
        shamap = []
    invdelta = []
    if base_ie is not None:
        old_path = base_inv.id2path(file_id)
        if base_ie.kind == "directory":
            invdelta.extend(remove_disappeared_children(old_path, base_ie.children, []))
    else:
        old_path = None
    invdelta.append((old_path, path, file_id, ie))
    return (invdelta, shamap)


class SubmodulesRequireSubtrees(BzrError):
    _fmt = """The repository you are fetching from contains submodules. To continue, upgrade your Bazaar repository to a format that supports nested trees, such as 'development-subtree'."""
    internal = False


def import_git_submodule(texts, mapping, path, hexsha, base_inv, base_ie,
    parent_id, revision_id, parent_invs, shagitmap, lookup_object):
    file_id = mapping.generate_file_id(path)
    ie = TreeReference(file_id, urlutils.basename(path.decode("utf-8")),
        parent_id)
    ie.revision = revision_id
    if base_ie is None:
        oldpath = None
    else:
        oldpath = path
        if (base_ie.kind == ie.kind and
            base_ie.reference_revision == ie.reference_revision):
            ie.revision = base_ie.revision
    ie.reference_revision = mapping.revision_id_foreign_to_bzr(hexsha)
    texts.insert_record_stream([FulltextContentFactory((file_id, ie.revision), (), None, "")])
    invdelta = [(oldpath, path, file_id, ie)]
    return invdelta, {}, {}


def remove_disappeared_children(path, base_children, existing_children):
    ret = []
    deletable = [(osutils.pathjoin(path, k), v) for k,v in base_children.iteritems() if k not in existing_children]
    while deletable:
        (path, ie) = deletable.pop()
        ret.append((path, None, ie.file_id, None))
        if ie.kind == "directory":
            for name, child_ie in ie.children.iteritems():
                deletable.append((osutils.pathjoin(path, name), child_ie))
    return ret


def import_git_tree(texts, mapping, path, hexsha, base_inv, base_ie, parent_id,
    revision_id, parent_invs, shagitmap, lookup_object, allow_submodules=False):
    """Import a git tree object into a bzr repository.

    :param texts: VersionedFiles object to add to
    :param path: Path in the tree
    :param tree: A git tree object
    :param base_inv: Base inventory against which to return inventory delta
    :return: Inventory delta for this subtree
    """
    invdelta = []
    file_id = mapping.generate_file_id(path)
    # We just have to hope this is indeed utf-8:
    ie = InventoryDirectory(file_id, urlutils.basename(path.decode("utf-8")),
        parent_id)
    if base_ie is None:
        # Newly appeared here
        ie.revision = revision_id
        texts.insert_record_stream([FulltextContentFactory((file_id, ie.revision), (), None, "")])
        invdelta.append((None, path, file_id, ie))
    else:
        # See if this has changed at all
        try:
            base_sha = shagitmap.lookup_tree(file_id, base_inv.revision_id)
        except KeyError:
            pass
        else:
            if base_sha == hexsha:
                # If nothing has changed since the base revision, we're done
                return [], {}, []
        if base_ie.kind != "directory":
            ie.revision = revision_id
            texts.insert_record_stream([FulltextContentFactory((ie.file_id, ie.revision), (), None, "")])
            invdelta.append((base_inv.id2path(ie.file_id), path, ie.file_id, ie))
    if base_ie is not None and base_ie.kind == "directory":
        base_children = base_ie.children
    else:
        base_children = {}
    # Remember for next time
    existing_children = set()
    child_modes = {}
    shamap = []
    tree = lookup_object(hexsha)
    for mode, name, child_hexsha in tree.entries():
        basename = name.decode("utf-8")
        existing_children.add(basename)
        child_path = osutils.pathjoin(path, name)
        if stat.S_ISDIR(mode):
            subinvdelta, grandchildmodes, subshamap = import_git_tree(
                    texts, mapping, child_path, child_hexsha, base_inv,
                    base_children.get(basename), file_id, revision_id,
                    parent_invs, shagitmap, lookup_object,
                    allow_submodules=allow_submodules)
            invdelta.extend(subinvdelta)
            child_modes.update(grandchildmodes)
            shamap.extend(subshamap)
        elif S_ISGITLINK(mode): # submodule
            if not allow_submodules:
                raise SubmodulesRequireSubtrees()
            subinvdelta, grandchildmodes, subshamap = import_git_submodule(
                    texts, mapping, child_path, child_hexsha, base_inv, base_children.get(basename),
                    file_id, revision_id, parent_invs, shagitmap, lookup_object)
            invdelta.extend(subinvdelta)
            child_modes.update(grandchildmodes)
            shamap.extend(subshamap)
        else:
            subinvdelta, subshamap = import_git_blob(texts, mapping,
                    child_path, child_hexsha, base_inv, base_children.get(basename), file_id,
                    revision_id, parent_invs, shagitmap, lookup_object,
                    mode_is_executable(mode), stat.S_ISLNK(mode))
            invdelta.extend(subinvdelta)
            shamap.extend(subshamap)
        if mode not in (stat.S_IFDIR, DEFAULT_FILE_MODE,
                        stat.S_IFLNK, DEFAULT_FILE_MODE|0111):
            child_modes[child_path] = mode
    # Remove any children that have disappeared
    if base_ie is not None and base_ie.kind == "directory":
        invdelta.extend(remove_disappeared_children(base_inv.id2path(file_id),
            base_children, existing_children))
    shamap.append((hexsha, "tree", (file_id, revision_id)))
    return invdelta, child_modes, shamap


def approx_inv_size(inv):
    # Very rough estimate, 1k per inventory entry
    return len(inv) * 1024


def import_git_commit(repo, mapping, head, lookup_object,
                      target_git_object_retriever, parent_invs_cache):
    o = lookup_object(head)
    rev = mapping.import_commit(o)
    # We have to do this here, since we have to walk the tree and
    # we need to make sure to import the blobs / trees with the right
    # path; this may involve adding them more than once.
    parent_invs = []
    for parent_id in rev.parent_ids:
        try:
            parent_invs.append(parent_invs_cache[parent_id])
        except KeyError:
            parent_inv = repo.get_inventory(parent_id)
            parent_invs.append(parent_inv)
            parent_invs_cache[parent_id] = parent_inv
    if parent_invs == []:
        base_inv = Inventory(root_id=None)
        base_ie = None
    else:
        base_inv = parent_invs[0]
        base_ie = base_inv.root
    inv_delta, unusual_modes, shamap = import_git_tree(repo.texts,
            mapping, "", o.tree, base_inv, base_ie, None, rev.revision_id,
            parent_invs, target_git_object_retriever._idmap, lookup_object,
            allow_submodules=getattr(repo._format, "supports_tree_reference", False))
    target_git_object_retriever._idmap.add_entries(shamap)
    if unusual_modes != {}:
        for path, mode in unusual_modes.iteritems():
            warn_unusual_mode(rev.foreign_revid, path, mode)
        mapping.import_unusual_file_modes(rev, unusual_modes)
    try:
        basis_id = rev.parent_ids[0]
    except IndexError:
        basis_id = NULL_REVISION
        base_inv = None
    rev.inventory_sha1, inv = repo.add_inventory_by_delta(basis_id,
              inv_delta, rev.revision_id, rev.parent_ids,
              base_inv)
    parent_invs_cache[rev.revision_id] = inv
    repo.add_revision(rev.revision_id, rev)
    if "verify" in debug.debug_flags:
        new_unusual_modes = mapping.export_unusual_file_modes(rev)
        if new_unusual_modes != unusual_modes:
            raise AssertionError("unusual modes don't match: %r != %r" % (unusual_modes, new_unusual_modes))
        objs = inventory_to_tree_and_blobs(inv, repo.texts, mapping, unusual_modes)
        for newsha1, newobj, path in objs:
            assert path is not None
            if path == "":
                oldsha1 = o.tree
            else:
                (oldmode, oldsha1) = tree_lookup_path(lookup_object, o.tree, path)
            if oldsha1 != newsha1:
                raise AssertionError("%r != %r in %s" % (oldsha1, newsha1, path))


def import_git_objects(repo, mapping, object_iter,
    target_git_object_retriever, heads, pb=None, limit=None):
    """Import a set of git objects into a bzr repository.

    :param repo: Target Bazaar repository
    :param mapping: Mapping to use
    :param object_iter: Iterator over Git objects.
    :return: Tuple with pack hints and last imported revision id
    """
    def lookup_object(sha):
        try:
            return object_iter[sha]
        except KeyError:
            return target_git_object_retriever[sha]
    # TODO: a more (memory-)efficient implementation of this
    graph = []
    checked = set()
    heads = list(set(heads))
    parent_invs_cache = lru_cache.LRUSizeCache(compute_size=approx_inv_size,
                                               max_size=MAX_INV_CACHE_SIZE)
    target_git_object_retriever.start_write_group() # FIXME: try/finally
    # Find and convert commit objects
    while heads:
        if pb is not None:
            pb.update("finding revisions to fetch", len(graph), None)
        head = heads.pop()
        assert isinstance(head, str)
        try:
            o = lookup_object(head)
        except KeyError:
            continue
        if isinstance(o, Commit):
            rev = mapping.import_commit(o)
            if repo.has_revision(rev.revision_id):
                continue
            squash_revision(repo, rev)
            graph.append((o.id, o.parents))
            target_git_object_retriever._idmap.add_entry(o.id, "commit",
                    (rev.revision_id, o.tree))
            heads.extend([p for p in o.parents if p not in checked])
        elif isinstance(o, Tag):
            if o.object[1] not in checked:
                heads.append(o.object[1])
        else:
            trace.warning("Unable to import head object %r" % o)
        checked.add(o.id)
    del checked
    # Order the revisions
    # Create the inventory objects
    batch_size = 100
    revision_ids = topo_sort(graph)
    pack_hints = []
    if limit is not None:
        revision_ids = revision_ids[:limit]
    last_imported = None
    for offset in range(0, len(revision_ids), batch_size):
        repo.start_write_group()
        try:
            for i, head in enumerate(revision_ids[offset:offset+batch_size]):
                if pb is not None:
                    pb.update("fetching revisions", offset+i, len(revision_ids))
                import_git_commit(repo, mapping, head, lookup_object,
                                  target_git_object_retriever,
                                  parent_invs_cache)
                last_imported = head
        except:
            repo.abort_write_group()
            raise
        else:
            hint = repo.commit_write_group()
            if hint is not None:
                pack_hints.extend(hint)
    target_git_object_retriever.commit_write_group()
    return pack_hints, last_imported


class InterGitRepository(InterRepository):

    _matching_repo_format = GitRepositoryFormat()

    @staticmethod
    def _get_repo_format_to_test():
        return None

    def copy_content(self, revision_id=None, pb=None):
        """See InterRepository.copy_content."""
        self.fetch(revision_id, pb, find_ghosts=False)

    def fetch(self, revision_id=None, pb=None, find_ghosts=False,
        mapping=None, fetch_spec=None):
        self.fetch_refs(revision_id=revision_id, pb=pb,
            find_ghosts=find_ghosts, mapping=mapping, fetch_spec=fetch_spec)


class InterGitNonGitRepository(InterGitRepository):
    """Base InterRepository that copies revisions from a Git into a non-Git
    repository."""

    def fetch_refs(self, revision_id=None, pb=None, find_ghosts=False,
              mapping=None, fetch_spec=None):
        if mapping is None:
            mapping = self.source.get_mapping()
        if revision_id is not None:
            interesting_heads = [revision_id]
        elif fetch_spec is not None:
            interesting_heads = fetch_spec.heads
        else:
            interesting_heads = None
        self._refs = {}
        def determine_wants(refs):
            self._refs = refs
            if interesting_heads is None:
                ret = [sha for (ref, sha) in refs.iteritems() if not ref.endswith("^{}")]
            else:
                ret = [mapping.revision_id_bzr_to_foreign(revid)[0] for revid in interesting_heads if revid not in (None, NULL_REVISION)]
            return [rev for rev in ret if not self.target.has_revision(mapping.revision_id_foreign_to_bzr(rev))]
        (pack_hint, _) = self.fetch_objects(determine_wants, mapping, pb)
        if pack_hint is not None and self.target._format.pack_compresses:
            self.target.pack(hint=pack_hint)
        if interesting_heads is not None:
            present_interesting_heads = self.target.has_revisions(interesting_heads)
            missing_interesting_heads = set(interesting_heads) - present_interesting_heads
            if missing_interesting_heads:
                raise AssertionError("Missing interesting heads: %r" % missing_interesting_heads)
        return self._refs


_GIT_PROGRESS_RE = re.compile(r"(.*?): +(\d+)% \((\d+)/(\d+)\)")
def report_git_progress(pb, text):
    text = text.rstrip("\r\n")
    g = _GIT_PROGRESS_RE.match(text)
    if g is not None:
        (text, pct, current, total) = g.groups()
        pb.update(text, int(current), int(total))
    else:
        pb.update(text, 0, 0)


class InterRemoteGitNonGitRepository(InterGitNonGitRepository):
    """InterRepository that copies revisions from a remote Git into a non-Git
    repository."""

    def get_target_heads(self):
        # FIXME: This should be more efficient
        all_revs = self.target.all_revision_ids()
        parent_map = self.target.get_parent_map(all_revs)
        all_parents = set()
        map(all_parents.update, parent_map.itervalues())
        return set(all_revs) - all_parents

    def fetch_objects(self, determine_wants, mapping, pb=None, limit=None):
        def progress(text):
            report_git_progress(pb, text)
        store = BazaarObjectStore(self.target, mapping)
        self.target.lock_write()
        try:
            heads = self.get_target_heads()
            graph_walker = store.get_graph_walker(
                    [store._lookup_revision_sha1(head) for head in heads])
            recorded_wants = []

            def record_determine_wants(heads):
                wants = determine_wants(heads)
                recorded_wants.extend(wants)
                return wants

            create_pb = None
            if pb is None:
                create_pb = pb = ui.ui_factory.nested_progress_bar()
            try:
                objects_iter = self.source.fetch_objects(
                            record_determine_wants, graph_walker,
                            store.get_raw, progress)
                return import_git_objects(self.target, mapping,
                    objects_iter, store, recorded_wants, pb, limit)
            finally:
                if create_pb:
                    create_pb.finished()
        finally:
            self.target.unlock()

    @staticmethod
    def is_compatible(source, target):
        """Be compatible with GitRepository."""
        # FIXME: Also check target uses VersionedFile
        return (isinstance(source, RemoteGitRepository) and
                target.supports_rich_root() and
                not isinstance(target, GitRepository))


class InterLocalGitNonGitRepository(InterGitNonGitRepository):
    """InterRepository that copies revisions from a local Git into a non-Git
    repository."""

    def fetch_objects(self, determine_wants, mapping, pb=None, limit=None):
        """Fetch objects.
        """
        wants = determine_wants(self.source._git.get_refs())
        create_pb = None
        if pb is None:
            create_pb = pb = ui.ui_factory.nested_progress_bar()
        target_git_object_retriever = BazaarObjectStore(self.target, mapping)
        try:
            self.target.lock_write()
            try:
                return import_git_objects(self.target, mapping,
                    self.source._git.object_store,
                    target_git_object_retriever, wants, pb, limit)
            finally:
                self.target.unlock()
        finally:
            if create_pb:
                create_pb.finished()

    @staticmethod
    def is_compatible(source, target):
        """Be compatible with GitRepository."""
        # FIXME: Also check target uses VersionedFile
        return (isinstance(source, LocalGitRepository) and
                target.supports_rich_root() and
                not isinstance(target, GitRepository))


class InterGitGitRepository(InterGitRepository):
    """InterRepository that copies between Git repositories."""

    def fetch_objects(self, determine_wants, mapping, pb=None):
        def progress(text):
            trace.note("git: %s", text)
        graphwalker = self.target._git.get_graph_walker()
        if (isinstance(self.source, LocalGitRepository) and
            isinstance(self.target, LocalGitRepository)):
            return self.source._git.fetch(self.target._git, determine_wants,
                progress)
        elif (isinstance(self.source, LocalGitRepository) and
              isinstance(self.target, RemoteGitRepository)):
            raise NotImplementedError
        elif (isinstance(self.source, RemoteGitRepository) and
              isinstance(self.target, LocalGitRepository)):
            f, commit = self.target._git.object_store.add_thin_pack()
            try:
                refs = self.source._git.fetch_pack(determine_wants,
                    graphwalker, f.write, progress)
                commit()
                return refs
            except:
                f.close()
                raise
        else:
            raise AssertionError

    def fetch_refs(self, revision_id=None, pb=None, find_ghosts=False,
              mapping=None, fetch_spec=None, branches=None):
        if mapping is None:
            mapping = self.source.get_mapping()
        r = self.target._git
        if revision_id is not None:
            args = [mapping.revision_id_bzr_to_foreign(revision_id)[0]]
        elif fetch_spec is not None:
            args = [mapping.revision_id_bzr_to_foreign(revid)[0] for revid in fetch_spec.heads]
        if branches is not None:
            determine_wants = lambda x: [x[y] for y in branches if not x[y] in r.object_store]
        elif fetch_spec is None and revision_id is None:
            determine_wants = r.object_store.determine_wants_all
        else:
            determine_wants = lambda x: [y for y in args if not y in r.object_store]
        return self.fetch_objects(determine_wants, mapping)[0]


    @staticmethod
    def is_compatible(source, target):
        """Be compatible with GitRepository."""
        return (isinstance(source, GitRepository) and
                isinstance(target, GitRepository))
