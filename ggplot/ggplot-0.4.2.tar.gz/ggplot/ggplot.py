import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.dates import DateFormatter
from matplotlib.ticker import MultipleLocator

from .components import colors, linestyles, shapes, size, linestyles
from .components import aes
from .components.legend import draw_legend
from .geoms import *
from .scales import *
from .themes import *
from .themes.theme_gray import _set_default_theme_rcparams
from .themes.theme_gray import _theme_grey_post_plot_callback
from .utils import *
import utils.six as six

import sys
import re
import warnings

if sys.flags.interactive:
    plt.ion()

def is_identity(x):
    if x in colors.COLORS:
        return True
    elif x in shapes.SHAPES:
        return True
    elif isinstance(x, (float, int)):
        return True
    else:
        return False

class ggplot(object):
    """
    ggplot is the base layer or object that you use to define
    the components of your chart (x and y axis, shapes, colors, etc.).
    You can combine it with layers (or geoms) to make complex graphics
    with minimal effort.

    Parameters
    -----------
    aesthetics:  aes (ggplot.components.aes.aes)
        aesthetics of your plot
    data:  pandas DataFrame (pd.DataFrame)
        a DataFrame with the data you want to plot

    Examples
    ----------
    p = ggplot(aes(x='x', y='y'), data=diamonds)
    print p + geom_point()
    """

    CONTINUOUS = ['x', 'y', 'size', 'alpha']
    DISCRETE = ['color', 'shape', 'marker', 'alpha', 'linestyle']

    def __init__(self, aesthetics, data):
        # ggplot should just 'figure out' which is which
        if not isinstance(data, pd.DataFrame):
            aesthetics, data = data, aesthetics

        self.aesthetics = aesthetics
        self.data = data

        # TODO: This should probably be modularized
        # Look for alias/lambda functions
        for ae, name in self.aesthetics.items():
            if name not in self.data and not is_identity(name):
                result = re.findall(r'(?:[A-Z])|(?:[A-Za_-z0-9]+)|(?:[/*+_=\(\)-])', name)
                if re.match("factor[(][A-Za-z_0-9]+[)]", name):
                    m = re.search("factor[(]([A-Za-z_0-9]+)[)]", name)
                    self.data[name] = self.data[m.group(1)].apply(str)
                else:
                    lambda_column = ""
                    for item in result:
                        if re.match("[/*+_=\(\)-]", item):
                            pass
                        elif re.match("^[0-9.]+$", item):
                            pass
                        else:
                            item = "self.data.get('%s')" % item
                        lambda_column += item
                    self.data[name] = eval(lambda_column)

        # defaults
        self.geoms= []
        self.n_wide = 1
        self.n_high = 1
        self.n_dim_x = None
        self.n_dim_y = None
        # facets
        self.facets = []
        self.facet_type = None
        self.facet_scales = None
        # components
        self.title = None
        self.xlab = None
        self.ylab = None
        # format for x/y major ticks
        self.xtick_formatter = None
        self.xbreaks = None
        self.xtick_labels = None
        self.xmajor_locator = None
        self.xminor_locator = None
        self.ytick_formatter = None
        self.xlimits = None
        self.ylimits = None
        self.scale_y_reverse = None
        self.scale_x_reverse = None
        # legend is a dictionary of {legend_type: {visual_value: legend_key}},
        # where legend_type is one of "color", "linestyle", "marker", "size";
        # visual_value is color value, line style, marker character, or size
        # value; and legend_key is a quantile.
        self.legend = {}
        # Theme releated options
        # this must be set by any theme to prevent addig the default theme
        self.theme_applied = False
        self.rcParams = {}
        # Callbacks to change aspects of each axis 
        self.post_plot_callbacks = []

        # continuous color configs
        self.color_scale = None
        self.colormap = plt.cm.Blues
        self.manual_color_list = None

    def __repr__(self):
        """Print/show the plot"""
        figure = self.draw()
        # We're going to default to making the plot appear when __repr__ is
        # called.
        #figure.show() # doesn't work in ipython notebook
        plt.show()
        # TODO: We can probably get more sugary with this
        return "<ggplot: (%d)>" % self.__hash__()

    def draw(self):
        # Adding rc=self.rcParams does not validate/parses the params which then
        # throws an error during plotting!
        with mpl.rc_context():
            if not self.theme_applied:
                _set_default_theme_rcparams(mpl)
            # will be empty if no theme was applied
            for key in six.iterkeys(self.rcParams): 
                val = self.rcParams[key]
                # there is a bug in matplotlib which does not allow None directly
                # https://github.com/matplotlib/matplotlib/issues/2543
                try:
                    if key == 'text.dvipnghack' and val is None:
                        val = "none"
                    mpl.rcParams[key] = val
                except Exception as e:
                    msg = """Setting "mpl.rcParams['%s']=%s" raised an Exception: %s""" % (key, str(val), str(e))
                    warnings.warn(msg, RuntimeWarning)
            # draw is not allowed to show a plot, so we can use to result for ggsave 
            # This sets a rcparam, so we don't have to undo it after plotting
            mpl.interactive(False)
            if self.facet_type=="grid":
                fig, axs = plt.subplots(self.n_high, self.n_wide,
                        sharex=True, sharey=True)
                plt.subplots_adjust(wspace=.05, hspace=.05)
            elif self.facet_type=="wrap":
                # add (more than) the needed number of subplots
                fig, axs = plt.subplots(self.n_high, self.n_wide)
                # there are some extra, remove the plots
                subplots_available = self.n_wide * self.n_high
                extra_subplots = subplots_available - self.n_dim_x
                for extra_plot in axs.flatten()[-extra_subplots:]:
                    extra_plot.axis('off')

                # plots is a mapping from xth-plot -> subplot position
                plots = []
                for x in range(self.n_wide):
                    for y in range(self.n_high):
                        plots.append((x, y))
                plots = sorted(plots, key=lambda x: x[1] + x[0] * self.n_high + 1)
            else:
                fig, axs = plt.subplots(self.n_high, self.n_wide)

            # Set the default plot to the first one
            plt.subplot(self.n_wide, self.n_high, 1)

            # Aes need to be initialized BEFORE we start faceting. This is b/c
            # we want to have a consistent aes mapping across facets.
            self = colors.assign_colors(self)
            self = size.assign_sizes(self)
            self = linestyles.assign_linestyles(self)
            self = shapes.assign_shapes(self)

            # Faceting just means doing an additional groupby. The
            # dimensions of the plot remain the same
            if self.facets:
                # the current subplot in the axs and plots
                cntr = 0
                if len(self.facets)==2 and self.facet_type!="wrap":
                    # store the extreme x and y coordinates of each pair of axes
                    axis_extremes = np.zeros(shape=(self.n_high * self.n_wide, 4))
                    xlab_offset = .15
                    for iter, (facets, frame) in enumerate(self.data.groupby(self.facets)):
                        pos = self.facet_pairs.index(facets) + 1
                        plt.subplot(self.n_wide, self.n_high, pos)
                        for layer in self._get_layers(frame):
                            for geom in self.geoms:
                                callbacks = geom.plot_layer(layer)
                        axis_extremes[iter] = [min(plt.xlim()), max(plt.xlim()),
                            min(plt.ylim()), max(plt.ylim())]
                    # find the grid wide data extremeties
                    xlab_min, ylab_min = np.min(axis_extremes, axis=0)[[0,2]]
                    xlab_max, ylab_max = np.max(axis_extremes, axis=0)[[1,3]]
                    # position of vertical labels for facet grid
                    xlab_pos = xlab_max + xlab_offset
                    ylab_pos = ylab_max - float(ylab_max-ylab_min)/2
                    # This needs to enumerate all possibilities
                    for pos, facets in enumerate(self.facet_pairs):
                        pos += 1
                        if pos <= self.n_high:
                            plt.subplot(self.n_wide, self.n_high, pos)
                        for layer in self._get_layers(frame):
                            for geom in self.geoms:
                                callbacks = geom.plot_layer(layer)
                        axis_extremes[iter] = [min(plt.xlim()), max(plt.xlim()),
                            min(plt.ylim()), max(plt.ylim())]
                    # find the grid wide data extremeties
                    xlab_min, ylab_min = np.min(axis_extremes, axis=0)[[0,2]]
                    xlab_max, ylab_max = np.max(axis_extremes, axis=0)[[1,3]]
                    # position of vertical labels for facet grid
                    xlab_pos = xlab_max + xlab_offset
                    ylab_pos = ylab_max - float(ylab_max-ylab_min)/2
                    # This needs to enumerate all possibilities
                    for pos, facets in enumerate(self.facet_pairs):
                        pos += 1
                        if pos <= self.n_high:
                            plt.subplot(self.n_wide, self.n_high, pos)
                            plt.table(cellText=[[facets[1]]], loc='top',
                                    cellLoc='center', cellColours=[['lightgrey']])
                        if (pos % self.n_high)==0:
                            plt.subplot(self.n_wide, self.n_high, pos)
                            x = max(plt.xticks()[0])
                            y = max(plt.yticks()[0])
                            ax = axs[pos % self.n_high][pos % self.n_wide]
                            plt.text(xlab_pos, ylab_pos, facets[0],
                                bbox=dict(
                                    facecolor='lightgrey',
                                    edgecolor='black',
                                    color='black',
                                    width=mpl.rcParams['font.size']*1.65
                                ),
                                fontdict=dict(rotation=-90, verticalalignment="center", horizontalalignment='left')
                            )

                    plt.subplot(self.n_wide, self.n_high, pos)
                    # Handle the different scale types here
                    # (free|free_y|free_x|None) and also make sure that only the
                    # left column gets y scales and the bottom row gets x scales
                    scale_facet_grid(self.n_wide, self.n_high,
                            self.facet_pairs, self.facet_scales)

                else:
                    for facet, frame in self.data.groupby(self.facets):
                        for layer in self._get_layers(frame):
                            for geom in self.geoms:
                                if self.facet_type=="wrap":
                                    if cntr+1 > len(plots):
                                        continue
                                    pos = plots[cntr]
                                    if pos is None:
                                        continue
                                    y_i, x_i = pos
                                    pos = x_i + y_i * self.n_high + 1
                                    plt.subplot(self.n_wide, self.n_high, pos)
                                else:
                                    plt.subplot(self.n_wide, self.n_high, cntr)
                                    # TODO: this needs some work
                                    if (cntr % self.n_high)==-1:
                                        plt.tick_params(axis='y', which='both',
                                                bottom='off', top='off',
                                                labelbottom='off')
                                callbacks = geom.plot_layer(layer)
                                if callbacks:
                                    for callback in callbacks:
                                        fn = getattr(axs[cntr], callback['function'])
                                        fn(*callback['args'])
                        title = facet
                        if isinstance(facet, tuple):
                            title = ", ".join(facet)
                        plt.table(cellText=[[title]], loc='top',
                                cellLoc='center', cellColours=[['lightgrey']])
                        cntr += 1

                    # NOTE: Passing n_high for cols (instead of n_wide) and
                    # n_wide for rows because in all previous calls to
                    # plt.subplot, n_wide is passed as the number of rows, not
                    # columns.
                    scale_facet_wrap(self.n_wide, self.n_high, range(cntr), self.facet_scales)
            else:
                for layer in self._get_layers(self.data):
                    for geom in self.geoms:
                        plt.subplot(1, 1, 1)
                        callbacks = geom.plot_layer(layer)
                        if callbacks:
                            for callback in callbacks:
                                fn = getattr(axs, callback['function'])
                                fn(*callback['args'])

            # Handling the details of the chart here; probably be a better
            # way to do this...
            if self.title:
                plt.title(self.title)
            if self.xlab:
                if self.facet_type=="grid":
                    fig.text(0.5, 0.025, self.xlab)
                else:
                    plt.xlabel(self.xlab)
            if self.ylab:
                if self.facet_type=="grid":
                    fig.text(0.025, 0.5, self.ylab, rotation='vertical')
                else:
                    plt.ylabel(self.ylab)
            if self.xmajor_locator:
                plt.gca().xaxis.set_major_locator(self.xmajor_locator)
            if self.xtick_formatter:
                plt.gca().xaxis.set_major_formatter(self.xtick_formatter)
                fig.autofmt_xdate()
            if self.xbreaks: # xbreaks is a list manually provided
                plt.gca().xaxis.set_ticks(self.xbreaks)
            if self.xtick_labels:
                plt.gca().xaxis.set_ticklabels(self.xtick_labels)
            if self.ytick_formatter:
                plt.gca().yaxis.set_major_formatter(self.ytick_formatter)
            if self.xlimits:
                plt.xlim(self.xlimits)
            if self.ylimits:
                plt.ylim(self.ylimits)
            if self.scale_y_reverse:
                plt.gca().invert_yaxis()
            if self.scale_x_reverse:
                plt.gca().invert_xaxis()

            # TODO: Having some issues here with things that shouldn't have a legend
            # or at least shouldn't get shrunk to accomodate one. Need some sort of
            # test in place to prevent this OR prevent legend getting set to True.
            if self.legend:
                if self.facets:
                    ax = axs[0][self.n_wide - 1]
                    box = ax.get_position()
                    ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
                else:
                    box = axs.get_position()
                    axs.set_position([box.x0, box.y0, box.width * 0.8, box.height])
                    ax = axs
                
                cntr = 0
                for ltype, legend in self.legend.items():
                    lname = self.aesthetics.get(ltype, ltype)
                    new_legend = draw_legend(ax, legend, ltype, lname, cntr)
                    ax.add_artist(new_legend)
                    cntr += 1

            # Finaly apply any post plot callbacks (theming, etc)
            if self.theme_applied:
                for ax in plt.gcf().axes:
                    self._apply_post_plot_callbacks(ax)
            else:
                for ax in plt.gcf().axes:
                    _theme_grey_post_plot_callback(ax)

        return plt.gcf()

    def _get_layers(self, data=None):
        # This is handy because... (something to do w/ facets?)
        if data is None:
            data = self.data
        # We want everything to be a DataFrame. We're going to default
        # to key to handle items where the user hard codes a aesthetic
        # (i.e. alpha=0.6)
        mapping = pd.DataFrame({
            ae: data.get(key, key)
                for ae, key in self.aesthetics.items()
        })
        if "color" in mapping:
            mapping['color'] = data['color_mapping']
        if "size" in mapping:
            mapping['size'] = data['size_mapping']
        if "shape" in mapping:
            mapping['marker'] = data['shape_mapping']
            del mapping['shape']
        if "linestyle" in mapping:
            mapping['linestyle'] = data['linestyle_mapping']

        # Default the x and y axis labels to the name of the column
        if "x" in self.aesthetics and self.xlab is None:
            self.xlab = self.aesthetics['x']
        if "y" in self.aesthetics and self.ylab is None:
            self.ylab = self.aesthetics['y']

        # Automatically drop any row that has an NA value
        mapping = mapping.dropna()

        discrete_aes = [ae for ae in self.DISCRETE if ae in mapping]
        layers = []
        if len(discrete_aes)==0:
            frame = mapping.to_dict('list')
            layers.append(frame)
        else:
            for name, frame in mapping.groupby(discrete_aes):
                frame = frame.to_dict('list')
                for ae in self.DISCRETE:
                    if ae in frame:
                        frame[ae] = frame[ae][0]
                layers.append(frame)

        return layers
        
    def _apply_post_plot_callbacks(self, axis):
        for cb in self.post_plot_callbacks:
            cb(axis)
