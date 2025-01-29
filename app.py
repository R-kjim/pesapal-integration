from flask import Flask,request,make_response,render_template
from assists import *
from models import Order,Payment,db
from flask_restful import Resource, Api
import secrets
from flask_migrate import Migrate
from flask_uuid import FlaskUUID

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app=Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] =secrets.token_hex(32)

api=Api(app=app)
db.init_app(app=app)
Migrate(app=app, db=db)
FlaskUUID(app=app)


class Initiate_payment(Resource):
    def post(self):
        data=request.get_json()
        '''
        validate your data accordingly
        '''
        amount=data.get("amount")
        try:
            # create an order and a payment instance
            new_order=Order(amount=data.get('amount'))
            db.session.add(new_order)
            db.session.flush()
            order_id=new_order.order_id
            print(new_order.to_dict())
            payment=Payment(amount=amount,order_id=order_id)
            db.session.add(payment)
            db.session.flush()
            payment_id=payment.id
            auth_response=authentication()
            if auth_response['status']!="200":
                return make_response({"message":auth_response["message"]},auth_response['status'])
            ipn_url_response=registerIPNURL(auth_response=auth_response,payment_id=payment_id)
            if ipn_url_response["status"]!="200":
                return make_response({"message":ipn_url_response["message"]},ipn_url_response["status"])
            submit_order_response=submit_order(ipn_url_response["ipn_id"],auth_response,order_id=order_id,amount=amount)
            if submit_order_response['status']!="200":
                return make_response({'message':f"{submit_order_response['message']}"},submit_order_response['status'])
            setattr(payment,"tracking_id",submit_order_response['order_tracking_id'])
            db.session.commit()
            return make_response(submit_order_response,201)
        except Exception as e:
            print(e)
            return make_response({"message":"Server error occurred"},500)
api.add_resource(Initiate_payment,'/order-now')

class Update_payment(Resource):
    def post(self,id):
        try:
            payment=Payment.query.filter_by(id=id).first()
            if not payment:
                return make_response({"message":"Payment record doesn't exist"},400)
            transaction_response=check_transaction(tracking_id=payment.tracking_id)
            if transaction_response["status"]!="200":
                return make_response({"message":"Error checking transaction"},400)
            setattr(payment,"payment_status",transaction_response["payment_status_description"])
            setattr(payment,"payment_method",transaction_response["payment_method"])
            db.session.commit()
            return make_response(payment.to_dict(),200)
        except Exception as e:
            print(e)
            db.session.rollback()
            return make_response({"message":"Error updating payment record"},500)
api.add_resource(Update_payment,'/payment/<string:id>')

class Home(Resource):
    def get(self):
        return make_response(render_template('index.html'),200)
api.add_resource(Home,'/')

if __name__=="__main__":
    app.run(port=5555,debug=True)