# RA1STATS

## DO NOT MERGE WITH MASTER!

Hacky as shit, use at your own risk!

## License
[GPLv3](http://www.gnu.org/licenses/gpl.html)

## Quick Start
1. Clone the repository:
```bash
git clone https://github.com/elaird/ra1stats.git
cd ra1stats
git submodule update --init
```

2. If needed, set up the environment:
```bash
source env.sh
```

3. Run it:
```bash
./stats.py --help
./test.py --help
```

## Brief Description
* The likelihood function is built in workspace.py.  To fit a set of
data or test a signal model, one uses an instance of the class
driver.driver.

* test.py shows how to use an instance of driver, and will produce a
pdf file in the subdirectory plots.  The observations, MC yields,
etc. are stored in inputData/.  The switches selecting options for the
likelihood are in likelihood/.

* stats.py allows one to run on many signal models in parallel, using
either one computer (`--local`) or a farm (`--batch`).  The results
are merged into a root file using `--merge`.

## Requirements
* ROOT >= v5.32.01
* python >= v2.6

## Notes
Useful pages for setting up and learning pyROOT:
[here](http://root.cern.ch/drupal/content/how-use-use-python-pyroot-interpreter) and [here](http://wlav.web.cern.ch/wlav/pyroot/)

## Bugs
Please report any problems on our [issues page](https://github.com/elaird/ra1stats/issues)
