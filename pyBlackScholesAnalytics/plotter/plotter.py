"""
Author: Gabriele Pompa (gabriele.pompa@gmail.com)

Date: 20-May-2020
File name: plotter.py
"""

# ----------------------- standard imports ---------------------------------- #
# for NumPy arrays
import numpy as np

# for Pandas Series and DataFrame
import pandas as pd

# for Matplotlib plotting
import matplotlib.pyplot as plt

# for 3D plot
from mpl_toolkits.mplot3d import Axes3D

# ----------------------- sub-modules imports ------------------------------- #

from utils.utils import *

#-----------------------------------------------------------------------------#

class Plotter:
    """
    Interface Plotter class to plot the price/P&L of options or portfolio of options. It implements a composition with 
    an underlying `FinancialObject` object to access option-/portfolio-specific attributes. This class is not meant to be 
    instantiated. 
    
    Attributes:
    -----------
        FinancialObject (EuropeanOption sub-class or Portfolio):      Instance of an EuropeanOption sub-class 
                                                                      (PlainVanillaOption or DigitalOption) or a Portfolio 
                                                                      class.
        x_axis (np.ndarray):                                          An array representing the x-axis of the plot.
        time_parameter (single or Iterable date or time-to-maturity): A single value or Iterable object representing the
                                                                      time(s)-to-maturity or valuation date(s) at which the
                                                                      plot has to be made.
        title_label (String):                                         String representing the plot title. From .get_info()
                                                                      and .get_mkt_info() of FinancialInstrument.
    
    Public Methods:
    --------   
    
        getters for all attributes
        
        x_axis utility method to set x-axis
        
        time_parameter utility method to discriminate between single or Iterable time_parameter.
        
        parse_plot_metrics utility method to parse 'plot_metrics' optional parameter of .plot() method.
        
        parse_plot_details utility method to parse 'plot_details' optional parameter of .plot() method.
        
        plot:
            Public method to plot the price/P&L of the FinancialObject. It raises a NotImplementedError if called.

    """
    
    def __init__(self, FinancialObject):
        
        print("Calling the Plotter initializer!")
        
        # parse informations from FinancialInstrument
        self.fin_inst = FinancialObject
        self.__title_label = self.fin_inst.get_info() + "\n" + "Market at emission: " + self.fin_inst.get_mkt_info()

        # set default x-axis 
        self.__x_axis = self.x_axis(self.fin_inst.get_K())

        # set default time parameter
        self.__time_parameter, _ = self.time_parameter(self.fin_inst.get_tau())
               
    #
    # getters
    #
    
    def get_x_axis(self):
        return self.__x_axis

    def get_time_parameter(self):
        return self.__time_parameter

    def get_title(self):
        return self.__title_label
    
    #
    # utility methods
    #
    
    def x_axis(self, *args, **kwargs):
        """
        Utility method to define the x-axis of the plot, optionally parsing x-axis in input.
        """
        
        #
        # parsing optional parameters
        #
        
        x = None
        
        # case 1: x-axis = S
        if len(args) > 0 or 'S' in kwargs:
            x_name = 'S'
            if len(args) > 0:
                x = args[0]
            elif 'S' in kwargs:
                x = kwargs[x_name]
        
        # other cases
        else:
            # case 2: x-axis = K
            if 'K' in kwargs:
                x_name = 'K'
                x = kwargs[x_name]
            # case 3: x-axis = sigma
            elif 'sigma' in kwargs:
                x_name = 'sigma'
                x = kwargs[x_name]
            # case 4: x-axis = r
            elif 'r' in kwargs:
                x_name = 'r'
                x = kwargs[x_name]
            
        # case default: x-axis = S default
        if x is None:
            x_name = 'S'
            x = self.get_x_axis()[x_name]
        
        # granularity of the axis
        n = kwargs['n'] if 'n' in kwargs else 100
        
        #
        # defining the x-axis
        #
        
        # Case x-axis = S or K
        if x_name in ['S', 'K']:
            # case 1: a list of x-points in input. The x-axis is a wide range, including x-points
            if is_iterable(x):
                x_min = max(min(x)-20, 0.0)
                x_max = max(x)+20
            # case 2: a single x-point in input. The x-point is the middle point of the x-axis
            else:
                x_min = max(x-20, 0.0)
                x_max = x+20
                
        # Case x-axis = sigma or r
        elif x_name in ['sigma', 'r']:
            # case 1: a list of x-points in input. The x-axis is a wide range, including x-points
            if is_iterable(x):
                x_min = 0.0
                x_max = 1.5*max(x)
            # case 2: a single x-point in input. The x-point is the middle point of the x-axis
            else:
                x_min = 0.0
                x_max = 1.5*x

        return {x_name: np.linspace(x_min, x_max, n), 'x_axis': x_name}
        
    def time_parameter(self, *args, **kwargs):
        """
        Utility method to define the time parameter of the plot, optionally parsing time parameter in input.
        It returns appropriate time parameter labels too.
        """
        
        # parsing optional parameter: notice the backslash operator '\' 
        # to split code into multiple lines for readability
        time = args[0] if len(args) == 1 \
               else args[1] if len(args) > 1 \
                   else (kwargs['tau'] if 'tau' in kwargs \
                       else (kwargs['t'] if 't' in kwargs else self.get_time_parameter()))
        
        # case 1: time-to-maturity in input (if Iterable, sort from longest to shortest)
        if is_numeric(time):
            time_parameter = homogenize(time, reverse_order=True)

        # case 2: valuation date in input (if Iterable, sort from first to last, i.e. chronological order)
        elif is_date(time):
            time_parameter = homogenize(time, sort_func=date_string_to_datetime_obj)

        else:
            raise TypeError("Time parameter {} in input has not recognized data-type \
                             (only 'dd-mm-YYYY' Strings or dt.datetime objects allowed)".format(type(time_parameter)))
            
        # create time parameter label
        time_parameter_label = self.time_parameter_label(time_parameter)
        
        return time_parameter, time_parameter_label
    
    def time_parameter_label(self, time_parameter):
    
        if is_numeric(time_parameter):
            if is_iterable_not_string(time_parameter):
                return np.array([r"$\tau={:.2f}y$".format(tau) for tau in time_parameter])
            else:
                return r"$\tau={:.2f}y$".format(time_parameter)
            
        elif is_date(time_parameter):
            if is_iterable_not_string(time_parameter):
                return np.array([datetime_obj_to_date_string(t) for t in time_parameter])
            else:
                return datetime_obj_to_date_string(time_parameter)
            
    def add_time_tick_and_label(self, time_parameter, old_time_ticks, old_time_ticks_label):

        if is_numeric(time_parameter):
            
            # include zero time-to-maturity tick (that is, expiration)
            time_ticks = np.union1d(old_time_ticks, 0.0)            
            time_ticks = homogenize(time_ticks, reverse_order=True)
            
            # include zero time-to-maturity tick label
            time_ticks_label = np.union1d(old_time_ticks_label, r"$\tau=0.00y$")
            time_ticks_label = homogenize(time_ticks_label, reverse_order=True)
            
        elif is_date(time_parameter):
            
            # in case of multi-horizon portfolio, 
            # only the most recent expiration date is added
            T = self.fin_inst.get_T()
            expiration_date = T[0] if is_iterable_not_string(T) else T
            
            # convert to numeric representation
            expiration_date_numeric = date_to_number(expiration_date)   
            
            # include expiration date to ticks
            time_ticks = np.union1d(old_time_ticks, expiration_date_numeric)
            
            # include expiration date to tick labels
            old_time_ticks_label = np.union1d(old_time_ticks_label, datetime_obj_to_date_string(expiration_date))
            time_ticks_label = homogenize(old_time_ticks_label, sort_func=date_string_to_datetime_obj)
        
        return time_ticks, time_ticks_label
                            
    def parse_plot_metrics(self, **kwargs):
        """
        Utility method to parse the metrics of the plot: either 'price' or 'PnL'.
        """
        plot_metrics = kwargs['plot_metrics'] if 'plot_metrics' in kwargs else 'price'
        return plot_metrics
    
    def parse_plot_details(self, **kwargs):
        """
        Utility method to decide whether to plot details or not.
        """
        plot_details = kwargs['plot_details'] if 'plot_details' in kwargs else False
        return plot_details
     
    def parse_surf_plot(self, **kwargs):
        """
        Utility method to decide whether to plot multi-line or surface.
        """
        surf_plot = kwargs['surf_plot'] if 'surf_plot' in kwargs else False
        return surf_plot
    
    def parse_surf_plot_view(self, **kwargs):
        """
        Utility method to set the elevation and azimutal angles of the surface view.
        """
        view = kwargs['view'] if 'view' in kwargs else (30, -60)
        return view

    def make_dense(self, time, n=100):
        """
        Utility method to densify a time-parameter parameter.
        """
        if is_numeric(time):
            
            # define a dense grid of times-to-maturity
            time_dense = np.linspace(0.0, max(time), n)
            
            # include the requested times-to-maturity
            time_dense = np.union1d(time_dense, time)
            
            return homogenize(time_dense, reverse_order=True)
        
        elif is_date(time):
            
            # in case of multi-horizon portfolio, 
            # only the most recent expiration date is added
            T = self.fin_inst.get_T()
            expiration_date = T[0] if is_iterable_not_string(T) else T
            
            # include expiration date to valuation dates
            time = np.union1d(time, expiration_date)

            # define a dense grid of times-to-maturity
            time_dense = pd.date_range(start=min(time, key=date_string_to_datetime_obj), 
                                       end=max(time, key=date_string_to_datetime_obj),# - pd.Timedelta(days=10), 
                                       periods=n)
            
            # include the requested dates
            time_dense = time_dense.union(pd.DatetimeIndex(time))

            return homogenize(time_dense, sort_func=date_string_to_datetime_obj)
                
    #
    # Public methods
    # 
    
    def plot(self, *args, **kwargs):
        """
        Plotter class public plotting method. Usage example: 
            - example_options_plot.py
            - example_bull_spread.py
            - example_calendar_spread.py
            
        Can be called using (underlying, 
                             time-parameter, 
                             plot-metrics, 
                             plot-details, 
                             surf_plot, 
                             view), where:

        - underlying can be specified either as the 1st positional argument or as keyboard argument 'S'. 
          It's value can be:
        
            - Empty: the option's or portfolio's strike price(s) used as middle point(s) of the x-axis,
            - A number (e.g. S=100),
            - A List of numbers
            
        - time-parameter can be specified either as the 1st positional argument (if no underlying is specified) or
          as the 2nd positional argument or as keyboard argument 't' or 'tau'. 
          It's value can be:
        
            - Empty: .get_tau() is used,
            - A single (e.g. t='15-05-2020') / Iterable (e.g. pd.date_range) valuation date(s): 
              accepted types are either a 'dd-mm-YYYY' String or a dt.datetime object
            - A single (e.g. tau=0.5) / Iterable time-to-maturity value(s) 
            
        - plot-metrics can be specified as keyboard argument 'plot_metrics'. It's value can be:
        
            - Empty: default value used is 'price'
            - plot_metrics = a String 'method' corresponding to a valid '.method()' implemented by self.fin_inst object  
            
        - plot-details can be specified as keyboard argument 'plot_details'. It's value can be:
        
            - Empty: default value used is False
            - plot_details = True or False
        
          If True, we distinguish between the single-option (a) and portfolio (b) cases:
        
            a) Single-option case: upper and lower price boundaries are shown if .plot_single_time() method is called. 
            b) Portfolio case: constituent instruments' details are shown if .plot_single_time() method is called.
        
        - surf-plot can be specified as keyboard argument 'surf_plot'. It's value can be:
            
            - Empty: default value used is False
            - surf_plot = True or False
            
          If True, .plot_surf() is called in case of Iterable time-parameter, 
          otherwise .plot_multi_time() is called.
        
        - view can be specified as keyboard argument 'view'. It's value can be:
            
            - Empty: default value used is (30, -60)
            - surf_plot = Tuple of two numbers
            
          It represent the pair of (elevation angle, azimutal angle) of the plot view
          in case .plot_surf() is called.
        """
        
        # argument parsing and plot setup
        x_axis = self.x_axis(*args, **kwargs)
        time_parameter, time_label_parameter = self.time_parameter(*args, **kwargs)
        plot_metrics = self.parse_plot_metrics(**kwargs)
        surf_plot = self.parse_surf_plot(**kwargs)

        if is_iterable_not_string(time_parameter) and not surf_plot:
            self.plot_multi_time(x_axis, time_parameter, time_label_parameter, plot_metrics)
        elif is_iterable_not_string(time_parameter):
            plot_view = self.parse_surf_plot_view(**kwargs)
            self.plot_surf(x_axis, time_parameter, time_label_parameter, plot_metrics, plot_view)
        else:
            plot_details = self.parse_plot_details(*args, **kwargs)
            self.plot_single_time(x_axis, time_parameter, time_label_parameter, plot_metrics, plot_details)
            
#-----------------------------------------------------------------------------#

class OptionPlotter(Plotter):
    """
    Plotter class to plot the price/P&L of single options. Inherits from Plotter base-class.
    It implements a composition with an underlying `PlainVanillaOption` or `DigitalOption` object to access 
    option-specific attributes.
    
    Attributes:
    -----------
    
        public attributes inherited from Plotter class
    
    Public Methods:
    --------   
    
        public methods inherited from Plotter class
        
        plot_surf:
            Plot FinancialInstrument values as a surface of underlying value(s) and multiple dates.

        plot_multi_time:
            Plot FinancialInstrument values against underlying value(s), possibly at multiple dates.
        
        plot_single_time:
            Plot FinancialInstrument values against underlying value(s) at fixed date. 
    """
    
    def __init__(self, *args, **kwargs):
        # calling the Plotter initializer
        super(OptionPlotter, self).__init__(*args, **kwargs)
                                                                
    def plot_surf(self, x_axis_dict, times, time_labels, plot_metrics, view):
        """
        Plot FinancialInstrument values as a surface of underlying value(s) and multiple dates.
        """
        
        # identifier of the x-axis
        x_id = x_axis_dict.pop('x_axis', 'x-id not found')
        if x_id not in ["S", "K"]:
            raise NotImplementedError(".plot_surf() availabe only for S or K x-axis variables. Given: " + x_id)
        
        # x-axis values
        x = x_axis_dict[x_id]

        # number of times-to-maturity considered
        n_times = len(times)
        plt.rcParams["axes.prop_cycle"] = plt.cycler("color", plt.cm.Blues(np.linspace(0,1,n_times)))

        # define the figure
        fig = plt.figure(figsize=(15,10))
        ax = fig.gca(projection='3d')
        
        # define a dense grid of times
        # in case of dates: from the most recent valuation date to expiration date
        # in case of times-to-maturity: from the biggest tau to 0 (that is, expiration)
        times_dense = self.make_dense(times)
        n_times_dense = len(times_dense)

        # if times are dates, we convert into their numeric representation. This is needed for plotting
        times_numeric = date_to_number(times)
        times_dense_numeric = date_to_number(times_dense)
        
        # precompute surface (exploiting vectorization)
        surface_metrics = getattr(self.fin_inst, plot_metrics)(**{x_id: x, 't': times_dense}, np_output=False)
                
        # grid points, if needed convert dates to numeric representation for plotting
        x_axis_grid, time_grid = np.meshgrid(surface_metrics.columns, times_dense_numeric)
                
        # surface plot
        surf = ax.plot_surface(x_axis_grid, time_grid, surface_metrics.values.astype('float64'), rstride=2, cstride=2,
                               cmap=plt.cm.Blues, linewidth=0.5, antialiased=True, zorder=1)
                
        # plot the price for different underlying values, one line for each different date
        plt.gca().set_prop_cycle(None)
        for i in range(n_times):
            ax.plot(x, np.repeat(times_numeric[i], repeats=len(x)), surface_metrics.loc[times[i],:], '-', lw=1.5, 
                    label=time_labels[i], zorder=1+i+1)
            
        # precompute emission level metrics (exploiting vectorization)
        if x_id == 'S':
            x_emission = self.fin_inst.get_S()
        elif x_id == 'K':
            x_emission = self.fin_inst.get_K()
        elif x_id == 'sigma':
            x_emission = self.fin_inst.get_sigma()
        elif x_id == 'r':
            x_emission = self.fin_inst.get_r()
        
        emission_metrics = getattr(self.fin_inst, plot_metrics)(**{x_id: x_emission, 't': times})
        emission_metrics_dense = getattr(self.fin_inst, plot_metrics)(**{x_id: x_emission, 't': times_dense})

        # blue dot at original underlying level for reference
        ax.plot(x_emission + np.zeros(n_times), times_numeric, emission_metrics, 'b.', ms=10, 
                label=r"Emission level $" + x_id + r"={:.2f}$".format(x_emission), zorder=1+i+2)
        ax.plot(x_emission + np.zeros(n_times_dense), times_dense_numeric, emission_metrics_dense, 'b--', lw=1.5, zorder=1+i+2)

        # plot the red payoff line for different underlying values
        if plot_metrics in ['price', 'PnL']:
            ax.plot(x, np.repeat(times_dense_numeric[-1], repeats=len(x)), getattr(self.fin_inst, plot_metrics)(x_axis_dict,tau=0.0), 'r-',  lw=1.5, 
                    label=plot_metrics + r" at maturity (" + self.fin_inst.get_docstring('payoff') + r")", zorder=1+i+3)
        
        # plot a dot to highlight the strike position and a reference zero line
        ax.plot(np.array([self.fin_inst.get_K()]), np.array([times_dense_numeric[-1]]), np.array([0.0]), 'k.', ms=15, 
                label="Strike $K={}$".format(self.fin_inst.get_K()), zorder=1+i+4)
        ax.plot(self.fin_inst.get_K() + np.zeros(n_times_dense), times_dense_numeric, np.zeros_like(times_dense), 'k--', lw=1.5, zorder=1+i+5)
                
        # include expiraton time tick
        times_numeric, time_labels = self.add_time_tick_and_label(time_parameter=times, 
                                                                  old_time_ticks=times_numeric, 
                                                                  old_time_ticks_label=time_labels)
        
        # set y ticks
        ax.set_yticks(times_numeric)
        ax.set_yticklabels(time_labels)
        
        # set axis labels 
        ax.set_xlabel(x_id, fontsize=12) 
        ax.set_ylabel(r"Date" if is_date(times) else r"Time-to-Maturity", fontsize=12)        
        ax.set_zlabel('Black-Scholes {}'.format(plot_metrics), fontsize=12) 

        # set title
        ax.set_title(plot_metrics + " of a " + self.get_title(), fontsize=12) 

        # add the legend ('best' loc parameters places the legend in the best position automatically)
        ax.legend(loc='best', ncol=1)
        
        # add a gride to ease visualization
        plt.grid(True)

        # draw a colorbar for color-reference
        fig.colorbar(surf, orientation="horizontal",  shrink=0.5, aspect=10, pad=0.05)

        # set the plot view
        ax.view_init(view[0], view[1])
                
        # rotate view and invert y axis in case of dates 
        # for better perspective
        if is_date(times):
            ax.view_init(ax.elev, ax.azim+180)
            ax.invert_xaxis()
            
        # show the plot
        fig.tight_layout()
        plt.show()

    def plot_multi_time(self, x_axis_dict, times, time_labels, plot_metrics):
        """
        Plot FinancialInstrument values against underlying value(s), possibly at multiple dates.
        """
        
        # identifier of the x-axis
        x_id = x_axis_dict.pop('x_axis', 'x-id not found')
        if x_id not in ["S", "K"]:
            raise NotImplementedError(".plot_multi_time() availabe only for S or K x-axis variables. Given: " + x_id)
        
        # x-axis values
        x = x_axis_dict[x_id]
        
        # number of times-to-maturity considered
        n_times = len(times)

        plt.rcParams["axes.prop_cycle"] = plt.cycler("color", plt.cm.Blues(np.linspace(0,1,n_times)))

        # define the figure
        fig, ax = plt.subplots(figsize=(10,6))

        # precompute surface (exploiting vectorization)
        surface_metrics = getattr(self.fin_inst, plot_metrics)(**{x_id: x, 't': times})
            
        # plot the price for different x-axis values, one line for each different date
        for i in range(n_times):
            ax.plot(x, surface_metrics[i,:], '-', lw=1.5, label=time_labels[i])
            
        # precompute emission level metrics (exploiting vectorization)
        if x_id == 'S':
            x_emission = self.fin_inst.get_S()
        elif x_id == 'K':
            x_emission = self.fin_inst.get_K()
        elif x_id == 'sigma':
            x_emission = self.fin_inst.get_sigma()
        elif x_id == 'r':
            x_emission = self.fin_inst.get_r()
        
        emission_metrics = getattr(self.fin_inst, plot_metrics)(**{x_id: x_emission, 't': times})

        # blue dot at original emission level of the x-axis for reference
        ax.plot(x_emission + np.zeros_like(emission_metrics), emission_metrics, 'b.', ms=10,\
                label=r"Emission level $" + x_id + r"={:.2f}$".format(x_emission))
            
        # plot the red payoff line for different x-axis values
        if plot_metrics in ['price', 'PnL']:
            ax.plot(x, getattr(self.fin_inst, plot_metrics)(**{x_id: x, 'tau': 0.0}), 'r-',  lw=1.5, 
                    label=plot_metrics + r" at maturity (" + self.fin_inst.get_docstring('payoff') + r")")
        
        # plot a dot to highlight the strike position and a reference zero line
        ax.plot(self.fin_inst.get_K(), 0, 'k.', ms=15, label="Strike $K={}$".format(self.fin_inst.get_K()))
        ax.plot(x, np.zeros_like(x), 'k--', lw=1.5)
        
        # set axis labels 
        ax.set_xlabel(x_id + r" at different dates", fontsize=12)
        ax.set_ylabel('Black-Scholes {}'.format(plot_metrics), fontsize=12) 

        # set title
        ax.set_title(plot_metrics + " of a " + self.get_title(), fontsize=12) 

        # add the legend ('best' loc parameters places the legend in the best position automatically)
        ax.legend(loc='best', ncol=2)

        # add a gride to ease visualization
        plt.grid(True)

        # show the plot
        fig.tight_layout()
        plt.show()
 
    def plot_single_time(self, x_axis_dict, time, time_label, plot_metrics, plot_price_limits):
        """
        Plot FinancialInstrument values against underlying value(s) at fixed date. 
        """
        
        # identifier of the x-axis
        x_id = x_axis_dict.pop('x_axis', 'x-id not found')
        
        # x-axis values
        x = x_axis_dict[x_id]

        # define the figure
        fig, ax = plt.subplots(figsize=(10,6))
        
        # plot the price for different x-axis values
        ax.plot(x, getattr(self.fin_inst, plot_metrics)(**{x_id: x, 't': time}), 'b-', lw=1.5, 
                label=time_label)
        
        # precompute emission level metrics (exploiting vectorization)
        if x_id == 'S':
            x_emission = self.fin_inst.get_S()
        elif x_id == 'K':
            x_emission = self.fin_inst.get_K()
        elif x_id == 'sigma':
            x_emission = self.fin_inst.get_sigma()
        elif x_id == 'r':
            x_emission = self.fin_inst.get_r()
        
        emission_metric = getattr(self.fin_inst, plot_metrics)(**{x_id: x_emission, 't': time})

        # blue dot at original emission level of the x-axis for reference
        ax.plot(x_emission, emission_metric, 'b.', ms=10,\
                label=r"Emission level $" + x_id + r"={:.2f}$".format(x_emission))
        
        # part meaningful only if the x-axis is 'S' or 'K'
        if x_id in ['S', 'K']:
            if plot_price_limits:
                # plot the upper limit, the price and the lower limit for different x-axis values
                ax.plot(x, self.fin_inst.price_upper_limit(**{x_id: x, 't': time}), 'k-.', lw=1.5, label=self.fin_inst.get_docstring('price_upper_limit'))
                ax.plot(x, self.fin_inst.price_lower_limit(**{x_id: x, 't': time}), 'k--', lw=1.5, label=self.fin_inst.get_docstring('price_lower_limit'))
    
            # plot the red payoff line for different x-axis values
            if plot_metrics in ['price', 'PnL']:
                ax.plot(x, getattr(self.fin_inst, plot_metrics)(**{x_id: x, 'tau': 0.0}), 'r-',  lw=1.5, 
                        label=plot_metrics + r" at maturity(" + self.fin_inst.get_docstring('payoff') + r")")
    
            # plot a dot to highlight the strike position and a reference zero line
            ax.plot(self.fin_inst.get_K(), 0, 'k.', ms=15, label="Strike $K={}$".format(self.fin_inst.get_K()))
            ax.plot(x, np.zeros_like(x), 'k--', lw=1.5)

        # set axis labels 
        ax.set_xlabel(x_id + r" at " + time_label, fontsize=12) 
        ax.set_ylabel('Black-Scholes {}'.format(plot_metrics), fontsize=12) 

        # set title
        ax.set_title(plot_metrics + " of a " + self.get_title(), fontsize=12) 

        # add the legend ('best' loc parameters places the legend in the best position automatically)
        ax.legend(loc='best', ncol=1)

        # add a gride to ease visualization
        plt.grid(True)

        # show the plot
        fig.tight_layout()
        plt.show()
        
#-----------------------------------------------------------------------------#

class PortfolioPlotter(Plotter):
    """
    Plotter class to plot the price/P&L of portfolio of options. Inherits from Plotter base-class.
    It implements a composition with an underlying `Portfolio` object to access portfolio-specific attributes.
    
    Attributes:
    -----------
    
        public attributes inherited from Plotter class
    
    Public Methods:
    --------   
    
        public methods inherited from Plotter class
        
        plot_surf:
            Plot Portfolio values as a surface of underlying value(s) and multiple dates.

        plot_multi_time:
            Plot Portfolio values against underlying value(s), possibly at multiple dates.
        
        plot_single_time:
            Plot Portfolio values against underlying value(s) at fixed date. 
    """
    
    def __init__(self, *args, **kwargs):
        # calling the Plotter initializer
        super(PortfolioPlotter, self).__init__(*args, **kwargs)
        
        # setting the color cycle to plot constituent instruments reference lines
        plt.rcParams["axes.prop_cycle"] = plt.cycler("color", plt.cm.RdYlGn_r(np.linspace(0,1,len(self.fin_inst.get_composition()))))

    def plot_surf(self, x_axis_dict, times, time_labels, plot_metrics, view):
        """
        Plot Portfolio values as a surface of underlying value(s) and multiple dates.
        """
        
        # identifier of the x-axis
        x_id = x_axis_dict.pop('x_axis', 'x-id not found')
        if x_id != 'S':
            raise NotImplementedError(".plot_surf() for Portfolios availabe only for S x-axis variable. Given: " + x_id)
        
        # x-axis values
        S = x_axis_dict[x_id]

        # number of times-to-maturity considered
        n_times = len(times)
        plt.rcParams["axes.prop_cycle"] = plt.cycler("color", plt.cm.Blues(np.linspace(0,1,n_times)))

        # define the figure
        fig = plt.figure(figsize=(15,10))
        ax = fig.gca(projection='3d')
        
        # define a dense grid of times
        # in case of dates: from the most recent valuation date to expiration date
        # in case of times-to-maturity: from the biggest tau to 0 (that is, expiration)
        times_dense = self.make_dense(times, n=500)
        n_times_dense = len(times_dense)

        # if times are dates, we convert into their numeric representation. This is needed for plotting
        times_numeric = date_to_number(times)
        times_dense_numeric = date_to_number(times_dense)
        
        # precompute surface (exploiting vectorization)
        surface_metrics = getattr(self.fin_inst, plot_metrics)(S, times_dense, np_output=False)
                
        # grid points, if needed convert dates to numeric representation for plotting
        underlying_grid, time_grid = np.meshgrid(surface_metrics.columns, times_dense_numeric)
                
        # surface plot
        surf = ax.plot_surface(underlying_grid, time_grid, surface_metrics.values.astype('float64'), rstride=2, cstride=2,
                               cmap=plt.cm.Blues, linewidth=0.5, antialiased=True, zorder=1)
                
        # plot the price for different underlying values, one line for each different date
        plt.gca().set_prop_cycle(None)
        for i in range(n_times):
            ax.plot(S, np.repeat(times_numeric[i], repeats=len(S)), surface_metrics.loc[times[i],:], '-', lw=1.5, 
                    label=time_labels[i], zorder=1+i+1)
            
        # precompute S_t level metrics (exploiting vectorization)
        S_t = self.fin_inst.get_S()
        S_t_level_metrics = getattr(self.fin_inst, plot_metrics)(S_t, times)
        S_t_level_metrics_dense = getattr(self.fin_inst, plot_metrics)(S_t, times_dense)

        # blue dot at original underlying level for reference
        ax.plot(S_t + np.zeros(n_times), times_numeric, S_t_level_metrics, 'b.', ms=10, 
                label=r"Emission level $S={:.1f}$".format(S_t), zorder=1+i+2)
        ax.plot(S_t + np.zeros(n_times_dense), times_dense_numeric, S_t_level_metrics_dense, 'b--', lw=1.5, zorder=1+i+2)

        # if defined, plot the red payoff line for different underlying values
        if not self.fin_inst.is_multi_horizon:
            # plot the red payoff line for different underlying values
            if plot_metrics in ['price', 'PnL']:
                ax.plot(S, np.repeat(times_dense_numeric[-1], repeats=len(S)), getattr(self.fin_inst, plot_metrics)(S,tau=0.0), 'r-',  lw=1.5, 
                        label=plot_metrics + r" at maturity", zorder=1+i+3)
            
        # plot a dot to highlight the strike position and a reference zero line
        for K in self.fin_inst.get_K():
            ax.plot(np.array([K]), np.array([times_dense_numeric[-1]]), np.array([0.0]), 'k.', ms=15, 
                    label="Strike $K={}$".format(K), zorder=1+i+4)
            ax.plot(K + np.zeros(n_times_dense), times_dense_numeric, np.zeros_like(times_dense), 'k--', lw=1.5, zorder=1+i+5)
                
        # include expiraton time tick
        times_numeric, time_labels = self.add_time_tick_and_label(time_parameter=times, 
                                                                  old_time_ticks=times_numeric, 
                                                                  old_time_ticks_label=time_labels)
        
        # set y ticks
        ax.set_yticks(times_numeric)
        ax.set_yticklabels(time_labels)
        
        # set axis labels 
        ax.set_xlabel(r"Underlying Value", fontsize=12) 
        ax.set_ylabel(r"Date" if is_date(times) else r"Time-to-Maturity", fontsize=12)        
        ax.set_zlabel('Black-Scholes {}'.format(plot_metrics), fontsize=12) 

        # set title
        ax.set_title(plot_metrics + " of a " + self.get_title(), fontsize=12) 

        # add the legend ('best' loc parameters places the legend in the best position automatically)
        ax.legend(loc='best', ncol=1)
        
        # add a gride to ease visualization
        plt.grid(True)

        # draw a colorbar for color-reference
        fig.colorbar(surf, orientation="horizontal",  shrink=0.5, aspect=10, pad=0.05)

        # set the plot view
        ax.view_init(view[0], view[1])
                
        # rotate view and invert y axis in case of dates 
        # for better perspective
        if is_date(times):
            ax.view_init(ax.elev, ax.azim+180)
            ax.invert_xaxis()
            
        # show the plot
        fig.tight_layout()
        plt.show()
        
    def plot_multi_time(self, x_axis_dict, times, time_labels, plot_metrics):
        """
        Plot Portfolio values against underlying value(s), possibly at multiple dates.
        """
        
        # identifier of the x-axis
        x_id = x_axis_dict.pop('x_axis', 'x-id not found')
        if x_id != 'S':
            raise NotImplementedError(".plot_multi_time() for Portfolios availabe only for S x-axis variable. Given: " + x_id)
        
        # x-axis values
        S = x_axis_dict[x_id]

        # number of times-to-maturity considered
        n_times = len(times)

        plt.rcParams["axes.prop_cycle"] = plt.cycler("color", plt.cm.Blues(np.linspace(0,1,n_times)))

        # define the figure
        fig, ax = plt.subplots(figsize=(10,6))

        # precompute surface (exploiting vectorization)
        surface_metrics = getattr(self.fin_inst, plot_metrics)(S, times)

        # plot the price for different underlying values, one line for each different date
        for i in range(n_times):
            ax.plot(S, surface_metrics[i,:], '-', lw=1.5, label=time_labels[i])
            
        # precompute S_t level metrics (exploiting vectorization)
        S_t = self.fin_inst.get_S()
        S_t_level_metrics = getattr(self.fin_inst, plot_metrics)(S_t, times)

        # blue dot at original underlying level for reference
        ax.plot(S_t + np.zeros_like(S_t_level_metrics), S_t_level_metrics, 'b.', ms=10, label=r"Emission level $S={:.1f}$".format(S_t))
            
        # if defined, plot the red payoff line for different underlying values
        if not self.fin_inst.is_multi_horizon:
            if plot_metrics == 'price':
                ax.plot(S, self.fin_inst.payoff(S), 'r-',  lw=1.5, label=r"Payoff at maturity")
            elif plot_metrics == 'PnL':
                ax.plot(S, self.fin_inst.PnL(S, tau=0.0), 'r-',  lw=1.5, label=r"PnL at maturity")
            else:
                pass
            
        # plot a dot to highlight the strike position and a reference zero line
        strikes = self.fin_inst.get_K()
        ax.plot(strikes, np.zeros_like(strikes), 'k.', ms=15, label="Strikes $K={}$".format(strikes))
        ax.plot(S, np.zeros_like(S), 'k--', lw=1.5)
        
        # set axis labels 
        ax.set_xlabel(r"Underlying Value at different dates", fontsize=12)
        ax.set_ylabel('Black-Scholes {}'.format(plot_metrics), fontsize=12) 

        # set title
        ax.set_title(plot_metrics + " of a " + self.get_title(), fontsize=12) 

        # add the legend ('best' loc parameters places the legend in the best position automatically)
        ax.legend(loc='best', ncol=2)

        # add a gride to ease visualization
        plt.grid(True)

        # show the plot
        fig.tight_layout()
        plt.show()
    
    def plot_single_time(self, x_axis_dict, time, time_label, plot_metrics, plot_instruments_metrics):
        """
        Plot Portfolio values against underlying value(s) at fixed date. 
        """
        
        # identifier of the x-axis
        x_id = x_axis_dict.pop('x_axis', 'x-id not found')
        
        # x-axis values
        x = x_axis_dict[x_id]

        # define the figure
        fig, ax = plt.subplots(figsize=(10,6))
        
        # plot the price for different x-axis values
        ax.plot(x, getattr(self.fin_inst, plot_metrics)(**{x_id: x, 't': time}), 'b-', lw=1.5, 
                label=time_label)
        
        # precompute emission level metrics (exploiting vectorization)
        if x_id == 'S':
            x_emission = self.fin_inst.get_S()
        elif x_id == 'K':
            x_emission = self.fin_inst.get_K()
        elif x_id == 'sigma':
            x_emission = self.fin_inst.get_sigma()
        elif x_id == 'r':
            x_emission = self.fin_inst.get_r()
        
        emission_metric = getattr(self.fin_inst, plot_metrics)(**{x_id: x_emission, 't': time})

        # blue dot at original emission level of the x-axis for reference
        ax.plot(x_emission, emission_metric, 'b.', ms=10,\
                label=r"Emission level $" + x_id + r"={:.2f}$".format(x_emission))
        
        # part meaningful only if the x-axis is 'S' or 'K'
        if x_id in ['S', 'K']:

            # plot the red payoff line for different x-axis values
            if (not self.fin_inst.is_multi_horizon) and plot_metrics in ['price', 'PnL']:
                ax.plot(x, getattr(self.fin_inst, plot_metrics)(**{x_id: x, 'tau': 0.0}), 'r-',  lw=1.5, 
                        label=plot_metrics + r" at maturity")
#                if plot_metrics == 'price':
#                    ax.plot(x, self.fin_inst.payoff(S), 'r-',  lw=1.5, label=r"Payoff at maturity")
#                elif plot_metrics == 'PnL':
#                    ax.plot(S, self.fin_inst.PnL(S, tau=0.0), 'r-',  lw=1.5, label=r"PnL at maturity")
#                else:
#                    pass
                
            # optionally, plot the instruments details
            if plot_instruments_metrics:
                # loop over instruments in portfolio
                for inst in self.fin_inst.get_composition():
                    position = inst["position"]
                    # discriminating between multi- and single-horizon portfolios
                    if self.fin_inst.is_multi_horizon:          
                        # plot_metrics at current time
                        ax.plot(x, position * getattr(inst["instrument"], plot_metrics)(**{x_id: x, 't': time}), '--', lw=1.5, 
                            label=plot_metrics + r" " + inst["info"] + r" at " + time_label)
                    else:
                        # plot_metrics at-maturity
                        ax.plot(x, position * getattr(inst["instrument"], plot_metrics)(**{x_id: x, 'tau': 0.0}), '--', lw=1.5, 
                            label=plot_metrics + r" " + inst["info"] + r" at maturity")
    
            # plot a dot to highlight the strike position and a reference zero line
            strikes = self.fin_inst.get_K()
            ax.plot(strikes, np.zeros_like(strikes), 'k.', ms=15, label="Strikes $K={}$".format(strikes))
            ax.plot(x, np.zeros_like(x), 'k--', lw=1.5)

        # set axis labels 
        ax.set_xlabel(x_id + r" at " + time_label, fontsize=12)
        ax.set_ylabel('Black-Scholes {}'.format(plot_metrics), fontsize=12) 

        # set title
        ax.set_title(plot_metrics + " of a " + self.get_title(), fontsize=12) 

        # add the legend ('best' loc parameters places the legend in the best position automatically)
        ax.legend(loc='best', ncol=1)

        # add a gride to ease visualization
        plt.grid(True)

        # show the plot
        fig.tight_layout()
        plt.show()
