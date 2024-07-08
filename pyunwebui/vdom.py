from __future__ import annotations

import itertools
from typing import TypeAlias

from attrs import define, field
from cattrs.preconf.json import make_converter

__all__ = (
    'Tag', 'TagOrText', 'TagList',
    'DiffNoop', 'DiffReplace', 'DiffDetailed', 'DiffListItemCreate', 'DiffListItemRemove', 'DiffList',
    'diff_tag', 'diff_tags',
)

TagOrText: TypeAlias = 'Tag | str'
TagList: TypeAlias = 'list[TagOrText]'

converter = make_converter()


@define
class Tag:
    tag_name: str
    attributes: dict[str, str]
    children: list[TagOrText]
    # on: dict[str, str] = field(factory=dict)


@define
class DiffNoop:
    noop: True = True


@define
class DiffReplace:
    replace: Tag | str


@define
class DiffListItemCreate:
    create: Tag | str


@define
class DiffListItemRemove:
    remove: True = True


@define
class DiffModify:
    modify: DiffDetailed


DiffList: TypeAlias = 'list[DiffNoop | DiffModify | DiffReplace | DiffListItemCreate | DiffListItemRemove]'


@define
class DiffDetailed:
    removes: list[str]
    sets: dict[str, str]
    children: DiffList


def diff_tag(a: Tag | str, b: Tag | str) -> DiffNoop | DiffModify | DiffReplace:
    if isinstance(a, str) or isinstance(b, str):
        if a == b:
            return DiffNoop()
        else:
            return DiffReplace(b)

    if a.tag_name != b.tag_name:
        return DiffReplace(b)

    removes = list(a.attributes.keys() - b.attributes.keys())
    sets = {key: b.attributes[key] for key in b.attributes.keys() if b.attributes[key] != a.attributes[key]}
    children = diff_tags(a.children, b.children)
    return DiffModify(DiffDetailed(removes, sets, children))


def diff_tags(aa: list[Tag | str], bb: list[Tag | str]) -> DiffList:
    p = []
    for a, b in itertools.zip_longest(aa, bb):
        if a is None:
            p.append(DiffListItemCreate(b))
        elif b is None:
            p.append(DiffListItemRemove())
        else:
            p.append(diff_tag(a, b))
    return p


NO_CHILDREN_TAGS = {
    'IMG',
    'META',
    # ...
}


def to_html_str(tag: Tag | str | list[Tag | str]) -> str:
    if isinstance(tag, str):
        return tag
    if isinstance(tag, list):
        return ''.join((to_html_str(item) for item in tag))
    attrs = ''.join(f' {k}="{v}"' for k, v in tag.attributes.items())
    if tag.tag_name.upper() in NO_CHILDREN_TAGS:
        return f'<{tag.tag_name}{attrs}/>'
    else:
        children = ''.join((to_html_str(child) for child in tag.children))
        return f'<{tag.tag_name}{attrs}>{children}<{tag.tag_name}/>'


def serialize(tag: Tag | str | list[Tag | str]) -> str:
    return converter.dumps(tag)


def serialize_diff(diff: DiffNoop | DiffModify | DiffReplace | DiffList) -> str:
    return converter.dumps(diff)
