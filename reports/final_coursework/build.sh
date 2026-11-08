#!/bin/sh
set -eu
cd "$(dirname "$0")"
# Fixed date for reproducible PDF metadata. No manuscript or model access is needed.
export SOURCE_DATE_EPOCH=1794096000
tectonic --keep-logs main.tex
mv main.pdf AMEM_FTEC5660_Report.pdf
