from blank.core.models import LoadData, HaulierRate, LoadActivities
from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from flask_login import current_user
from sqlalchemy.sql import func
from sqlalchemy import and_
from datetime import date
from flask import flash
from blank import db
import requests
import json

class Load:

    # Generate knack connection headers
    def generateKnackHeaders(self):
        headers = { 'X-Knack-Application-Id': '56fb7babc4b0ccfb73a10d62', 'X-Knack-REST-API-Key': 'cf093a38-5a4b-4ef6-84ed-866276d3bd43', 'Content-Type': 'application/json' }
        retry_strategy = Retry( total=10, status_forcelist=[429, 500, 502, 503, 504], method_whitelist=["HEAD", "GET", "OPTIONS", "PUT"], backoff_factor=2)
        adapter = HTTPAdapter(max_retries=retry_strategy)
        http = requests.Session()
        http.mount("https://", adapter)
        print('FXN(generateKnackHeaders): Headers generated')
        return headers

    def updateLoadActivity(self, activity, load_id):
        data = LoadActivities(activity=activity, load_id=load_id, user_id=current_user.id)
        db.session.add(data)
        try:
            db.session.commit()
        except Exception as e:
            return False
        else:
            return True


    def getKnackDataByID(self, knack_id=""):
        # Generate query URL
        url = "https://api.knack.com/v1/objects/object_1/records"
        filters = { 'match': 'and', 'rules': [{ 'field': 'id', 'operator': 'is', 'value': str(knack_id) }]}
        json_filter = json.dumps(filters)
        url = url + "?filters=" + json_filter + "&rows_per_page=1000"
        try:
            response = requests.get(url, headers=self.generateKnackHeaders(), timeout=20)
        except:
            return None
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            return None


    def getLoadingCityTotals(self, loading_date):
        cities = [('Pickup', 'Select a City')]
        loads = db.session.query(LoadData.loading_city, func.count(LoadData.loading_city).label('total')).filter(and_(LoadData.load_date == loading_date, LoadData.loading_city != "", LoadData.transporter == "", LoadData.knack_load_status == "ACTIVE")).group_by(LoadData.loading_city).order_by(LoadData.loading_city).all()
        for load in loads:
            totals = load.loading_city + " [ " + str(load.total) + " loads ]"
            cities.append((load.loading_city,totals))
        return cities


    def getOffloadingCityTotals(self, offloading_date):
        cities = [('Drop', 'Select a City')]
        loads_data = db.session.query(LoadData.offloading_city, func.count(LoadData.offloading_city).label('total')).filter(and_(LoadData.load_date == offloading_date, LoadData.offloading_city != "", LoadData.transporter == "", LoadData.knack_load_status == "ACTIVE")).group_by(LoadData.offloading_city).order_by(LoadData.offloading_city).all()
        for load in loads_data:
            totals = load.offloading_city + " [ " + str(load.total) + " loads ]"
            cities.append((load.offloading_city,totals))
        return cities


    def getAvailableLoadTotals(self, pickup, drop, day):
        if pickup == 'Pickup' and drop == 'Drop':
            totals = db.session.query(func.count(LoadData.id).label('total')).filter(and_(LoadData.transporter == "", LoadData.knack_load_status == 'ACTIVE', LoadData.load_date == day)).all()
        elif pickup != 'Pickup' and drop == 'Drop':
            totals = db.session.query(func.count(LoadData.id).label('total')).filter(and_(LoadData.loading_city == pickup, LoadData.transporter == "", LoadData.knack_load_status == 'ACTIVE', LoadData.load_date == day)).all()
        elif pickup == 'Pickup' and drop != 'Drop':
            totals = db.session.query(func.count(LoadData.id).label('total')).filter(and_(LoadData.offloading_city == drop, LoadData.transporter == "", LoadData.knack_load_status == 'ACTIVE', LoadData.load_date == day)).all()
        elif pickup != 'Pickup' and drop != 'Drop':
            totals = db.session.query(func.count(LoadData.id).label('total')).filter(and_(LoadData.loading_city == pickup, LoadData.offloading_city == drop, LoadData.transporter == "", LoadData.knack_load_status == 'ACTIVE', LoadData.load_date == day)).all()
        return totals


    def getAvailableLoads(self, data):
        if data['pickup'] == 'Pickup' and data['drop'] == 'Drop':
            loads = db.session.query(LoadData, HaulierRate).join(HaulierRate, and_(LoadData.loading_city == HaulierRate.load_city, LoadData.offloading_city == HaulierRate.offload_city, HaulierRate.category == data['category']), isouter=True).filter(and_(LoadData.transporter == "", LoadData.knack_load_status == 'ACTIVE', LoadData.load_date == data['loading_date'])).order_by(LoadData.load_date)
        elif data['pickup'] != 'Pickup' and data['drop'] == 'Drop':
            loads = db.session.query(LoadData, HaulierRate).join(HaulierRate, and_(LoadData.loading_city == HaulierRate.load_city, LoadData.offloading_city == HaulierRate.offload_city, HaulierRate.category == data['category']), isouter=True).filter(and_(LoadData.loading_city == data['pickup'], LoadData.transporter == "", LoadData.knack_load_status == 'ACTIVE', LoadData.load_date == data['loading_date'])).order_by(LoadData.load_date)
        elif data['pickup'] == 'Pickup' and data['drop'] != 'Drop':
            loads = db.session.query(LoadData, HaulierRate).join(HaulierRate, and_(LoadData.loading_city == HaulierRate.load_city, LoadData.offloading_city == HaulierRate.offload_city, HaulierRate.category == data['category']), isouter=True).filter(and_(LoadData.offloading_city == data['drop'], LoadData.transporter == "", LoadData.knack_load_status == 'ACTIVE', LoadData.load_date == data['loading_date'])).order_by(LoadData.load_date)
        elif data['pickup'] != 'Pickup' and data['drop'] != 'Drop':
            loads = db.session.query(LoadData, HaulierRate).join(HaulierRate, and_(LoadData.loading_city == HaulierRate.load_city, LoadData.offloading_city == HaulierRate.offload_city, HaulierRate.category == data['category']), isouter=True).filter(and_(LoadData.loading_city == data['pickup'], LoadData.offloading_city == data['drop'], LoadData.transporter == "", LoadData.knack_load_status == 'ACTIVE', LoadData.load_date == data['loading_date'])).order_by(LoadData.load_date)
        return loads


    def getUnassignedLoads(self):
        if current_user.employer.type == 'Internal':
            loads = LoadData.query.filter(and_(LoadData.offload_date >= date.today(), LoadData.knack_load_status == "ACTIVE" )).order_by(LoadData.load_date).all()
        else:
            loads = LoadData.query.filter(and_(LoadData.transporter == current_user.employer.haulier.knack_id, LoadData.offload_date >= date.today(), LoadData.knack_load_status == "ACTIVE", LoadData.vehicle_registration == "" )).order_by(LoadData.load_date).all()
        return loads


    def getActiveLoads(self):
        if current_user.employer.type == 'Internal':
            loads = LoadData.query.filter(and_(LoadData.offload_date >= date.today(), LoadData.knack_load_status == "ACTIVE" )).order_by(LoadData.load_date).all()
        else:
            loads = LoadData.query.filter(and_(LoadData.transporter == current_user.employer.haulier.knack_id, LoadData.offload_date >= date.today(), LoadData.knack_load_status == "ACTIVE", LoadData.vehicle_registration != "" )).order_by(LoadData.load_date).all()
        return loads


    def getCompletedLoads(self):
        if current_user.employer.type == 'Internal':
            loads = LoadData.query.filter(LoadData.knack_load_status == "COMPLETE").order_by(LoadData.load_date).all()
        else:
            loads = LoadData.query.filter(and_(LoadData.transporter == current_user.employer.haulier.knack_id, LoadData.knack_load_status == "COMPLETE" )).order_by(LoadData.load_date).all()
        return loads


    def assignHaulier(self, id, rate):
        if (current_user.employer.type != 'haulier' and current_user.employer.status != 'Yes'):
            flash('You are not authorised to book loads.', 'orange')
            return False
        else:
            load = LoadData.query.filter_by(id=int(id)).first()
            data = self.getKnackDataByID(load.load_id_knack)
            # Check if the load is already booked on knack
            if data:
                if (data['records'][0]['field_294']):
                    flash('Another Haulier is already assigned to the load', 'red')
                    load.transporter = "123"
                    db.session.commit()
                    print('AssignHaulierFXN: Another Haulier is already assigned to the load')
                    return False
                else:
                    print('AssignHaulierFXN: Load is not booked on knack')
                    url = "https://api.knack.com/v1/pages/scene_6/views/view_7/records/" + str(load.load_id_knack)
                    data = {"field_58": 'No', 'field_80': 'No', 'field_294': str(current_user.employer.haulier.knack_id), 'field_7_raw': rate, 'field_7': 'R' + str(rate)}
                    try:
                        response = requests.put(url, headers=self.generateKnackHeaders(), data=json.dumps(data), timeout=20)
                    except requests.exceptions.RequestException as e:
                        error = str(e.__dict__['orig'])
                        print("AssignHaulierFXN: Error: " + error)
                        flash('We experienced an internal error. Please try again.', 'red')
                        return False
                    else:
                        if (response.status_code == 200):
                            # Add transporter and change to booked from Olog
                            load.transporter = current_user.employer.haulier.knack_id
                            load.booked_on_olog = 'Yes'

                            # Capture a record of the activity
                            activity = LoadActivities(activity="Booked a load", load_id=load.id, user_id=current_user.id)
                            db.session.add(activity)

                            db.session.commit()
                            print('AssignHaulierFXN: Haulier assigned to the load. Status Code: ' + str(response.status_code))
                            flash('Load booked', 'green')
                            return True
                        else:
                            print('AssignHaulierFXN: Something happened. Status Code: ' + str(response.status_code))
                            return False


    def cancelBooking(self, id):
        load = LoadData.query.filter_by(id=int(id)).first()
        data = self.getKnackDataByID(load.load_id_knack)
        if (data['records'][0]['field_294']):
            url = "https://api.knack.com/v1/pages/scene_6/views/view_7/records/" + str(load.load_id_knack)
            data = {"field_58": 'No', 'field_80': 'No', 'field_294': None, 'field_7_raw': None, 'field_7': None}
            try:
                response = requests.put(url, headers=self.generateKnackHeaders(), data=json.dumps(data), timeout=20)
            except requests.exceptions.RequestException as e:
                error = str(e.__dict__['orig'])
                print("cancelBooking: Error: " + error)
                flash('We experienced an internal error. Please try again.\n\n\n' + error, 'orange')
                return False
            else:
                if (response.status_code == 200):
                    # Remove transporter and change to not booked from Olog
                    load.transporter = ""
                    load.booked_on_olog = 'No'

                    # Capture a record of the activity
                    activity = LoadActivities(activity="Cancelled booking", load_id=load.id, user_id=current_user.id)
                    db.session.add(activity)

                    db.session.commit()
                    print('cancelBooking: Booking cancelled ' + str(response.status_code))
                    flash('Booking cancelled', 'green')
                    return True
                else:
                    print('cancelBooking: Something went wrong. Status Code: ' + str(response.status_code))
                    return False
        else:
            print('Load is not booked on knack')
            return False


    def generateLoadCon(self, knack_id, company, driver):
        print('Generating Load con')
        url = "https://api.knack.com/v1/pages/scene_6/views/view_7/records/" + knack_id
        data = {"field_58": 'Yes', 'field_80': 'Yes', 'field_42': driver['name'], 'field_275': driver['id'], 'field_43': driver['reg'], 'field_97': driver['cell'], 'field_294': company}
        try:
            response = requests.put(url, headers=self.generateKnackHeaders(), data=json.dumps(data), timeout=20)
            print('Load con sent: ' + str(response.status_code))
            if response.status_code == 200:
                load = LoadData.query.filter_by(load_id_knack=knack_id).first()
                # Capture a record of the activity
                if load:
                    activity = LoadActivities(activity="Load con generated", load_id=load.id, user_id=current_user.id)
                    db.session.add(activity)
                    db.session.commit()

                flash('Load con sent', 'green')
            return True
        except requests.exceptions.RequestException as e:
            print('Error sending load con')
            flash('Failed to send load con. Please retry', 'red')
            return False
