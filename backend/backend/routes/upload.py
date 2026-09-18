#upload part
from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import login_required
from models import db
import os

upload_bp = Blueprint('upload', __name__, url_prefix='/upload')

@upload_bp.route('/scan', methods=['GET', 'POST'])
@login_required
def upload_scan():
    if request.method == 'POST':
        scan_file = request.files.get('scan')
        if scan_file and scan_file.filename != '':
            # Save the scan file
            filename = scan_file.filename
            upload_path = os.path.join('static', 'uploads', filename)
            scan_file.save(upload_path)
            # Optionally, save file info to DB for user tracking
            flash('Scan uploaded successfully!')
            return redirect(url_for('upload.upload_scan'))
        else:
            flash('No file selected. Please upload a scan.')
    return render_template('upload_scan.html')