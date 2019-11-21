# TiGL Python Examples

The easiest way to install TiGL is via Anaconda/Miniconda. We suggest installing into a clean environment called `tigl`:

```bash
conda create -n tigl tigl3 -c dlr-sc
conda activate tigl
```

To run the jupyter examples, some further dependencies must be met, which can be installed via

```bash
conda install pip numpy jupyter rise pythreejs -c conda-forge
pip install jupyter-contrib-nbextensions
jupyter contrib nbextension install --user
jupyter nbextension enable splitcell/splitcell
```

## Contents

### CPACSCreator Animation

Using the CPACSCreator to generate an airplane from scratch and create an animation from a sequence of cpacs configurations.

 - [cpacscreator-animation](cpacscreator-animation)

### Geometry Modeling

Using TiGL's internal geometry modeling algorithms for surface skinning and Gordon surface creation. Run the demo by pressing the button below:

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/DLR-SC/tigl-examples/master?filepath=tigl%2Fpython%2Fgeometry-modeling%2Fgeometry-modeling.ipynb)

