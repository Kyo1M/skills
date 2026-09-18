#!/usr/bin/env python3
"""Convert explicitly named footer text boxes to native PowerPoint slide fields.

No third-party dependencies. Never changes the input or overwrites an output.
"""
import argparse
import json
import posixpath
import uuid
from pathlib import Path
from xml.dom import minidom
from zipfile import ZipFile

A = 'http://schemas.openxmlformats.org/drawingml/2006/main'
P = 'http://schemas.openxmlformats.org/presentationml/2006/main'
R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'


def children(node, ns, name):
    return [n for n in node.childNodes if n.namespaceURI == ns and n.localName == name]


def process(source, output=None, shape_name='SlideNumber', skip=()):
    patches, report = {}, []
    with ZipFile(source) as archive:
        pres = minidom.parseString(archive.read('ppt/presentation.xml'))
        rels = minidom.parseString(archive.read('ppt/_rels/presentation.xml.rels'))
        targets = {n.getAttribute('Id'): n.getAttribute('Target') for n in
                   rels.documentElement.childNodes if n.nodeType == n.ELEMENT_NODE}
        ids = pres.getElementsByTagNameNS(P, 'sldId')
        first = int(pres.documentElement.getAttribute('firstSlideNum') or '1')
        if set(skip) - set(range(1, len(ids) + 1)):
            raise ValueError('Skipped slide is outside presentation order')
        for index, slide_id in enumerate(ids, 1):
            if index in skip:
                continue
            target = targets[slide_id.getAttributeNS(R, 'id')]
            part = (target.lstrip('/') if target.startswith('/') else
                    posixpath.normpath(posixpath.join('ppt', target)))
            doc = minidom.parseString(archive.read(part))
            matches = []
            for shape in doc.getElementsByTagNameNS(P, 'sp'):
                props = shape.getElementsByTagNameNS(P, 'cNvPr')
                if props and props[0].getAttribute('name') == shape_name:
                    matches.append(shape)
            if len(matches) != 1:
                raise ValueError(f'Slide {index}: expected one {shape_name!r}, found {len(matches)}')
            shape = matches[0]
            bodies = children(shape, P, 'txBody')
            paragraphs = children(bodies[0], A, 'p') if len(bodies) == 1 else []
            if len(paragraphs) != 1:
                raise ValueError(f'Slide {index}: footer must have one text paragraph')
            paragraph = paragraphs[0]
            fields = children(paragraph, A, 'fld')
            runs = children(paragraph, A, 'r')
            number = str(first + index - 1)
            if output is None:
                if len(fields) != 1 or fields[0].getAttribute('type') != 'slidenum' or runs:
                    raise ValueError(f'Slide {index}: footer is not a native slide-number field')
                cached = ''.join(t.firstChild.data if t.firstChild else '' for t in
                                 children(fields[0], A, 't'))
                if cached != number:
                    raise ValueError(f'Slide {index}: cached number {cached!r}, expected {number}')
            else:
                if children(paragraph, A, 'br'):
                    raise ValueError(f'Slide {index}: footer contains a line break')
                text = ''.join(n.firstChild.data if n.firstChild else '' for n in
                               paragraph.getElementsByTagNameNS(A, 't')).strip()
                if text and not text.isdecimal():
                    raise ValueError(f'Slide {index}: footer must contain only a number, got {text!r}')
                if any(f.getAttribute('type') != 'slidenum' for f in fields):
                    raise ValueError(f'Slide {index}: footer contains another field type')
                prefix = paragraph.prefix or 'a'
                field = doc.createElementNS(A, prefix + ':fld')
                field.setAttribute('id', fields[0].getAttribute('id') if fields else
                                   '{' + str(uuid.uuid4()).upper() + '}')
                field.setAttribute('type', 'slidenum')
                source_run = (fields + runs)[0] if fields or runs else None
                styles = children(source_run, A, 'rPr') if source_run else []
                if styles:
                    field.appendChild(styles[0].cloneNode(True))
                value = doc.createElementNS(A, prefix + ':t')
                value.appendChild(doc.createTextNode(number))
                field.appendChild(value)
                for old in runs + fields:
                    paragraph.removeChild(old)
                end = children(paragraph, A, 'endParaRPr')
                paragraph.insertBefore(field, end[0] if end else None)
                patches[part] = doc.toxml(encoding='UTF-8')
            report.append({'slide': index, 'part': part, 'number': number})
        if not report:
            raise ValueError('No numbered slides selected')
        if output is not None:
            if Path(source).resolve() == Path(output).resolve():
                raise ValueError('Input and output must differ')
            with ZipFile(output, 'x') as dest:
                dest.comment = archive.comment
                for entry in archive.infolist():
                    dest.writestr(entry, patches.get(entry.filename, archive.read(entry.filename)))
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('--output', type=Path, help='Omit to validate native fields and cached numbers')
    parser.add_argument('--shape-name', default='SlideNumber')
    parser.add_argument('--skip-slide', type=int, action='append', default=[],
                        help='1-based position with no footer (repeatable; still counted)')
    args = parser.parse_args()
    result = process(args.input, args.output, args.shape_name, args.skip_slide)
    if args.output:
        process(args.output, None, args.shape_name, args.skip_slide)
    print(json.dumps({'mode': 'convert' if args.output else 'check', 'slides': result}))


if __name__ == '__main__':
    main()
