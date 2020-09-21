import time

from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
from waitress import serve
import cv2
import numpy as np
from tensorflow.keras.models import load_model

import hddUsage


app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 512 * 1024 * 5

last_executed = 0


def predict_images(image_size, image):
    size = image_size
    new_model = load_model("models/nsfw_classifier_v9.h5")
    test = image
    test_img = cv2.imread(test, cv2.IMREAD_UNCHANGED)
    test_img_re = cv2.resize(test_img, (size, size), interpolation=cv2.INTER_AREA)
    print(test_img.shape)
    test_img = np.expand_dims(test_img_re, axis=0)
    print(test_img.shape)
    raw = new_model.predict(test_img)
    result = raw > 0.5
    return result[0][0]


@app.route('/upload', endpoint='upload_file')
def upload_file():
    space_free = hddUsage.get_free_space_mb(".")
    print("Disk free : {}".format(space_free))
    if space_free > 40000:
        return render_template('upload2.html')
    else:
        return render_template('space_error.html')


@app.route('/uploader', methods=['GET', 'POST'], endpoint='upload_file2')
def upload_file():
    global last_executed
    age = time.time() - last_executed
    # print("Age : {}".format(age))
    if request.method == 'POST' and age >= 6:
        f = request.files['file']
        # print(f.filename)
        try:
            if request.files['file'].filename == '':
                return render_template('upload2.html')
            else:
                time_var = int(time.time())
                f.save("images/{}_{}.{}".format(secure_filename(f.filename).split(".")[0], time_var, secure_filename(f.filename).split(".")[1]))
                last_executed = time.time()
                is_nsfw = predict_images(306, "images/{}_{}.{}".format(secure_filename(f.filename).split(".")[0], time_var, secure_filename(f.filename).split(".")[1]))
                if is_nsfw:
                    return 'Picture is not safe for work!'
                else:
                    return 'Picture is probably safe for work!'
        except Exception as e:
            # print("Size : {}".format(f.content_length))
            return app_handle_413(e)
    elif age < 60:
        return 'Time since last operation executed is less than 1 Minute :: Wait for {} Seconds, Please wait.'.format(60 - int(age))


@app.errorhandler(413)
@app.errorhandler(RequestEntityTooLarge)
def app_handle_413(e):
    return 'File Too Large :: {}'.format(str(e)), 413


if __name__ == '__main__':
    # app.run(debug=False)
    serve(app, host='0.0.0.0', port=5000)
