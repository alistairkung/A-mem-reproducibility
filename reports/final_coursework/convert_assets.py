"""Convert only the four manuscript SVGs to vector PDF 1.5 with CairoSVG 2.9.0."""
import hashlib
import json
from pathlib import Path
from lxml import etree
import cairocffi as cairo
from cairosvg.surface import PDFSurface

HERE = Path(__file__).resolve().parent
ASSETS = HERE.parent / 'publication_assets'

class PDF15Surface(PDFSurface):
    def _create_surface(self, width, height):
        surface, width, height = super()._create_surface(width, height)
        surface.restrict_to_version(cairo.PDF_VERSION_1_5)
        surface.set_metadata(cairo.PDF_METADATA_CREATE_DATE, "2026-11-08T00:00:00Z")
        surface.set_metadata(cairo.PDF_METADATA_MOD_DATE, "2026-11-08T00:00:00Z")
        return surface, width, height

def updated_policy_labels(source):
    """Rename display labels in SVG text elements, preserving all plotted data."""
    root = etree.fromstring(source)
    changes = []
    for label in root.iter('{http://www.w3.org/2000/svg}text'):
        original = label.text or ''
        updated = original.replace('Alternative-reference', 'Updated').replace('Complementary', 'Updated')
        if updated != original:
            label.text = updated
            changes.append({'from': original, 'to': updated})
    return (etree.tostring(root, encoding='UTF-8') if changes else source), changes


if __name__ == '__main__':
    records=[]
    for source in json.loads((HERE/'conversion_checks.json').read_text())['figures']:
        path=ASSETS/source
        target=HERE/'assets'/(path.stem+'.pdf')
        original = path.read_bytes()
        artwork, changes = updated_policy_labels(original)
        PDF15Surface.convert(bytestring=artwork, url=str(path), write_to=str(target))
        records.append({'source':source,'source_sha256':hashlib.sha256(original).hexdigest(),'label_changes':changes,'output':str(target.relative_to(HERE)),'output_sha256':hashlib.sha256(target.read_bytes()).hexdigest()})
    (HERE/'asset_manifest.json').write_text(json.dumps(records,indent=2)+'\n')
