# Imports
from flask import render_template, Blueprint, url_for, request, flash, redirect, jsonify
from flask_login import current_user, login_required
from datetime import timedelta, datetime
from blank.routes.classes.load import *
from blank.core.models import LoadUpdate
from blank.routes.forms import *
# Create blueprint handler
main = Blueprint('main', __name__)


@main.route('/')
def home():
    return render_template('main/home.html', title='Welcome')


@main.route('/browse', methods=['GET', 'POST'])
@login_required
def browse():
    today = str((datetime.utcnow()).strftime('%Y-%m-%d'))
    # Search form
    form = SearchLoadForm()
    form.pickup.choices = Load().getLoadingCityTotals(today)
    form.drop.choices = Load().getOffloadingCityTotals(today)
    # If form is submitted ...
    if form.validate_on_submit():
        if form.pickup.data != 'Pickup' and form.drop.data != 'Drop':
            activity = 'Searched for a load from ' + str(form.pickup.data) + ' to ' + str(form.drop.data)
        elif form.pickup.data != 'Pickup' and form.drop.data == 'Drop':
            activity = 'Searched for a load from ' + str(form.pickup.data)
        elif form.pickup.data == 'Pickup' and form.drop.data != 'Drop':
            activity = 'Searched for a load to ' + str(form.drop.data)
        else:
            activity = 'Searched for a load'
        Load().updateLoadActivity(activity, 0)
        return redirect(url_for('main.loads', pickup=form.pickup.data, drop=form.drop.data, loading_date=form.loading_date.data))
    # Show webpage
    return render_template('main/browse.html', title='Search for loads', form=form)


@main.route('/loads')
@login_required
def loads():
    today = str((datetime.utcnow()).strftime('%Y-%m-%d'))
    # Search form
    form = SearchLoadForm()
    formAssign = AssignDetailsForm()
    form.pickup.choices = Load().getLoadingCityTotals(today)
    form.drop.choices = Load().getOffloadingCityTotals(today)
    # Receive search data
    if request.args.get('loading_date', None) == None:
        return redirect(url_for('main.browse'))
    loading_date = datetime.strptime(request.args.get('loading_date', None),'%Y-%m-%d')
    data = {'pickup': request.args.get('pickup', 'Pickup'), 'drop': request.args.get('drop', None), 'loading_date': loading_date, 'category': current_user.employer.haulier.category}
    # Template variables
    loads = Load().getAvailableLoads(data)
    days = {
        'today': today,
        'prev_2': loading_date + timedelta(days=-2),
        'prev': loading_date + timedelta(days=-1),
        'next': loading_date + timedelta(days=+1),
        'next_2': loading_date + timedelta(days=+2),
        'next_3': loading_date + timedelta(days=+3),
        'next_4': loading_date + timedelta(days=+4)
    }
    totals = {
        'prev_2': Load().getAvailableLoadTotals(data['pickup'], data['drop'], days['prev_2']),
        'prev': Load().getAvailableLoadTotals(data['pickup'], data['drop'], days['prev']),
        'next': Load().getAvailableLoadTotals(data['pickup'], data['drop'], days['next']),
        'next_2': Load().getAvailableLoadTotals(data['pickup'], data['drop'], days['next_2']),
        'next_3': Load().getAvailableLoadTotals(data['pickup'], data['drop'], days['next_3']),
        'next_4': Load().getAvailableLoadTotals(data['pickup'], data['drop'], days['next_4'])
    }
    # If form is submitted ...
    if form.validate_on_submit():
        return redirect(url_for('main.loads', pickup=form.pickup.data, drop=form.drop.data, loading_date=form.loading_date.data))
    # If send load con form is submitted
    if formAssign.validate_on_submit():
        print('Form submitted')
        data = {'name': form.driver.data, 'id': form.id.data, 'reg': form.reg.data, 'cell': form.cell.data}
        Load().generateLoadCon(form.load_id.data, current_user.employer.haulier.knack_id, data)
        return redirect(url_for('main.loads'))
    # Show webpage
    return render_template('main/loads.html', title='Available loads', form=form, formAssign=formAssign, loads=loads, days=days, totals=totals, data=data)


@main.route('/loads/unassigned', methods=['GET', 'POST'])
@login_required
def unassigned_loads():
    today = str((datetime.utcnow()).strftime('%Y-%m-%d'))
    # Forms
    form = AssignDetailsForm()
    # If send load con form is submitted
    if form.validate_on_submit():
        print('Form submitted')
        data = {'name': form.driver.data, 'id': form.id.data, 'reg': form.reg.data, 'cell': form.cell.data}
        Load().generateLoadCon(form.load_id.data, current_user.employer.haulier.knack_id, data)
        return redirect(url_for('main.unassigned_loads'))
    # Get booked loads
    loads = Load().getUnassignedLoads()
    # Show webpage
    return render_template('main/unassigned_loads.html', title='Unassigned loads', loads=loads, form=form)


@main.route('/loads/active', methods=['GET', 'POST'])
@login_required
def active_loads():
    today = str((datetime.utcnow()).strftime('%Y-%m-%d'))
    # Forms
    form = AssignDetailsForm()
    updateform = UpdateStatusForm()
    # If send load con form is submitted
    if form.validate_on_submit():
        print('Form submitted')
        data = {'name': form.driver.data, 'id': form.id.data, 'reg': form.reg.data, 'cell': form.cell.data}
        Load().generateLoadCon(form.load_id.data, current_user.employer.haulier.knack_id, data)
        return redirect(url_for('main.active_loads'))
    # If update form is submitted
    if updateform.validate_on_submit():
        update = LoadUpdate(load_id=updateform.load_id.data, eta=updateform.eta.data, status=updateform.status.data, comments=updateform.comments.data, updated_by=current_user.id)
        db.session.add(update)
        try:
            db.session.commit()
            flash('Load Information Updated', 'green')
        except Exception as e:
            flash('Failed to update load infomation', 'red')
        finally:
            return redirect(url_for('main.active_loads'))
    # Get booked loads
    loads = Load().getActiveLoads()
    # Show webpage
    return render_template('main/active_loads.html', title='Active loads', loads=loads, form=form, updateform=updateform)


@main.route('/loads/completed', methods=['GET', 'POST'])
@login_required
def completed_loads():
    today = str((datetime.utcnow()).strftime('%Y-%m-%d'))
    # Get completed loads
    loads = Load().getCompletedLoads()
    # Show webpage
    return render_template('main/completed_loads.html', title='Completed loads', loads=loads)


@main.route('/loads/book/<int:id>/<float:rate>')
@login_required
def accept_tender(id, rate):
    Load().assignHaulier(id, rate)
    return redirect(url_for('main.browse'))


@main.route('/loads/cancel_booking/<int:id>')
@login_required
def cancel_booking(id):
    Load().cancelBooking(id)
    return redirect(url_for('main.unassigned_loads'))


@main.route('/reports')
@login_required
def reports():
    return render_template('main/reports.html', title='Reports')


@main.route('/filter_browse_form', methods=['GET', 'POST'])
@login_required
def filter_browse_form():
    if request.method == "POST":
        loading_date = request.form['loading_date']
        data = {}
        # If the Loading from form has been changed
        if 'pickup' in request.form:
            pickup = request.form['pickup']
            if pickup == "Pickup":
                loads = db.session.query(LoadData.offloading_city, func.count(LoadData.offloading_city).label('total')).filter(and_(LoadData.load_date == loading_date, LoadData.offloading_city != "", LoadData.transporter == "", LoadData.knack_load_status == "ACTIVE")).group_by(LoadData.offloading_city).order_by(LoadData.offloading_city).all()
            else:
                loads = db.session.query(LoadData.offloading_city, func.count(LoadData.offloading_city).label('total')).filter(and_(LoadData.load_date == loading_date, LoadData.loading_city == pickup, LoadData.offloading_city != "", LoadData.transporter == "", LoadData.knack_load_status == "ACTIVE")).group_by(LoadData.offloading_city).order_by(LoadData.offloading_city).all()
            for load in loads:
                city = load.offloading_city + " [ " + str(load.total) + " loads ]"
                data.update({load.offloading_city : city})
        # If the Loading to form has been changed
        elif 'drop' in request.form:
            drop = request.form['drop']
            if drop == "Drop":
                loads = db.session.query(LoadData.loading_city, func.count(LoadData.loading_city).label('total')).filter(and_(LoadData.load_date == loading_date, LoadData.offloading_city != "", LoadData.loading_city != "", LoadData.transporter == "", LoadData.knack_load_status == "ACTIVE")).group_by(LoadData.loading_city).order_by(LoadData.loading_city).all()
            else:
                loads = db.session.query(LoadData.loading_city, func.count(LoadData.loading_city).label('total')).filter(and_(LoadData.load_date == loading_date, LoadData.offloading_city == drop, LoadData.offloading_city != "", LoadData.loading_city != "", LoadData.transporter == "", LoadData.knack_load_status == "ACTIVE")).group_by(LoadData.loading_city).order_by(LoadData.loading_city).all()
            for load in loads:
                city = load.loading_city + " [ " + str(load.total) + " loads ]"
                data.update({load.loading_city : city})
        # If the loading from and loading to have not been changed
        else:
            loading = {}
            offloading = {}
            loads = db.session.query(LoadData.loading_city, func.count(LoadData.loading_city).label('total')).filter(and_(LoadData.load_date == loading_date, LoadData.loading_city != "", LoadData.transporter == "", LoadData.knack_load_status == "ACTIVE")).group_by(LoadData.loading_city).order_by(LoadData.loading_city).all()
            for load in loads:
                city = load.loading_city + " [ " + str(load.total) + " loads ]"
                loading.update({load.loading_city : city})

            loads = db.session.query(LoadData.offloading_city, func.count(LoadData.offloading_city).label('total')).filter(and_(LoadData.load_date == loading_date, LoadData.offloading_city != "", LoadData.transporter == "", LoadData.knack_load_status == "ACTIVE")).group_by(LoadData.offloading_city).order_by(LoadData.offloading_city).all()
            for load in loads:
                city = load.offloading_city + " [ " + str(load.total) + " loads ]"
                offloading.update({load.offloading_city : city})
            data = {'loading': loading, 'offloading': offloading}
        print(data)
        return jsonify(data)
    return redirect(url_for('main.browse'))



@main.route('/shipper')
# @login_required
def shipper():
    return render_template('main/shipper.html', title='Shipper')



@main.route('/carrier')
# @login_required
def carrier():
    return render_template('main/carrier.html', title='Carrier')
