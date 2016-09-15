# -*- coding: utf-8 -*-
import pkg_resources
from Acquisition import aq_base
from App.class_init import InitializeClass
from Products.CMFEditions.Modifiers import ConditionalTalesModifier
from Products.CMFEditions.interfaces.IModifier import ICloneModifier
from Products.CMFEditions.interfaces.IModifier import IConditionalTalesModifier
from Products.CMFEditions.interfaces.IModifier import ISaveRetrieveModifier
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from ZODB.blob import Blob
from persistent.list import PersistentList
from persistent.mapping import PersistentMapping
from zope.annotation import IAnnotations
from zope.interface import implementer
from plone.tiles.data import ANNOTATIONS_KEY_PREFIX
from plone.namedfile import NamedFile

try:
    from plone.namedfile import NamedBlobFile
    HAS_BLOBS = True
except ImportError:
    HAS_BLOBS = False

try:
    pkg_resources.get_distribution('z3c.relationfield')
except pkg_resources.DistributionNotFound:
    class RelationValue(object):
        pass
else:
    from z3c.relationfield import RelationValue


def install(portal_modifier, ids=None):
    """Registers modifiers in the modifier registry (at tool install time).
    """
    for m in modifiers:
        id_ = m['id']
        if ids is not None and id_ not in ids:
            continue
        if id_ in portal_modifier.objectIds():
            continue
        title = m['title']
        modifier = m['modifier']()
        wrapper = m['wrapper'](id_, modifier, title)
        enabled = m['enabled']
        if IConditionalTalesModifier.providedBy(wrapper):
            wrapper.edit(enabled, m['condition'])
        else:
            wrapper.edit(enabled)

        portal_modifier.register(m['id'], wrapper)


manage_CleanTileAnnotationsAddForm = \
    PageTemplateFile('www/CleanTileAnnotations.pt',
                     globals(),
                     __name__='manage_CleanTileAnnotationsAddForm')


def manage_addCleanTileAnnotations(self, id, title=None, REQUEST=None):
    """Add a skip parent pointers modifier
    """
    modifier = CleanTileAnnotations()
    self._setObject(id, ConditionalTalesModifier(id, modifier, title))

    if REQUEST is not None:
        REQUEST['RESPONSE'].redirect(self.absolute_url() + '/manage_main')


ANNOTATION_KEY_PREFIXES = [ANNOTATIONS_KEY_PREFIX,  # plone.tiles default
                           'plone.tiles.scale']  # collective.cover scales
MAPPING_TYPES = [dict, PersistentMapping]
ITERABLE_TYPES = [list, tuple, set, frozenset, PersistentList]
CLEANABLE_TYPES = [Blob, NamedFile, RelationValue]

if HAS_BLOBS:
    CLEANABLE_TYPES.append(NamedBlobFile)


def getReferences(obj):
    """Recursively walk through the annotation value and collect
    references to all CLEANABLE_TYPES so that they can be skipped
    when pickling annotations when CMFEditions versioning does
    the deepcopy of them.
    """
    refs = []
    if any([isinstance(obj, t) for t in MAPPING_TYPES]):
        refs.extend(getReferences(obj.values()))
    if not any([isinstance(obj, t) for t in ITERABLE_TYPES]):
        return refs
    for value in obj:
        if any([isinstance(value, t) for t in CLEANABLE_TYPES]):
            refs.append(id(aq_base(value)))
        elif any([isinstance(value, t) for t in MAPPING_TYPES]):
            refs.extend(getReferences(value.values()))
        elif any([isinstance(value, t) for t in ITERABLE_TYPES]):
            refs.extend(getReferences(value))
    return refs


def restoreValues(obj, repo_clone, key=None):
    """Recursively walk through the annotation value of current
    working copy and whenever a value of CLEANABLE_TYPE is seen,
    and it seems to have a place in the restored repository clone,
    we
    """
    if any([isinstance(obj, t) for t in MAPPING_TYPES]):
        for key, value in obj.items():
            if any([isinstance(value, t) for t in MAPPING_TYPES]):
                # Handle mappings recursively
                if key in repo_clone and repo_clone.get(key) is not None:
                    restoreValues(value, repo_clone[key])
            elif any([isinstance(value, t) for t in CLEANABLE_TYPES]):
                # Assign simple value by reference
                repo_clone[key] = value
            else:
                # Recurse to handle possible iterable values
                restoreValues(value, repo_clone, key)
    elif any([isinstance(obj, t) for t in ITERABLE_TYPES]) and key:
        # Check if working copy iterable has anything to restore
        if [x for x in obj if [isinstance(x, t) for t in CLEANABLE_TYPES]]:
            # And if so, use the working copy
            repo_clone[key] = obj


@implementer(ICloneModifier, ISaveRetrieveModifier)
class CleanTileAnnotations:
    """Prevent versioning of blobs and relations in tile annotations"""

    def getOnCloneModifiers(self, obj):
        refs = []
        annotations = IAnnotations(obj)
        for key in annotations:
            if not any([key.startswith(k) for k in ANNOTATION_KEY_PREFIXES]):
                continue
            refs.extend(getReferences(annotations[key]))

        def persistent_id(obj):
            if id(aq_base(obj)) in refs:
                return True
            return None

        def persistent_load(ignored):
            return None

        return persistent_id, persistent_load, [], []

    def beforeSaveModifier(self, obj, clone):
        return {}, [], []

    def afterRetrieveModifier(self, obj, repo_clone, preserve=()):
        """Replace removed values from working copy on restore"""
        annotations = IAnnotations(obj)
        for key in annotations:
            if not key.startswith(ANNOTATIONS_KEY_PREFIX):
                continue
            if key in IAnnotations(repo_clone):
                restoreValues(annotations[key], IAnnotations(repo_clone)[key])
        return [], [], {}


InitializeClass(CleanTileAnnotations)

modifiers = (
    {
        'id': 'CleanTileAnnotations',
        'title': 'Skip storing blobs or relations on tile annotations',
        'enabled': True,
        'condition': 'python:True',
        'wrapper': ConditionalTalesModifier,
        'modifier': CleanTileAnnotations,
        'form': manage_CleanTileAnnotationsAddForm,
        'factory': manage_addCleanTileAnnotations,
        'icon': 'www/modifier.gif',
    },
)
