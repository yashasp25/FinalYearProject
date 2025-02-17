from flask import redirect, render_template, Flask,flash,request,session
from flask_sqlalchemy import SQLAlchemy
from flask.helpers import url_for
import json,os
from flask_login import UserMixin
from flask_login import login_required,logout_user,login_user,login_manager,LoginManager,current_user
from werkzeug.security import generate_password_hash,check_password_hash
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array, load_img
import numpy as np
import io
from PIL import Image
from werkzeug.utils import secure_filename

model = load_model("model_inception.h5")

CLASSES = ['Potato___Early_blight', 'Potato___Late_blight', 'Potato___healthy',
                'Tomato_Early_blight', 'Tomato_Late_blight', 'Tomato_healthy',
                'unknown']

DESCRIPTIONS = {
    'Potato___Early_blight': (
        "Potato early blight is a fungal disease caused by *Alternaria solani*, a pathogen that thrives in warm, humid conditions. "
        "It primarily affects older leaves, where it causes brown or black spots that often develop into concentric ring patterns, resembling a target. "
        "As the disease progresses, it can cause significant defoliation, reducing the plant's ability to photosynthesize and produce healthy tubers. "
        "Symptoms are often more pronounced on stressed plants or those lacking adequate nutrients. "
        "\n\n"
        "Farmers can manage early blight through a combination of cultural and chemical methods. Crop rotation, removal of infected plant debris, "
        "and maintaining optimal plant nutrition are essential preventive measures. In severe cases, fungicides containing active ingredients like chlorothalonil or mancozeb may be applied to limit the spread of the disease. "
        "Using resistant potato varieties is another effective strategy for minimizing the impact of early blight on yield and quality."
    ),
    'Potato___Late_blight': (
        "Potato late blight is one of the most notorious plant diseases in history, responsible for the devastating Irish Potato Famine. "
        "Caused by the oomycete pathogen *Phytophthora infestans*, late blight spreads rapidly under cool, wet conditions. "
        "It manifests as dark, water-soaked lesions on leaves, stems, and tubers, often accompanied by white fungal growth on the undersides of leaves. "
        "If untreated, the disease can destroy entire fields in just a few days, leading to massive crop losses."
        "\n\n"
        "Management of late blight requires vigilance and a multifaceted approach. Regular scouting for early symptoms and immediate removal of infected plants can help contain outbreaks. "
        "Fungicides such as copper-based compounds or systemic options like metalaxyl are commonly used to prevent and control infections. "
        "Farmers are encouraged to plant certified disease-free seed potatoes and rotate crops to break the pathogen's lifecycle. "
        "Storing tubers in a cool, dry environment also reduces post-harvest losses due to late blight."
    ),
    'Potato___healthy': (
        "The potato plant appears healthy and free from any visible signs of disease or pest damage. "
        "Healthy potato plants have strong, upright stems, vibrant green foliage, and a uniform growth pattern. "
        "The plant's productivity is optimal under these conditions, ensuring a high yield of quality tubers that meet market standards."
        "\n\n"
        "To maintain the health of potato plants, proper agricultural practices are essential. "
        "This includes ensuring balanced fertilization with nitrogen, phosphorus, and potassium, as well as timely irrigation to prevent water stress. "
        "Farmers should also monitor for early signs of diseases or pests and take preventive measures such as crop rotation, field sanitation, and pest control. "
        "Healthy plants are a testament to good farm management practices and contribute significantly to the farmer's overall profitability."
    ),
    'Tomato_Early_blight': (
        "Early blight in tomatoes is a common disease caused by the fungus *Alternaria solani*. "
        "It typically begins as small, dark spots on older leaves, which then develop into larger lesions with characteristic concentric rings. "
        "Severely infected leaves may yellow and drop prematurely, reducing the plant's capacity to support fruit development. "
        "In some cases, early blight can also affect stems and fruits, leading to further yield losses."
        "\n\n"
        "Preventing early blight involves maintaining good field hygiene by removing infected plant debris and avoiding overhead irrigation, which can spread fungal spores. "
        "Resistant tomato varieties are an excellent choice for areas prone to early blight outbreaks. "
        "Fungicides may be applied as a protective measure, especially during warm, humid weather. "
        "Providing adequate spacing between plants also improves air circulation, reducing the chances of disease spread."
    ),
    'Tomato_Late_blight': (
        "Tomato late blight, caused by *Phytophthora infestans*, is a highly destructive disease that can decimate crops within days under favorable conditions. "
        "The disease starts as irregular, dark, water-soaked lesions on leaves and stems. "
        "As it progresses, these lesions enlarge, turn brown, and may be surrounded by a pale halo. "
        "Infected fruits develop brown, sunken spots and are often covered with a whitish fungal growth, rendering them unmarketable."
        "\n\n"
        "Effective management of late blight requires an integrated approach. Resistant tomato varieties are a critical first step in preventing severe outbreaks. "
        "Farmers should practice crop rotation and avoid planting tomatoes in the same field as potatoes, as both crops share this pathogen. "
        "Fungicides, particularly systemic ones, can provide protection when applied early in the season. "
        "Good drainage and reducing leaf wetness through drip irrigation also minimize the risk of disease development."
    ),
    'Tomato_healthy': (
        "The tomato plant is in excellent health, showing no signs of disease, pest infestation, or environmental stress. "
        "Healthy tomato plants are characterized by their sturdy stems, lush green leaves, and abundant flowering and fruiting. "
        "Such plants are indicative of optimal growing conditions and effective farm management."
        "\n\n"
        "Maintaining healthy tomato plants involves regular monitoring for early signs of issues, balanced fertilization, and proper irrigation practices. "
        "Using well-drained soil and mulching helps retain moisture while preventing waterlogging. "
        "In addition, protecting plants from pests like aphids and whiteflies through natural predators or targeted insecticides ensures their continued growth and productivity. "
        "Healthy plants are vital for achieving high-quality fruit that meets consumer demands."
    ),
    'unknown': (
    "The uploaded image does not match any of the known classes. This could be due to the image being of poor quality, "
    "containing an unknown type of plant or disease, or the model's inability to recognize it. "
    "\n\n"
    "Please ensure the image is clear and represents a potato or tomato plant. If you believe this is an error, try uploading another image."
)

}

#my app initialization
local_server = True
app = Flask(__name__)
app.secret_key="yashasp"


with open('config.json','r') as e:
    params=json.load(e)["params"]

#set login manager(for getting unique user access)
login_manager=LoginManager(app)
login_manager.login_view='login'

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# app.config['SQLALCHEMY_DATABASE_URI']='mysql://username:password@localhost/datbasename'
app.config['SQLALCHEMY_DATABASE_URI']='mysql://root:@localhost/vegetable'
db=SQLAlchemy(app)#telling what all

class Test(db.Model):
    id=db.Column(db.Integer(),primary_key=True)
    name=db.Column(db.String(40))

class User(db.Model, UserMixin):
    id=db.Column(db.Integer(),primary_key=True)
    user_id=db.Column(db.String(20),unique=True)
    name=db.Column(db.String(20))
    city=db.Column(db.String(20))
    dob=db.Column(db.String(300))

class Dealer(db.Model):
    __tablename__ = 'dealers'
    id = db.Column(db.Integer, primary_key=True)
    dealer_name = db.Column(db.String(100), nullable=False)
    dealer_email = db.Column(db.String(100), unique=True, nullable=False)
    dealer_phone = db.Column(db.String(15), nullable=False)
    license_number = db.Column(db.String(50), unique=True, nullable=False)
    dealer_address = db.Column(db.Text, nullable=False)
    dealer_city = db.Column(db.String(50), nullable=False)
    dealer_state = db.Column(db.String(50), nullable=False, default="Karnataka")
    dealer_postal_code = db.Column(db.String(10), nullable=False)
    additional_notes = db.Column(db.Text, nullable=True)


@app.route("/")

def index():
    return render_template('firsthome.html')

@app.route("/about")
@login_required
def about():
    return render_template('about.html')

def preprocess_image(image_path):
    img = load_img(image_path, target_size=(224, 224))  # Resize to model's expected size
    img = img_to_array(img) / 255.0  # Normalize
    img = np.expand_dims(img, axis=0)  # Add batch dimension
    return img

import random as r
import hashlib

@app.route("/ind", methods=["GET", "POST"])
@login_required
def ind():
    if request.method == "POST":
        if "file" not in request.files:
            return "No file uploaded", 400

        file = request.files["file"]
        if file.filename == "":
            return "No file selected", 400

        filename = secure_filename(file.filename)
        file_path = os.path.join("static", filename)
        file.save(file_path)

        # Image preprocessing function
        def preprocess_image(image_path):
            img = load_img(image_path, target_size=(224, 224))  
            img_array = img_to_array(img) / 255.0  # Normalize pixel values
            return np.expand_dims(img_array, axis=0)  # Add batch dimension

        img = preprocess_image(file_path)

        # Model prediction
        try:
            predictions = model.predict(img)
            print(f"Raw Predictions: {predictions}")

            # Apply softmax to get confidence scores
            predictions = tf.nn.softmax(predictions).numpy()  
            print(f"Softmax Predictions: {predictions}")

            class_index = np.argmax(predictions)
            class_name = CLASSES[class_index]
            confidence_score = np.max(predictions) * 100
            accuracy_text = f"{confidence_score:.2f}%"

        except Exception as e:
            print(f"Model prediction error: {e}")
            return "Error in model prediction", 500

        class_description = DESCRIPTIONS.get(class_name, "No description available.")

        # Show dealers only for diseased plants
        show_dealers = class_name not in ["unknown", "Potato___healthy", "Tomato_healthy"]
        dealers = []

        if show_dealers and current_user.is_authenticated:
            user_city = current_user.city
            dealers = Dealer.query.filter_by(dealer_city=user_city).all()

        return render_template(
            "ind.html",
            prediction=class_name,
            accuracy=accuracy_text,
            description=class_description,
            image_url=file_path,
            dealers=dealers,
            show_dealers=show_dealers
        )

    return render_template("ind.html", prediction=None, description=None, dealers=[], show_dealers=False)

@app.route("/signup", methods=['POST','GET'])
def signup():
    if request.method == "POST":
        user_id = request.form.get('user_id')
        name = request.form.get('name')
        city = request.form.get('city')
        dob = request.form.get('dob')
        encpassword = generate_password_hash(dob)
        user = User.query.filter_by(user_id=user_id).first()
        
        if user:
            flash("User ID already exists", "warning")
            return render_template("usersignup.html")
        
        # Creating a new user instance
        new_user = User(user_id=user_id, name=name, city=city, dob=encpassword)
        # Adding the new user to the database session
        db.session.add(new_user)
        # Committing the transaction to the database
        db.session.commit()
        
        # Direct access without login page
        user1 = User.query.filter_by(user_id=user_id).first()
        if user1 and check_password_hash(user1.dob, dob):
            login_user(user1)
            flash("SignIn Success", 'success')
            return render_template('firsthome.html')

    return render_template('usersignup.html')

@app.route("/login",methods=['POST','GET'])
def login():
    if request.method=="POST":
        user_id=request.form.get('user_id')
        dob=request.form.get('dob')
        user=User.query.filter_by(user_id=user_id).first()

        if user and check_password_hash(user.dob,dob):
            login_user(user)
            flash("Login Success","info")
            return render_template("firsthome.html")
        else:
            flash("Invalid Credentials","danger")
            return render_template("userlogin.html")

    return render_template('userlogin.html')

#logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logout Successfull","info")
    return redirect(url_for('login'))

#admin login
@app.route("/admin",methods=['POST','GET'])
def admin():
    if request.method=="POST":
        username=request.form.get('username')
        password=request.form.get('password')
        if (username==params['user'] and password==params['password']):
            session['user']=username
            flash("Login success","info")
            return render_template("addDealer.html")
        else:
            flash("Invalid Credentials","danger")

    return render_template('admin.html')


@app.route("/addinfo", methods=["POST"])
def add_dealer():
    if request.method == "POST":
        dealer_name = request.form.get("dealer_name")
        dealer_email = request.form.get("dealer_email")
        dealer_phone = request.form.get("dealer_phone")
        license_number = request.form.get("license_number")
        dealer_address = request.form.get("dealer_address")
        dealer_city = request.form.get("dealer_city")
        dealer_state = request.form.get("dealer_state")
        dealer_postal_code = request.form.get("dealer_postal_code")
        additional_notes = request.form.get("additional_notes")

        # Create a new dealer instance
        new_dealer = Dealer(
            dealer_name=dealer_name,
            dealer_email=dealer_email,
            dealer_phone=dealer_phone,
            license_number=license_number,
            dealer_address=dealer_address,
            dealer_city=dealer_city,
            dealer_state=dealer_state,
            dealer_postal_code=dealer_postal_code,
            additional_notes=additional_notes,
        )
        db.session.add(new_dealer)
        db.session.commit()
        flash("Dealer added successfully!", "success")
        return render_template("addDealer.html")  
        # try:
        #     # Add to database session and commit
        #     db.session.add(new_dealer)
        #     db.session.commit()
        #     flash("Dealer added successfully!", "success")
        #     return render_template("addDealer.html")  
        # except Exception as e:
        #     db.session.rollback()
        #     flash(f"Error: {str(e)}", "danger")
        #     return redirect("/admin")

    return render_template("admin.html")

#testing connection
@app.route("/test")
def test():
    try:
        a=Test.query.all()
        print(a)
        return 'Mydatabase is connected'
    except Exception as e:
        print(e)
        return 'My database is not connected'
    

if __name__ == '__main__':
    app.run(debug=True)