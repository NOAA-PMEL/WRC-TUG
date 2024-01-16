I created this [DASH application (PMEL VPN required)](https://dash.pmel.noaa.gov/tammy) using Plotly App Studio. The proceedure I followed was a bit convoluted because this is a pre-release product.

I got the idea for this example from reading the [2023 Hurricane mission blog](https://www.pmel.noaa.gov/saildrone-hurricane/2023/mission-blog-2023.html). The October 25 entry mentions the encounter with Hurricane Tammy. The interactive dashboard is not as cool as the animation in the blob, but one can actaully interact with the plots and data. It was simple enough to build, that similar things could be built and deployed during future missions and linked to from the blog.

I built this on our development server (sour.pmel.noaa.gov).

1. I disabled by current conda environment.
2. I built a virtual environtment following [these instructions](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/).
    * Namely: python3 -m venv .venv; source .venv/bin/activate
3. I installed the app-studio package and all it's dependecies into this virtual environment.
   * pip install app-studio --extra-index-url=[CONTACT ME FOR THE MAGIC URL THAT GOES HERE].
   * N.B. I had to install multidict, typing_extensions, attr and yarl "by hand" for some reason. You can perhaps save yourself some trouble by installing them first.
  
4. Created up my [notebook]() to load the data and make the two plots.
5. Started App Studio. I used the following command since I wanted a specific host and port:
  * PORT=8940;HOST=sour.pmel.noaa.gov app-studio app_studio_plots.ipynb
6. Used the GUI to rearrange the plots and add the title, explanatory text, my name and contact info.
