from flask import Blueprint, render_template
from flask_login import login_required
import app.database as data
from app.helpers import reject_operator

from app.middleware import db
from flask import jsonify
from app.helpers2 import build_reports_excel
from flask import send_file


reports = Blueprint('reports', __name__)


@reports.route('/reports')
@login_required
@reject_operator
def reports_home():
    
    return render_template('reports.html', page_title='Reports')


@reports.route('/reports_data')
@login_required
@reject_operator
def reports_data():
    tickets = data.Serial.all_clean()

    office_ids = [row[0] for row in 
              db.session.query(data.Serial.office_id)
              .distinct()
              .all()]
    statistics_by_office_name={}
    for oid in office_ids:
        q = tickets.filter_by(office_id=oid)
        office_name = data.Office.query.get(oid).name
        statistics_by_office_name[office_name]={}
        statistics_by_office_name[office_name]["total_count"]=q.count()
        statistics_by_office_name[office_name]["attended_count"]=q.attended.count()
        statistics_by_office_name[office_name]["unattended_count"]=q.unattended
        statistics_by_office_name[office_name]["waiting_count"]=q.waiting.count()
        statistics_by_office_name[office_name]["processed_count"]=q.processed.count()


    return jsonify(statistics_by_office_name=statistics_by_office_name)


@reports.route('/make_reports_excel')
@login_required
@reject_operator
def make_reports_excel():
    tickets = data.Serial.all_clean()

    office_ids = [row[0] for row in 
              db.session.query(data.Serial.office_id)
              .distinct()
              .all()]
    statistics_by_office_name={}
    for oid in office_ids:
        q = tickets.filter_by(office_id=oid)
        office_name = data.Office.query.get(oid).name
        statistics_by_office_name[office_name]={}
        statistics_by_office_name[office_name]["total_count"]=q.count()
        statistics_by_office_name[office_name]["attended_count"]=q.attended.count()
        statistics_by_office_name[office_name]["unattended_count"]=q.unattended
        statistics_by_office_name[office_name]["waiting_count"]=q.waiting.count()
        statistics_by_office_name[office_name]["processed_count"]=q.processed.count()
    
    excel_io, filename = build_reports_excel(statistics_by_office_name)
    return send_file(
        excel_io,
        as_attachment=True,
        download_name=filename,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )