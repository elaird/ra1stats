# RA1STATS

## License
[GPLv3](http://www.gnu.org/licenses/gpl.html)

## Quick Start
1. Clone the repository:
```bash
git clone git://github.com/elaird/ra1stats.git
```
or, if you have forked it:
```bash
git clone git://github.com/your_username/ra1stats.git
```
then
```cd ra1stats
git submodule init
```


2. If needed, set up the environment:
```bash
source env.sh
```

3. Run it:
```bash
./stats.py --help
```

## Brief Description
* The likelihood function is specified in workspace.py.  To fit a set of
data or test a signal model, one uses an instance of the class
fresh.foo.

* test.py shows how to use an instance of fresh.foo, and will produce
a pdf file in the subdirectory plots.  The plotting is done in
plotting.py.  The observations, MC yields, etc. are stored in
inputData.py.  The switches selecting options for the likelihood are
in likelihoodSpec.py.

* stats.py and configuration.py allow one to run on many signal models
  in parallel, using either one computer (`--local`) or a farm
  (`--batch`).  The results are merged into a root file using `--merge`.

## Requirements
* ROOT >= v5.32.01
* python >= v2.6

## Notes
Useful pages for setting up and learning pyROOT:
[here](http://root.cern.ch/drupal/content/how-use-use-python-pyroot-interpreter) and [here](http://wlav.web.cern.ch/wlav/pyroot/)

## Bugs
Please report any problems on our [issues page](https://github.com/elaird/ra1stats/issues)
