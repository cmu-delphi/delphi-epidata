# This script sets up the correct directory structure within the `delphi_img`
# docker image.

# Some notes on package structure:
#   - Python package names can't contain hyphens, so hyphens in repo names are
#     replaced with underscores in the package hierarchy. (An exception is the
#     repo `delphi-epidata`, which is renamed to simply `epidata`.)
#   - Repos are organized such that the main code for the package is inside of
#     a `src/` directory. When deployed, `src/` is elided. (An exception is the
#     legacy `undef-analysis` repo, which has sources at the top-level.)

# bail if anything fails
set -e

# create python package `undefx`
mkdir undefx
mv repos/undefx/py3tester/src undefx/py3tester
mv repos/undefx/undef-analysis undefx/undef_analysis

# create python package `delphi`
mkdir delphi
mv repos/delphi/operations/src delphi/operations
mv repos/delphi/utils/src delphi/utils
mv repos/delphi/github-deploy-repo/src delphi/github_deploy_repo
mv repos/delphi/delphi-epidata/src delphi/epidata
mv repos/delphi/flu-contest/src delphi/flu_contest
mv repos/delphi/nowcast/src delphi/nowcast
