from flask import Flask, request, redirect, url_for, render_template, send_from_directory, flash, after_this_request
from werkzeug.utils import secure_filename
from secrets import token_hex
import requests

app = Flask(__name__)

auth_token = "auth_token"

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        post = False
        get = False
        delete = False

        original_id = request.form.get("original_id")
        signed_id = request.form.get("signed_id")
        pending_file_id = request.form.get("pending_file_id")
        template_id = request.form.get("template_id")
        signed_file_id = request.form.get("signed_file_id")
        rs_id = request.form.get("rs_id")

        # user
        if request.form["button"] == "Fetch User Details":
            url = "https://api.signeasy.com/v2.1/me/"
            get = True

        # originals
        if request.form["button"] == "List all originals":
            url = "https://api.signeasy.com/v2.1/original/"
            get = True
        if request.form["button"] == "Fetch details of an original":
            url = f"https://api.signeasy.com/v2.1/original/{original_id}/" # replace "original_id"
            get = True
        if request.form["button"] == "Download an original document":
            url = f"https://api.signeasy.com/v2.1/original/{original_id}/download" # replace "original_id"
            get = True
        if request.form["button"] == "Delete an original document":
            url = f"https://api.signeasy.com/v2.1/original/{original_id}" # replace "original_id"
            delete = True
        
        # embedded self sign
        if request.form["button"] == "Fetch all self signed files":
            url = "https://api.signeasy.com/v2.1/me/signed/"
            get = True
        if request.form["button"] == "Fetch details of self signed document":
            url = f"https://api.signeasy.com/v2.1/me/signed/{signed_id}" # replace "signed_id"
            get = True
        if request.form["button"] == "Download self signed document":
            url = f"https://api.signeasy.com/v2.1/me/signed/{signed_id}/download" # replace "signed_id"
            get = True
        if request.form["button"] == "Download certificate of self signed document":
            url = f"https://api.signeasy.com/v2.1/me/signed/{signed_id}/certificate/" # replace "signed_id"
            get = True
        if request.form["button"] == "Delete self signed document":
            url = f"https://api.signeasy.com/v2.1/me/signed/{signed_id}" # replace "signed_id"
            delete = True
        
        # embedded sending url for request signatures
        if request.form["button"] == "Fetch Pending Embedded RS":
            url = "https://api.signeasy.com/v2.1/rs/embedded/" 
            get = True

        if request.form["button"] == "Fetch Embedded RS details":
            url = f"https://api.signeasy.com/v2.1/rs/embedded/{pending_file_id}"
            get = True

        if request.form["button"] == "Download Embedded RS pending file":
            url = f"https://api.signeasy.com/v2.1/rs/embedded/{pending_file_id}/download/" # replace "pending_file_id"
            get = True

        if request.form["button"] == "Remind Signers of Embedded RS":
            url = f"https://api.signeasy.com/v2.1/rs/embedded/{pending_file_id}/remind" # replace "pending_file_id"
            post = True

        if request.form["button"] == "Cancel Embedded RS":
            url = f"https://api.signeasy.com/v2.1/rs/embedded/{pending_file_id}/cancel" # replace "pending_file_id"
            post = True
        
        # completed documents (embedded rs)

        if request.form["button"] == "Fetch Signed Embedded RS":
            url = "https://api.signeasy.com/2.1/rs/embedded/signed"
            get = True

        if request.form["button"] == "Fetch Signed document details":
            url = f"https://api.signeasy.com/2.1/rs/embedded/signed/{signed_id}" # replace "signed_id"
            get = True

        if request.form["button"] == "Download Signed document":
            url = f"https://api.signeasy.com/2.1/rs/embedded/signed/{signed_id}/download" # replace "signed_id"
            get = True

        if request.form["button"] == "Download Signed document certificate":
            url = f"https://api.signeasy.com/2.1/rs/embedded/signed/{signed_id}/certificate" # replace "signed_id"
            get = True

        if request.form["button"] == "Delete Signed document":
            url = f"https://api.signeasy.com/2.1/rs/embedded/signed/{signed_id}"  # replace "signed_id"
            delete = True

        # envelope (signature requests with one or more documents)

        if request.form["button"] == "List envelope RS":
            url = "https://api.signeasy.com/v2.1/rs/envelope/" 
            get = True        

        if request.form["button"] == "Fetch envelope RS details":
            url = f"https://api.signeasy.com/v2.1/rs/envelope/{pending_file_id}" # replace "pending file id"
            get = True        

        if request.form["button"] == "Download pending envelope RS document":
            url = f"https://api.signeasy.com/v2.1/rs/envelope/{pending_file_id}/download/merged" # replace "pending file id"
            get = True        

        if request.form["button"] == "Download envelope RS document as zip":
            url = f"https://api.signeasy.com/v2.1/rs/envelope/{pending_file_id}/download/split" # replace "pending file id"
            get = True        

        if request.form["button"] == "Remind signers of envelope RS":
            url = f"https://api.signeasy.com/v2.1/rs/envelope/{pending_file_id}/remind/" # replace "pending file id"
            post = True        

        if request.form["button"] == "Cancel an envelope RS document":
            url = f"https://api.signeasy.com/v2.1/rs/envelope/{pending_file_id}/cancel" # replace "pending file id"
            post = True        

        if request.form["button"] == "Retrieve Signed File details using pending ID":
            url = f"https://api.signeasy.com/v2.1/rs/envelope/signed/pending/{pending_file_id}" # replace "pending file id"
            get = True

        # signed (completed envelopes)

        if request.form["button"] == "List envelope signed documents":
            url = "https://api.signeasy.com/v2.1/rs/envelope/signed/"
            get = True

        if request.form["button"] == "Details of envelope signed document":
            url = f"https://api.signeasy.com/v2.1/rs/envelope/signed/{signed_id}" # replace "signed_id"
            get = True

        if request.form["button"] == "Download envelope signed documents as zip":
            url = f"https://api.signeasy.com/v2.1/rs/envelope/signed/{signed_id}/download/split" # replace "signed_id"
            get = True

        if request.form["button"] == "Download certificate envelope signed document":
            url = f"https://api.signeasy.com/v2.1/rs/envelope/signed/{signed_id}/certificate" # replace "signed_id"
            get = True

        if request.form["button"] == "Download envelope signed documents as merged PDF":
            url = f"https://api.signeasy.com/v2.1/rs/envelope/signed/{signed_id}/download/merged" # replace "signed_id"
            get = True

        if request.form["button"] == "Download envelope signed document individually":
            url = f"https://api.signeasy.com/v2.1/rs/envelope/signed/{signed_id}/original_id/download" # replace "signed_id"
            get = True

        if request.form["button"] == "Delete envelope signed document":
            url = f"https://api.signeasy.com/v2.1/rs/envelope/signed/{signed_id}" # replace "signed_id"
            delete = True

        # templates

        if request.form["button"] == "List templates":
            url = "https://api.signeasy.com/v2.1/template"
            get = True

        if request.form["button"] == "Fetch template details":
            url = f"https://api.signeasy.com/v2.1/template/{template_id}" # replace "template id"
            get = True

        if request.form["button"] == "Delete template details":
            url = f"https://api.signeasy.com/v2.1/template/{template_id}" # replace "template id"
            delete = True

        # complete documents (request signature using templates)
        
        if request.form["button"] == "Fetch details of signed file":
            url = f"https://api.signeasy.com/v2.1/template/rs/signed/{signed_file_id}/" # replace "signed file id"
            get = True
        
        if request.form["button"] == "Download signed file":
            url = f"https://api.signeasy.com/v2.1/template/rs/signed/{signed_file_id}/download" # replace "signed file id"
            get = True
        
        if request.form["button"] == "Download certificate of signed file":
            url = f"https://api.signeasy.com/v2.1/template/rs/signed/{signed_file_id}/certificate" # replace "signed file id"
            get = True
        
        if request.form["button"] == "Delete signed file":
            url = f"https://api.signeasy.com/v2.1/template/rs/signed/{signed_file_id}" # replace "signed file id"
            delete = True

        # request signature without markers
        
        if request.form["button"] == "List Request Signature without markers":
            url = "https://api.signeasy.com/v2.1/rs/"
            get = True
        
        if request.form["button"] == "Fetch Request Signature without markers details":
            url = f"https://api.signeasy.com/v2.1/rs/{rs_id}" # replace "rs_id"
            get = True
        
        if request.form["button"] == "Download Request Signature without markers":
            url = f"https://api.signeasy.com/v2.1/rs/{rs_id}/download" # replace "rs_id"
            get = True
        
        if request.form["button"] == "Remind Request Signature without markers":
            url = f"https://api.signeasy.com/v2.1/rs/{rs_id}/remind" # replace "rs_id"
            post = True
        
        if request.form["button"] == "Cancel Request Signature without markers":
            url = f"https://api.signeasy.com/v2.1/rs/{rs_id}/cancel" # replace "rs_id"
            post = True

        # completed documents (request signature without fields)

        if request.form["button"] == "List Signed documents":
            url = "https://api.signeasy.com/v2.1/rs/signed"
            get = True

        if request.form["button"] == "Fetch details of Signed document":
            url = f"https://api.signeasy.com/v2.1/rs/signed/{signed_id}" # replace "signed_id"
            get = True

        if request.form["button"] == "Download Signed document pdf":
            url = f"https://api.signeasy.com/v2.1/rs/signed/{signed_id}/download" # replace "signed_id"
            get = True

        if request.form["button"] == "Download Signed document certificate":
            url = f"https://api.signeasy.com/v2.1/rs/signed/{signed_id}/certificate" # replace "signed_id"
            get = True

        if request.form["button"] == "Delete Signed document":
            url = f"https://api.signeasy.com/v2.1/rs/signed/{signed_id}" # replace "signed_id"
            delete = True

        # callbacks
        # n/a at the moment

        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {auth_token}"
        }

        if post == True:
            response = requests.post(url, headers=headers)
        if get == True:
            response = requests.get(url, headers=headers)
        if delete == True:
            response = requests.delete(url, headers=headers)

        print(response.text)

    return render_template('index.html')

if __name__ == "__main__":
    app.run(port=6969, debug=True) # when on localhost
