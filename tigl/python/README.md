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

Note that the jupyter examples can all be run interactively online using binder.

## Contents

 - [CPACSCreator Animation](#cpacscreator-animation)
 - [Geometry Modeling](#geometry-modeling) [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/DLR-SC/tigl-examples/master?filepath=tigl%2Fpython%2Fgeometry-modeling%2Fgeometry-modeling.ipynb)
  - [Internal API 1 - Basics](#internal-api-1)  [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/DLR-SC/tigl-examples/master?filepath=tigl%2Fpython%2Finternal-api-1-basics.ipynb)
  - [Internal API 2 - Customization and Visualization](#internal-api-2) [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/DLR-SC/tigl-examples/master?filepath=tigl%2Fpython%2Finternal-api-2-customization-visualization.ipynb)
  - [Internal API 3 - Geometry Modeling](#internal-api-3) [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/DLR-SC/tigl-examples/master?filepath=tigl%2Fpython%2Finternal-api-3-geometry-modeling.ipynb)

## CPACSCreator Animation 
<a name="cpacscreator-animation"/>

[cpacscreator-animation](cpacscreator-animation)

Using the CPACSCreator to generate an airplane from scratch and create an animation from a sequence of cpacs configurations.


## Geometry Modeling [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/DLR-SC/tigl-examples/master?filepath=tigl%2Fpython%2Fgeometry-modeling%2Fgeometry-modeling.ipynb)
<a name="geometry-modeling"/>

[geometry-modeling](geometry-modeling)

Using TiGL's internal geometry modeling algorithms for surface skinning and Gordon surface creation. This is a presentation. For an indepth tutorial with the same contents, checkout [Internal API 3 - Geometry Modeling](#internal-api-3).

## Internal API 1 - Basics  [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/DLR-SC/tigl-examples/master?filepath=tigl%2Fpython%2Finternal-api-1-basics.ipynb)
<a name="internal-api-1"/>

[internal-api-1-basics.ipynb](internal-api-1-basics.ipynb)

Using TiGL's internal API to 
 - traverse the CPACS tree, 
 - get information about the geometric components
 - creating named shapes and 
 - using the CAD exporter.

 ## Internal API 2 - Customization and Visualization [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/DLR-SC/tigl-examples/master?filepath=tigl%2Fpython%2Finternal-api-2-customization-visualization.ipynb)
<a name="internal-api-2"/>

[internal-api-2-customization-visualization.ipynb](internal-api-2-customization-visualization.ipynb)

 - using TiGL's internal API to create a wing cutout, 
 - using the SimpleGUI (does not work online)
 - using the jupyter renderer

  ## Internal API 3 - Geometry Modeling [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/DLR-SC/tigl-examples/master?filepath=tigl%2Fpython%2Finternal-api-3-geometry-modeling.ipynb)
<a name="internal-api-3"/>

[internal-api-3-geometry-modeling.ipynb](internal-api-3-geometry-modeling.ipynb)

Create a wing geometry from scratch
 - interpolating points to surfaces
 - skinning surfaces from curves
 - interpolating curve networks to Gordon surfaces