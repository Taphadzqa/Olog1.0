from datetime import datetime
from blank import db, login_manager
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    last_login = db.Column(db.DateTime, nullable=True)
    created_on = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id})

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)



class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    type = db.Column(db.String(50), nullable=False) #Can be a Haulier, Supplier, Internal
    employees = db.relationship('User', backref='employer', lazy='dynamic')
    haulier = db.relationship('Haulier', backref='company', uselist=False)
    location = db.relationship('Location', backref='owner', lazy='dynamic')
    created_on = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)



class Haulier(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    knack_id = db.Column(db.String(50), nullable=False)
    git_cover_amount = db.Column(db.Integer, nullable=False)
    insurance_expires_on = db.Column(db.DateTime, nullable=False)
    beer_cover = db.Column(db.Boolean, nullable=False)
    spirits_cover = db.Column(db.Boolean, nullable=False)
    hazchem = db.Column(db.Boolean, nullable=False)
    category = db.Column(db.String(50), nullable=False, default="General")
    loads = db.relationship('Load', backref='transporter', lazy='dynamic')
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), unique=True, nullable=False)
    created_on = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)



class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    knack_id = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    coordinates = db.Column(db.String(50), nullable=False)
    comments = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    created_on = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)



class Load(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    knack_id = db.Column(db.String(50), nullable=False)
    reference_number = db.Column(db.String(50), nullable=False)
    load_date = db.Column(db.Date, nullable=False)
    offload_date = db.Column(db.Date, nullable=False)
    multidrop = db.Column(db.Boolean, nullable=False)
    order_number = db.Column(db.String(50), nullable=False)
    sap_number = db.Column(db.String(50), nullable=False)
    supplier_rate = db.Column(db.String(50), nullable=False)
    haulier_rate = db.Column(db.String(50), nullable=True)
    driver_name = db.Column(db.String(50), nullable=True)
    driver_cell = db.Column(db.String(50), nullable=True)
    driver_id = db.Column(db.String(50), nullable=True)
    vehicle_reg = db.Column(db.String(50), nullable=True)
    status = db.Column(db.String(50), default='Active', nullable=False)
    booked_on_olog = db.Column(db.String(50), default='No', nullable=False)
    load_location = db.Column(db.Integer, db.ForeignKey('location.id'), nullable=False)
    offload_location = db.Column(db.Integer, db.ForeignKey('location.id'), nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    haulier_id = db.Column(db.Integer, db.ForeignKey('haulier.id'), nullable=True)
    created_on = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)



class LoadData(db.Model):
    __tablename__ = "load_data"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    load_id_knack = db.Column(db.String(255), nullable=False)
    ol_num = db.Column(db.String(25), nullable=False)
    load_date = db.Column(db.Date, nullable=False)
    offload_date = db.Column(db.Date, nullable=False)
    truck_type = db.Column(db.String(50), nullable=False)
    loading_city = db.Column(db.String(50), nullable=False)
    offloading_city = db.Column(db.String(255), nullable=False)
    loading_address = db.Column(db.String(255), nullable=False)
    offloading_address = db.Column(db.String(255), nullable=False)
    loading_address_coords = db.Column(db.String(255), nullable=False)
    offloading_address_coords = db.Column(db.String(255), nullable=False)
    load_type = db.Column(db.String(25), nullable=False)
    knack_load_status = db.Column(db.String(20), default='Active', nullable=False)
    customer_rate_knack = db.Column(db.Integer, nullable=False)
    haulier_rate_knack = db.Column(db.Integer, nullable=False)
    margin = db.Column(db.Integer, nullable=False)
    po_number = db.Column(db.String(255), nullable=False)
    sap_number = db.Column(db.String(255), nullable=False)
    transporter = db.Column(db.String(255), nullable=False)
    driver_name = db.Column(db.String(255), nullable=False)
    driver_cellnumber = db.Column(db.String(25), nullable=False)
    driver_id = db.Column(db.String(255), nullable=False)
    vehicle_registration = db.Column(db.String(25), nullable=False)
    vehicle_location = db.Column(db.String(50), nullable=False)
    vehicle_location_tmstp = db.Column(db.String(50), nullable=False)



class LoadActivities(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    activity = db.Column(db.String(255), nullable=False)
    load_id = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    done_on = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)



class SystemActivities(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    activity = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    done_on = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)



class SupplierRate(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    load_city = db.Column(db.String(50), nullable=False)
    offload_city = db.Column(db.String(50), nullable=False)
    rate = db.Column(db.Integer, nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    created_on = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)



class HaulierRate(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    load_city = db.Column(db.String(50), nullable=False)
    offload_city = db.Column(db.String(50), nullable=False)
    base_rate = db.Column(db.Float, nullable=False, default=0)
    rate = db.Column(db.Float, nullable=False)
    created_on = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)



class LoadUpdate(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    load_id = db.Column(db.String(50), nullable=False)
    eta = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    comments = db.Column(db.String(255), nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_by = db.Column(db.Integer, nullable=False)



class SystemVariables(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    base_fuel_price = db.Column(db.Float, nullable=False, default=0)
    new_fuel_price = db.Column(db.Float, nullable=False, default=0)
    date_updated = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_by = db.Column(db.Integer, nullable=False)
