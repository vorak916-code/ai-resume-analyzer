import os
import json
import pandas as pd
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify, Response
from werkzeug.utils import secure_filename
from models import User, ResumeReport
from resume_parser import LocalPDFParser
from ai_analyzer import AIAnalysisEngine

routes_bp = Blueprint('routes', __name__)
analyzer_engine = AIAnalysisEngine()

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Keyword list for local fallback tracking matching mechanisms
TARGET_KEYWORDS = ["Python", "Flask", "SQL", "Machine Learning", "Data Structures", "Cloud", "API", "Agile"]

@routes_bp.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('routes.dashboard'))
    return redirect(url_for('routes.login'))

@routes_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.register(username, password):
            flash("Registration Successful. Please Login.", "success")
            return redirect(url_for('routes.login'))
        flash("Username already exists.", "danger")
    return render_template('register.html')

@routes_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.authenticate(username, password)
        if user:
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('routes.dashboard'))
        flash("Invalid user verification credentials.", "danger")
    return render_template('login.html')

@routes_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('routes.login'))

@routes_bp.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('routes.login'))
    history = ResumeReport.get_by_user(session['user_id'])
    return render_template('dashboard.html', history=history)

@routes_bp.route('/analyze', methods=['POST'])
def analyze():
    if 'user_id' not in session:
        return redirect(url_for('routes.login'))
        
    if 'resume' not in request.files:
        flash("No file object provided", "danger")
        return redirect(url_for('routes.dashboard'))
        
    file = request.files['resume']
    if file.filename == '':
        flash("No file highlighted for tracking data upload.", "danger")
        return redirect(url_for('routes.dashboard'))

    if file and file.filename.lower().endswith('.pdf'):
        filename = secure_filename(file.filename)
        save_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(save_path)
        
        try:
            # Core processing step workflows 
            extracted_text = LocalPDFParser.extract_text(save_path)
            ai_data = analyzer_engine.analyze_resume_content(extracted_text)
            
            # Augmented Local Matching Algorithm
            kw_match = analyzer_engine.calculate_keyword_match(extracted_text, TARGET_KEYWORDS)
            
            # Combine scores
            final_score = int(min(100, (ai_data.get('base_score', 70) * 0.7) + (kw_match * 0.3)))
            ai_data['calculated_keyword_match'] = kw_match
            
            report_id = ResumeReport.save(session['user_id'], filename, final_score, ai_data)
            return redirect(url_for('routes.view_report', report_id=report_id))
            
        except Exception as process_error:
            flash(f"Analysis system failed processing sequence: {str(process_error)}", "danger")
            return redirect(url_for('routes.dashboard'))
        finally:
            if os.path.exists(save_path):
                os.remove(save_path)
                
    flash("Invalid File Type. Ensure upload structure targets explicit PDFs.", "danger")
    return redirect(url_for('routes.dashboard'))

@routes_bp.route('/report/<int:report_id>')
def view_report(report_id):
    if 'user_id' not in session:
        return redirect(url_for('routes.login'))
    report = ResumeReport.get_by_id(report_id, session['user_id'])
    if not report:
        flash("Unauthorized resource search.", "danger")
        return redirect(url_for('routes.dashboard'))
    return render_template('analysis.html', report=report)

@routes_bp.route('/export/<string:format_type>/<int:report_id>')
def export_report(format_type, report_id):
    if 'user_id' not in session:
        return redirect(url_for('routes.login'))
    report = ResumeReport.get_by_id(report_id, session['user_id'])
    if not report:
        return "Unauthorized file request", 401
        
    if format_type == 'json':
        return jsonify(report.data)
        
    elif format_type == 'csv':
        flat_data = {
            "Filename": [report.filename],
            "Score": [report.score],
            "Skills Found": [", ".join(report.data.get('skills', []))],
            "Roles Recommended": [", ".join(report.data.get('recommended_roles', []))]
        }
        df = pd.DataFrame(flat_data)
        return Response(
            df.to_csv(index=False),
            mimetype="text/csv",
            headers={"Content-disposition": f"attachment; filename=report_{report_id}.csv"}
        )