from flask import request,render_template,Flask,send_file
import os 
from main import *
import logging
from io import BytesIO
#from config_gen import gen
from authentication import local_authentication




app = Flask(__name__)


logging.basicConfig(filename="logs.log",
                    format='%(asctime)s %(message)s',
                    filemode='a+')


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def send_file_remove(file,source=None):
    with open (file,"r") as n:
        load_file=n.read()
    os.remove(file)
    if source:
        os.remove(source)
    loaded_file = BytesIO(load_file.encode('utf-8'))
    return loaded_file


@app.route("/")
def login():
    if request.args.get('internal'):
        logger.info(f"Login successfully Via local username : Django UI")
        return render_template("config_conversion.html")
    return render_template('login.html')

@app.route("/index",methods=['POST'])
def index():
    if request.method=="POST":
        if local_authentication(request.form["uname"],request.form["psw"]):
            logger.info(f"Login successfully Via local username : {request.form['uname']}")
            return render_template("config_conversion.html")
        else:
            return render_template ('login.html',msg="Login Failed")



@app.route("/Converter",methods=['POST'])
def input_file():
    if request.method=="POST":
        if request.form["Source_file"]=="HUAWEI-ANY" and request.form["destination_file"]=="NOKIA-7250-IXR":
            if request.files["input_file"]:
                file=request.files["input_file"]
                file.save(file.filename)
                try:
                    output = Huawei_To_Nokia(file.filename,city=request.form["City"])
                    if output == 1:
                        os.remove(file.filename)
                        return render_template("location_error.html")
                    else:
                        logger.info(f"successfully converted : {output} from {request.form['Source_file']} to {request.form['destination_file']}")
                        return send_file(send_file_remove(output,file.filename), mimetype='text/plain', as_attachment=True, download_name=output)
                except Exception as e:
                    os.remove(file.filename)
                    logger.info(f"Error occurred while processing {file.filename} and ERROR : {e}")
                    return render_template('FileError.html',Error_msg=e)


if __name__ == "__main__":
    
    app.run(host="0.0.0.0",port=8081)
