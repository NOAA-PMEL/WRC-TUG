This shows a few different ways to decimate the data in a long time series so it can be plotted using a browser-based plotting library (like Plotly). The client-side rendering of such a plot is limited because each data point becomes a node in the DOM tree in the browser. To avoid overwhelming the browser, this example shows different ways to deimate the data before plotting. When the plot is zoomed and the number of points in the full resolution of the data is reduced, so eventually the decimation stops the full full resolution of the data is shown in the plot.

If you were doing this in your own code, you'd probably only use one of the decimation methods and when the data was small enough return the full resoltuion plot in the same place in the layout.