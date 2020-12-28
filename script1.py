from flask import Flask, render_template, request, send_file # last 2 added for geocoder

# LINES ADDED FOR GEOCODER
import pandas
from werkzeug.utils import secure_filename
from geopy.geocoders import ArcGIS
import os
nom=ArcGIS()
# END OF ADDED LINES TO GEOCODER
app=Flask(__name__)

# LINES ADDED FOR GEOCODER
UPLOAD_FOLDER = './geocoder'
DOWNLOAD_FOLDER = './geocoder'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER
# END OF ADDED LINES TO GEOCODER

@app.route('/plot/')
def plot():
    from pandas_datareader import data
    import datetime
    from bokeh.plotting import figure, show, output_file
    from bokeh.embed import components
    from bokeh.resources import CDN

    start = datetime.datetime(2015,11,1)#the funcion requires a datetime parameter
    end = datetime.datetime(2016,3,10)

    df = data.DataReader(name="GOOG", data_source="yahoo", start=start, end=end)

    def inc_dec(c, o):
        if c > o:
            value = "Increase"
        elif c < o:
            value = "Decrease"
        else:
            Value = "Equal"
        return value

    df["Status"]=[inc_dec(c,o) for c, o in zip(df.Close,df.Open)]

    df["Middle"] = (df.Open + df.Close)/2
    df["Height"] = abs(df.Close-df.Open)

    p=figure(x_axis_type='datetime', width=1000, height=300, sizing_mode="scale_width")

    p.title.text="Candlestick Chart"

    p.grid.grid_line_alpha=0.3 #alpha means the level of transparency

    hours_12 = 12*60*60*1000

    p.segment(df.index, df.High, df.index, df.Low, color="black")

    p.rect(df.index[df.Status=="Increase"], df.Middle[df.Status=="Increase"],
           hours_12, df.Height[df.Status=="Increase"], fill_color="#CCFFFF", line_color="black")

    p.rect(df.index[df.Status=="Decrease"], df.Middle[df.Status=="Decrease"],
           hours_12, df.Height[df.Status=="Decrease"], fill_color="#FF3333", line_color="black")

    script1, div1 = components(p)

    cdn_js=CDN.js_files[0]

    return render_template('plot.html', script1=script1, div1=div1, cdn_js=cdn_js)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about/')
def about():
    return render_template('about.html')

# LINES ADDED FOR GEOCODER

@app.route("/geocoder/")
def geocoder():
    return render_template("geocoder.html")

@app.route("/success", methods=['POST'])
def success():
    global file
    if request.method=='POST':
        file=request.files["file"]
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename("uploaded_file.xlsx")))
        df = pandas.read_excel("./geocoder/uploaded_file.xlsx")
        df["Complete Add"] = df["Address"]+", "+ df["City"]+", " + df["State"]+", "+ str(df["ZIP"])+", " + df["Country"]
        df["Coordinates"]=df["Complete Add"].apply(nom.geocode)
        df["Latitude"]=df["Coordinates"].apply(lambda x: x.latitude)
        df["Longitude"]=df["Coordinates"].apply(lambda x: x.longitude)
        del df['Coordinates']
        del df['Complete Add']
        df.to_excel('./geocoder/addresses_w_coordinates.xlsx')

        return render_template("index.html", btn = "download.html")

@app.route("/download.html")

def download():
    return send_file("./geocoder/addresses_w_coordinates.xlsx", attachment_filename="yourfile.xlsx", as_attachment=True)
    return render_template("geocoder.html")
# END OF ADDED LINES TO GEOCODER

if __name__=="__main__":
    app.run(debug=True)
