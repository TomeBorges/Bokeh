#!/usr/bin/python

import pandas as pd

from zigzag import * 

from math import pi
from bokeh.plotting import figure, show, output_file
from bokeh.models import ColumnDataSource, HoverTool

def Bokeh(df_ohlc, pivots, dfZ, FileLocation):	#FileLocation to be added as a title
	#Reset the index to remove Date column from index
	df_ohlc = df_ohlc.reset_index()

	#Renaming columns
	df_ohlc.columns = ["index","Date","Open","High",'Low',"Close","Volume"]
	df_ohlc["Date"] = pd.to_datetime(df_ohlc["Date"])

	inc = df_ohlc.Close > df_ohlc.Open #Bullish entrances
	dec = df_ohlc.Open > df_ohlc.Close #Bearish entrances

	width = (df_ohlc["Date"][1] - df_ohlc["Date"][0]).total_seconds() *1000 # Time difference in miliseconds between each entry on pandas DataFrame
	
	#use ColumnDataSource to pass in data for tooltips (HoverTool)
	sourceInc=ColumnDataSource(ColumnDataSource.from_df(df_ohlc.loc[inc]))
	sourceDec=ColumnDataSource(ColumnDataSource.from_df(df_ohlc.loc[dec]))

	TOOLS = "box_zoom,pan,wheel_zoom,reset"
	p = figure(x_axis_type="datetime", tools=TOOLS, plot_width=1200, title = FileLocation.strip('.csv'))

	p.xaxis.major_label_orientation = pi/4
	p.grid.grid_line_alpha = 0.4

	# Up and down Tail
	p.segment('Date', 'High', 'Date', 'Low', color="black", source=sourceInc)
	r1 = p.vbar('Date', width, 'Open', 'Close', fill_color="#7BE61D", line_color="black", source=sourceInc) #Bullish entrances
	r2 = p.vbar('Date', width, 'Open', 'Close', fill_color="#F2583E", line_color="black", source=sourceDec) #Bearish entrances

	# Bokeh format types referenced in: https://bokeh.pydata.org/en/latest/docs/reference/models/formatters.html
	# the values for the tooltip come from ColumnDataSource
	hover = HoverTool(
	    tooltips=[
	        ("Date", "@Date{%F %T}"), #Format: %Y-%M-%D %h:%m:%s
	        ("Open", "@Open"),
	        ("Close", "@Close"),
	        ("High", "@High"),
	        ("Low", "@Low"),
	        ("Volume", "@Volume{'0,0.0[000]'}"),
	    ],
	    formatters={
        'Date'      : 'datetime', # use 'datetime' formatter for 'date' field
    	},
    	mode='vline',
    	renderers=[r1,r2] # Added so hovertool only appears on top of candle-bar. Not on candlesticks or ZigZag's circles
	)
	p.add_tools(hover)

	# ZigZag Algorithm Start -------------------------
	p.line(dfZ.Time[pivots != 0], dfZ.Close[pivots != 0], color='#0E96EE', legend='ZigZag Algorithm')	
	p.circle((dfZ.Time [pivots == 1]).tolist(), dfZ.Close[pivots == 1], color="#7BE61D", fill_alpha=0.2, size=7, legend='ZigZag Algorithm') #Top
	p.circle((dfZ.Time [pivots == -1]).tolist(), dfZ.Close[pivots == -1], color="#F2583E", fill_alpha=0.2, size=7, legend='ZigZag Algorithm') #Bottom
	
	p.legend.location = "top_left"
	p.legend.click_policy = "hide" #If clicked on legend, all elements with the parameter {legend='ZigZag Algorithm'} will be hiden
	# ZigZag Algorithm End ---------------------------


	output_file( 'HTMLs/' + FileLocation.strip('.csv') + ".html", title = FileLocation.strip('.csv') + ' Candlesticks')
	show(p)  # open a browser


def main():

	FileLocation = 'TRXETH.csv'
	df = pd.read_csv('Data/' + FileLocation, sep=',')

	# Column names received from Binance. Column names may differ!
	new = df[['Open time', 'Open', 'High', 'Low', 'Close', 'Volume']].copy()
	new["Open time"] = pd.to_datetime(new["Open time"],format = '%Y-%m-%d %H:%M:%S')
	
	# ZigZag Algorithm Start -------------------------
	# ZigZag Pivots
	dfZ = new['Close'].as_matrix()
	pivots = peak_valley_pivots(dfZ, 0.1, -0.1)
	
	# Dataframe containing Pivots and Close (value) synced with the Date for the ZigZag algorithm
	dfZ = pd.DataFrame({'Pivots':pivots})
	dfZ['Time'] = new["Open time"]
	dfZ['Close'] = new['Close']
	# ZigZag Algorithm End ---------------------------


	#Function to plot the dataframe (candesticks) and the ZigZag algorithm (pivots)
	Bokeh(new, pivots, dfZ, FileLocation)
	
main()
