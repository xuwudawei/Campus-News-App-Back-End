from flask import Flask, request, flash, url_for, redirect, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_mail import Mail
import os
from sqlalchemy import create_engine
from sqlalchemy.sql.expression import update
from sqlalchemy.orm import sessionmaker
from send_mail import send_mail
import json
# creating database engine and connecting it to th flask application
engine = create_engine(
    'postgres://', echo=True)

# main flask application
app = Flask(__name__)
#basedir = os.path.abspath(os.path.dirname(__file__))

ENV = 'dev'
if ENV == 'dev':
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://'
else:
    app.debug = False
    app.config['SQLALCHEMY_DATABASE_URI'] = ''


def row2dict(row):
    print("Yes")
    d = {}
    for column in row.__table__.columns:
        d[column.name] = str(getattr(row, column.name))
    return d

# database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.urandom(24)

# init database
databaseObj = SQLAlchemy(app)
# init ma
ma = Marshmallow(app)
Session = sessionmaker(bind=engine)
session = Session()


# class which accepts our database model
class User(databaseObj.Model):
    # details for creating the database
    __tablename__ = 'user'
    USER_ID = databaseObj.Sequence('user_id_seq', start=1)

    id = databaseObj.Column(databaseObj.Integer, USER_ID,
                            primary_key=True, server_default=USER_ID.next_value())
    api_key = databaseObj.Column(databaseObj.String(
        500))
    name = databaseObj.Column(databaseObj.String(500), nullable=False)
    regNo = databaseObj.Column(databaseObj.String(
        50), unique=True, primary_key=True)
    email = databaseObj.Column(databaseObj.String(50), nullable=False)
    password = databaseObj.Column(databaseObj.String(50), nullable=False)
    course = databaseObj.Column(databaseObj.String(50), nullable=False)
    logged = databaseObj.Column(databaseObj.Boolean)

    # a constructor to insert new user's details
    def __init__(self,  api_key, logged, name, regNo, email, password, course):
        self.api_key = api_key
        self.logged = logged
        self.name = name
        self.regNo = regNo
        self.email = email
        self.password = password
        self.course = course

# user schema
class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'logged', 'api_key', 'name', 'regNo',
                  'email', 'password', 'course')
        # model = User
        # load_instance = True


# init schema
user_schema = UserSchema()
users_schema = UserSchema(many=True)


# all my routes
# show all registered users
@app.route('/user', methods=['GET', 'POST'])
def getAllUser():
    print("Yes")
    all_users = User.query.all()
    return users_schema.jsonify(all_users)
 ate('show_all.html', User=User.query.all())

# register new user
@app.route('/add', methods=['POST'])
def create_User():
    logged = False
    api_key = request.json['api_key']
    name = request.json['name']
    regNo = request.json['regNo']
    email = request.json['email']
    password = request.json['password']
    course = request.json['course']

    # constructing new user
    new_user = User(api_key, logged, name, regNo, email, password, course)
    exist = databaseObj.session.query(
        databaseObj.exists().where(User.regNo == regNo)).scalar()
    if(exist == False):
        # adding new user to database and then commit
        databaseObj.session.add(new_user)
        databaseObj.session.commit()
    
        return user_schema.jsonify(new_user)
    else:
        return jsonify({"message": "user with registration Number "+regNo + " already exist !"})

# get existing user details
@app.route('/user/<regNo>', methods=['GET', 'POST'])
def getSingleUser(regNo):
    user = User.query.filter_by(regNo=request.json["regNo"]).first()
    # print(user)
    if(row2dict(user)['password'] == request.json["password"]):
        # print(user)
        print(row2dict(user))
        return jsonify({**row2dict(user), "logged": True})
    else:
        return jsonify({"message": "Invalid User Details"})

# Change username
@app.route('/user/changeName/<regNo>', methods=['PUT'])
def updateName(regNo):
    user = User.query.filter_by(regNo=request.json["regNo"]).first()
    name = request.json['name']
    user.name = name

    databaseObj.session.commit()

    return user_schema.jsonify(user)


# Change Email
@ app.route('/user/changeEmail/<regNo>', methods=['PUT'])
def updateEmail(regNo):
    user = User.query.filter_by(regNo=request.json["regNo"]).first()
    email = request.json['email']
    user.email = email

    databaseObj.session.commit()

    return user_schema.jsonify(user)


# Change Password
@ app.route('/user/changePassword/<regNo>', methods=['PUT'])
def updatePassword(regNo):
    user = User.query.filter_by(regNo=request.json["regNo"]).first()
    password = request.json['password']
    user.password = password

    databaseObj.session.commit()

    return user_schema.jsonify(user)


# delete user
@ app.route('/user/delete/<regNo>', methods=['DELETE'])
def deleteUser(regNo):
    read_regNo = request.json["regNo"]
    user = User.query.filter_by(regNo=request.json["regNo"]).first()
    databaseObj.session.delete(user)
    databaseObj.session.commit()

    return jsonify({"message": f"User with registration number '{read_regNo}' has been deleted successfully!"})




    ######################################################################## NEWSPAPERS ##############################################

    # class for newspapers which accepts our database model


class News(databaseObj.Model):
    __tablename__ = 'news'
    title = databaseObj.Column(databaseObj.String(
        500), primary_key=True, nullable=False)
    content = databaseObj.Column(databaseObj.String(5000), nullable=False)
    description = databaseObj.Column(databaseObj.String(50000), nullable=False)
    date = databaseObj.Column(databaseObj.String(50), nullable=False)
    url = databaseObj.Column(databaseObj.String(500), nullable=False)
    imageUrl = databaseObj.Column(databaseObj.String(500), nullable=False)
    category = databaseObj.Column(databaseObj.String(500), nullable=False)

    # a constructor to insert newspaper details
    def __init__(self,  title, content, description, date, url, imageUrl, category):
        self.title = title
        self.content = content
        self.description = description
        self.date = date
        self.url = url
        self.imageUrl = imageUrl
        self.category = category


# news schema
class NewsSchema(ma.Schema):
    class Meta:
        fields = ('id', 'title', 'content', 'description', 'date',
                  'url', 'imageUrl', 'category')


# init schema
news_one_schema = NewsSchema()
news_many_schema = NewsSchema(many=True)


# all my routes
# show all news
@ app.route('/news', methods=['GET', 'POST'])
def getAllNews():
    all_news = News.query.all()
    return news_many_schema.jsonify(all_news)


# add news
@ app.route('/addNews', methods=['POST'])
def create_News():
    title = request.json['title']
    content = request.json['content']
    description = request.json['description']
    date = request.json['date']
    url = request.json['url']
    imageUrl = request.json['imageUrl']
    category = request.json['category']

    # constructing news details
    news_details = News(title, content, description,
                        date, url, imageUrl, category)

    # adding news to database and then commit
    databaseObj.session.add(news_details)
    databaseObj.session.commit()

    return news_one_schema.jsonify(news_details)


# get existing news details
@ app.route('/news/<title>', methods=['GET', 'POST'])
def getSingleNews(title):
    news = News.query.filter_by(title=title).first()
    if(row2dict(news)["title"] == title):
        return jsonify(row2dict(news))
    else:
        return jsonify({"message": "Selected news doesn't exist."})


# show categorized newsw;
@ app.route('/news/category/<category>', methods=['GET'])
def getCatNews(category):
    news = News.query.filter_by(category=category).all()
    # print(news)
    return news_many_schema.jsonify(news)


# delete news
@ app.route('/news/delete/<title>', methods=['DELETE'])
def deleteNews(title):
    read_title = request.json["title"]
    news = News.query.filter_by(title=request.json["title"]).first()
    databaseObj.session.delete(news)
    databaseObj.session.commit()

    return jsonify({"message": f"News with title '{read_title}' has been deleted successfully!"})




##################################################################### Opportunities   ################################################################################

    # class for opportunity which accepts our database model
class Opportunity(databaseObj.Model):
    # details for creating the database

    # id = databaseObj.Column(databaseObj.Integer,
    #                         primary_key=True, autoincrement=True)
    __tablename__ = 'opportunity'
    title = databaseObj.Column(databaseObj.String(
        500), primary_key=True, nullable=False)
    content = databaseObj.Column(databaseObj.String(5000), nullable=False)
    description = databaseObj.Column(databaseObj.String(50000), nullable=False)
    date = databaseObj.Column(databaseObj.String(50), nullable=False)
    url = databaseObj.Column(databaseObj.String(500), nullable=False)
    imageUrl = databaseObj.Column(databaseObj.String(500), nullable=False)
    category = databaseObj.Column(databaseObj.String(500), nullable=False)

    # a constructor to insert opportunity details
    def __init__(self,  title, content, description, date, url, imageUrl, category):
        self.title = title
        self.content = content
        self.description = description
        self.date = date
        self.url = url
        self.imageUrl = imageUrl
        self.category = category


# opportunity schema
class OpportunitySchema(ma.Schema):
    class Meta:
        fields = ('id', 'title', 'content', 'description', 'date',
                  'url', 'imageUrl', 'category')


# init schema
opportunity_one_schema = OpportunitySchema()
opportunity_many_schema = OpportunitySchema(many=True)


# all my routes
# show all opportunity
@ app.route('/opportunity', methods=['GET', 'POST'])
def getAllOpportunity():
    all_opportunity = Opportunity.query.all()
    return opportunity_many_schema.jsonify(all_opportunity)


# add opportunity
@ app.route('/addOpportunity', methods=['POST'])
def create_Opportunity():
    title = request.json['title']
    content = request.json['content']
    description = request.json['description']
    date = request.json['date']
    url = request.json['url']
    imageUrl = request.json['imageUrl']
    category = request.json['category']

    # constructing opportuntiy details
    opportunity_details = Opportunity(title, content, description,
                                      date, url, imageUrl, category)

    # adding opportunity to database and then commit
    databaseObj.session.add(opportunity_details)
    databaseObj.session.commit()

    return opportunity_one_schema.jsonify(opportunity_details)


# get existing opportunity details
@ app.route('/opportunity/<title>', methods=['GET', 'POST'])
def getSingleOpportunity(title):
    opportunity = Opportunity.query.filter_by(title=title).first()
    if(row2dict(news)["title"] == title):
        return jsonify(row2dict(opportunity))
    else:
        return jsonify({"message": "Selected opportunity doesn't exist."})


# show categorized opportunity;
@ app.route('/opportunity/category/<category>', methods=['GET'])
def getCatOpportunity(category):
    opportunity = Opportunity.query.filter_by(category=category).all()
    # print(news)
    return opportunity_many_schema.jsonify(opportunity)


# delete opportunity
@ app.route('/opportunity/delete/<title>', methods=['DELETE'])
def deleteOpportunity(title):
    read_title = request.json["title"]
    opportunity = Opportunity.query.filter_by(
        title=request.json["title"]).first()
    databaseObj.session.delete(opportunity)
    databaseObj.session.commit()

    return jsonify({"message": f"Opportunity with title '{read_title}' has been deleted successfully!"})


# Run server start
if __name__ == '__main__':
    databaseObj.create_all()
    # app.run(debug=True)
    app.run()
