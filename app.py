from flask import Flask, url_for, request, render_template, jsonify
from flask.helpers import send_from_directory
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, select, text
from datatables import ColumnDT, DataTables
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
import json
import datetime


app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres@postgres.lan:5432/dt_test'

db = SQLAlchemy(app)


class Address(db.Model):
    __tablename__ = 'address'

    id          = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text, unique=True)
    city        = db.Column(db.Text)
    user_id     = db.Column(db.Integer, db.ForeignKey('user.id'))


class User(db.Model):
    __tablename__ = 'user'

    id          = db.Column(db.Integer, primary_key=True)
    first_name  = db.Column(db.Text)
    last_name   = db.Column(db.Text)
    email       = db.Column(db.Text)
    ip_address  = db.Column(db.Text)
    country     = db.Column(db.Text)
    # date_joined  = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    date_joined = db.Column(db.Text)
    # Use lazy=joined to prevent O(N) queries
    address     = db.relationship("Address", uselist=False, backref="user", lazy="joined")
    city_array  = db.column_property(
        select(func.array_agg(Address.city.distinct())).
        scalar_subquery()
    )


@app.route("/")
def index():
    # return render_template("template.j2")
    return render_template("dt_110x.html")
    # pagetitle = "HomePage"
    # return render_template("index.html",
    #                        mytitle=pagetitle,
    #                        mycontent="Hello World")


@app.route("/data")
def data():
    """Return server side data."""
    # defining columns
    columns = [
        ColumnDT(User.id, mData='id'),
        ColumnDT(User.first_name, mData='first_name'),
        ColumnDT(User.last_name, mData='last_name'),
        ColumnDT(User.email, mData='email'),
        ColumnDT(User.ip_address, mData='ip_address'),
        ColumnDT(User.country, mData='country'),
        ColumnDT(Address.description, mData='Address_description'),
        ColumnDT(User.date_joined, mData='date_joined'),
        ColumnDT(User.city_array, mData='city_array'),
    ]

    # defining the initial query depending on your purpose
    query = db.session.query().select_from(User).join(Address, isouter=True)

    # GET parameters
    params = request.args.to_dict()

    # instantiating a DataTable for the query and table needed
    rowTable = DataTables(params, query, columns)

    # returns what is needed by DataTable
    return jsonify(rowTable.output_result())

if __name__ == "__main__":
    app.run(debug=True)
