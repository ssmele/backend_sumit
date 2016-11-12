from flask import  Flask,jsonify, request
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from models import User, Photo, Destination, Sumit
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

SQLALCHEMY_DATABASE_DEBUG_URI = 'mysql+pymysql://root:@104.197.242.244:3306/sumit?unix_socket=/cloudsql/sumit-149304:sumit'
SQLALCHEMY_DATABASE_PROD_URI = 'mysql+mysqldb://root:@/sumit?unix_socket=/cloudsql/sumit-149304:us-central1:sumit'

engine = create_engine(SQLALCHEMY_DATABASE_PROD_URI)
Session = sessionmaker(bind=engine)

app = Flask(__name__)


@app.route('/hello', methods=['GET'])
def hello_world():
    return "hello"


@app.route('/create_user', methods=['POST'])
def create_user():
    try:
        db_session = Session()
        queryParams = request.form
        if 'username' in queryParams:
            username = queryParams.get('username')
        else:
            return jsonify({"statusCode": 1, "desc": "Invalid params given."}), 400

        cur_user = db_session.query(User).filter_by(username=username).first()
        if cur_user is not None:
            return jsonify({"statusCode": 1, "desc": "Username already exists"}),409

        new_user = User(username=username)
        db_session.add(new_user)
        db_session.flush()

        uid = new_user.uid

        db_session.commit()
        return jsonify({"statusCode": 0, "desc": "Success creating user", "uid": uid})

    # If the query returned no users.
    except NoResultFound:
        return jsonify({"statusCode": 1, "desc": "Did not find user"}), 404
    # If the query returned more than one user.
    except MultipleResultsFound:
        return jsonify({"statusCode": 1,
                        "desc": "To many users found. Something is wrong with the database contact stone the db king."}), 404
    except Exception, e:
        db_session.rollback()
        return jsonify({"statusCode": 1, "desc": "Error checking if user is verified: " + str(e)}), 500
    finally:
        db_session.close()

@app.route('/sumit', methods=['POST'])
def create_user():
    try:
        db_session = Session()
        queryParams = request.form
        if queryParams.viewkeys() & {'uid', 'did','time'}:
            uid = queryParams.get('uid')
            did = queryParams.get('did')
            time = queryParams.get('time')
        else:
            return jsonify({"statusCode": 1, "desc": "Invalid params given."}), 400

        cur_sumit = db_session.query(User).filter_by(uid=uid,did=did).first()
        if cur_sumit is not None:
            return jsonify({"statusCode": 1, "desc": "User has already sumited."}),409

        new_sumit = Sumit(uid=uid,
                         did=did,
                         time=time)
        db_session.add(new_sumit)
        db_session.flush()

        sid = new_sumit.sid

        db_session.commit()
        return jsonify({"statusCode": 0, "desc": "Success in sumiting", "sid": sid})

    # If the query returned no users.
    except NoResultFound:
        return jsonify({"statusCode": 1, "desc": "Did not find user"}), 404
    # If the query returned more than one user.
    except MultipleResultsFound:
        return jsonify({"statusCode": 1,
                        "desc": "To many users found. Something is wrong with the database contact stone the db king."}), 404
    except Exception, e:
        db_session.rollback()
        return jsonify({"statusCode": 1, "desc": "Error checking if user is verified: " + str(e)}), 500
    finally:
        db_session.close()

if __name__ == '__main__':
    app.run(debug=True)
