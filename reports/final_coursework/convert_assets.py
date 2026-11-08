"""Convert only the four manuscript SVGs to vector PDF 1.5 with CairoSVG 2.9.0."""
import hashlib
import json
from pathlib import Path
import cairocffi as cairo
from cairosvg.surface import PDFSurface

HERE = Path(__file__).resolve().parent
ASSETS = HERE.parent / 'publication_assets'

class PDF15Surface(PDFSurface):
    def _create_surface(self, width, height):
        surface, width, height = super()._create_surface(width, height)
        surface.restrict_to_version(cairo.PDF_VERSION_1_5)
        return surface, width, height

if __name__ == '__main__':
    records=[]
    for source in json.loads((HERE/'conversion_checks.json').read_text())['figures']:
        path=ASSETS/source
        target=HERE/'assets'/(path.stem+'.pdf')
        PDF15Surface.convert(url=str(path),write_to=str(target))
        records.append({'source':source,'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'output':str(target.relative_to(HERE)),'output_sha256':hashlib.sha256(target.read_bytes()).hexdigest()})
    (HERE/'asset_manifest.json').write_text(json.dumps(records,indent=2)+'\n')
