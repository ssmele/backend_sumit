from flask import Flask,jsonify, request
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from models import User, Photo, Destination, Sumit
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from google.cloud import storage
import datetime

CLOUD_STORAGE_BUCKET = 'sumit_images'
SQLALCHEMY_DATABASE_DEBUG_URI = 'mysql+pymysql://root:@104.197.242.244:3306/sumit?unix_socket=/cloudsql/sumit-149304:sumit'
SQLALCHEMY_DATABASE_PROD_URI = 'mysql+mysqldb://root:@/sumit?unix_socket=/cloudsql/sumit-149304:us-central1:sumit'

engine = create_engine(SQLALCHEMY_DATABASE_DEBUG_URI)
Session = sessionmaker(bind=engine)

app = Flask(__name__)


def dest_to_json(dest):
    return dict(name=dest.name,
                did = dest.did,
                latitude=dest.latitude,
                longitude= dest.longitude,
                points = dest.points,
                elevation = dest.elevation)

def user_to_json(user):
    return dict(uid=user.uid,
                username=user.username,
                elevation=user.elevation,
                points=user.points)

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
            return jsonify({"statusCode": 2, "desc": "Username already exists", "uid":cur_user.uid}),200

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

@app.route('/create_sumit', methods=['POST'])
def create_sumit():
    try:
        db_session = Session()
        queryParams = request.form
        if queryParams.viewkeys() & {'uid', 'did'}: #'time'}:
            uid = queryParams.get('uid')
            did = queryParams.get('did')
            #time = queryParams.get('time')
        else:
            return jsonify({"statusCode": 1, "desc": "Invalid params given."}), 400

        cur_sumit = db_session.query(Sumit).filter_by(uid=uid,did=did).first()
        if cur_sumit is not None:
            return jsonify({"statusCode": 1, "desc": "User has already sumited."}),409

        new_sumit = Sumit(uid=uid,
                         did=did,
                         time=datetime.datetime.now())
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

@app.route('/sumits_by_uid', methods=['GET'])
def get_sumits_by_uid():
    try:
        db_sesssion = Session()
        queryParams = request.args
        if 'uid' in queryParams:
            uid = queryParams.get('uid')
        else:
            return jsonify({"statusCode": 1, "desc": "Invalid params given."}), 400

        cur_user = db_sesssion.query(User).filter_by(uid=uid).first()
        if cur_user is None:
            return jsonify({"statusCode": 1, "desc": "No user with that uid"}), 200

        sumits = db_sesssion.query(Sumit, Destination).filter(uid == uid).filter(Destination.did == Sumit.did)

        json_return = []
        for sumit in sumits:
            json_return.append(dest_to_json(sumit.Destination))

        return jsonify({"statusCode": 0, "desc": "All destinations sumited by user.", "user":user_to_json(cur_user), "destinations": json_return})

    except Exception, e:
        db_sesssion.rollback()
        return jsonify({"statusCode": 1, "desc": "Error checking if user is verified: " + str(e)}), 500
    finally:
        db_sesssion.close()



@app.route('/destinations', methods=['GET'])
def get_destinations():
    try:
        db_session = Session()

        destinations = db_session.query(Destination).all()
        json_return = []
        for destination in destinations:
            json_return.append(dest_to_json(destination))

        return jsonify({"statusCode": 0, "desc": "Success in sumiting", "destinations":json_return})

    except Exception, e:
        db_session.rollback()
        return jsonify({"statusCode": 1, "desc": "Error checking if user is verified: " + str(e)}), 500
    finally:
        db_session.close()


# [START upload]
@app.route('/upload', methods=['POST'])
def upload():
    """Process the uploaded file and upload it to Google Cloud Storage."""
    uploaded_file = request.files.get('file')

    if not uploaded_file:
        return 'No file uploaded.', 400

    # Create a Cloud Storage client.
    gcs = storage.Client()

    # Get the bucket that the file will be uploaded to.
    bucket = gcs.get_bucket(CLOUD_STORAGE_BUCKET)

    # Create a new blob and upload the file's content.
    blob = bucket.blob(uploaded_file.filename)

    blob.upload_from_string(
        uploaded_file.read(),
        content_type=uploaded_file.content_type
    )

    # The public URL can be used to directly access the uploaded file via HTTP.
    return blob.public_url
# [END upload]


if __name__ == '__main__':
    app.run(debug=True)
