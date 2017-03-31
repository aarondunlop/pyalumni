from flask import *
from flask_bootstrap import Bootstrap
from flask_login import * #LoginManager, login_user, logout_user, login_required, current_user
from flask_images import Images
import csv
import io
import shutil
import re
import sys

import logging
logging.basicConfig()

#from flask.ext.login import
#from flask import Flask, request, redirect, url_for

from util import *
from forms import *
from config import *
from models import *

reload(sys)
sys.setdefaultencoding('utf-8')

app = Flask(__name__)
Bootstrap(app)
app.secret_key = app_secret
app.salt = app_salt

login_manager = LoginManager()
login_manager.init_app(app)

UPLOAD_FOLDER = '/var/www/pyalumni/app/static/images/students/'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['IMAGES_CACHE'] = '/var/www/pyalumni/app/static/images/students/resized'
images = Images(app)

error=None

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@login_manager.user_loader
def load_user(session_token):
    try:
        userid=s.unsign(session_token, max_age=900)
        user=db_session.query(User).filter_by(id=userid).first()
    except:
        #return redirect(url_for('logout', next=request.url))
        return None

    return user

@login_manager.unauthorized_handler
def unauthorized():
    print('not auth')
    return redirect(url_for('login', next=request.url))

def check_admin(view):
    @functools.wraps(view)
    def inner(*args, **kwargs):
        print('checking admin.')
        if current_user.admin:
            return view(*args, **kwargs)
        else:
            return redirect(url_for('index', next=request.url))
            return None #redirect(url_for('login'))
    return inner

def check_user_or_admin(id, current_user):
    #print(id, current_user, current_user.email)
    try:
        user=db_session.query(User).filter_by(id=id, email=current_user.email).first()
        if user or current_user.admin:
            print('either user, or admin.')
    except:
        print('not ok.')

    #if current_user.admin:
    return 'ok'

#from forms import UserPasswordForm
#from models import User
#from util import ts, SendEmail

#s=TimestampSigner(app.secret_key, salt=app.salt)
#ts = URLSafeTimedSerializer(app.secret_key)
#from app import app

#login_manager = LoginManager()
#login_manager.init_app(app)

#@login_manager.user_loader
#def load_user(session_token):
#    return db_session.query(User).filter_by(session_token=session_token).first()

@app.route('/user/reset', methods=["GET", "POST"])
def reset():
    form = UserPasswordForm()
    #if form.validate_on_submit():
    if request.method == 'POST' and form.validate():
        #user = User.query.filter_by(email=form.email.data).first_or_404()
        user = db_session.query(User).filter_by(email=email).first()

        email = SendEmail(to=user.email, subject='Password reset requested.')
        email.html(html)
        email.send()

        # Here we use the URLSafeTimedSerializer we created in `util` at the
        # beginning of the chapter
        token = ts.dumps(user.email, salt='recover-key')

        recover_url = url_for(
            'reset_with_token',
            token=token,
            _external=True)

        html = render_template(
            'email/recover.html',
            recover_url=recover_url)

        # Let's assume that send_email was defined in myapp/util.py
        send_email(user.email, subject, html)

        return redirect(url_for('index'))
    return render_template('email/recover.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    next = get_redirect_target()
    form = UserLoginForm(request.form)
    ph = PasswordHasher()
    if request.method == 'POST':# and form.validate():
        #try:
            q = db_session.query(User).filter_by(email=form.email.data).first()
            #print(form.email.data, form.password.data, q.email_confirmed)
            if q.email_confirmed:
                q.session_token = s.sign(str(q.id))
                db_session.commit()
                ph.verify(q.password, form.password.data)
            login_user(q, remember=True)
            return redirect_back('index')
        #except:
            print('Email or password does not match. Try again.')

    return render_template('login.html', form=form, error=error)

@app.route('/logout', methods=['GET'])
#@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/user/')
@login_required
@check_admin
def userlist():
    #Add create button, redirect to user/edit wo params.
    if request.method == 'GET':
        values=['email', 'admin', 'id']
        users = db_session.query(User.email, User.admin, User.id).all()#(User.email, User.id)
        for user in users:
            print user
        resultset = [dict(zip(values, row)) for row in users]
    return render_template('userlist.html', users=resultset)

@app.route('/student/')
@login_required
@check_admin
def studentlist():
    if request.method == 'GET':
        values=['email', 'id', 'name', 'year']
        students = db_session.query(Student.email, Student.id, (Student.firstname + '.' + Student.lastname), Student.class_year).all()#(Student.email, Student.id)
        resultset = [dict(zip(values, row)) for row in students]
    return render_template('studentlist.html', students=resultset)

@app.route('/user/delete')
@login_required
@check_admin
def userdelete():
    if request.args.get('id'):
        opt = request.args.get('id').split(",")
    for id in opt:
        db_session.query(User).filter_by(id=id).delete()
        db_session.commit()
    return redirect(url_for('userlist'))

@app.route('/student/delete')
@login_required
@check_admin
def studentdelete():
    if request.args.get('id'):
        opt = request.args.get('id').split(",")
    for id in opt:
            db_session.query(Student).filter_by(id=id).delete()
            db_session.commit()
    return redirect(url_for('studentlist'))

@app.route('/user/edit', methods=['GET', 'POST'])
@login_required
#@check_admin
def useredit():
    opt = []
    record=None
    id=None
    form = UserEditForm(request.form)

    try:
        opt = request.args.get('id').split(",")
        id=next(iter(opt))
        if not opt:
            return redirect(url_for('index'))
    except:
        error.append('No ID was present. Aborting.')
        return redirect(url_for('index'))

    check_user_or_admin(id, current_user)

    try:
        record = db_session.query(User).filter_by(id=id).first()
        if record == None:
            if exit_if_last(id, opt):
                return redirect(url_for('index'))
    except:
        error.append('User does not exist.')
        if exit_if_last(id, opt):
            return redirect(url_for('index'))

    if request.method == 'GET':
        if record is not None:
            record = db_session.query(User).filter_by(id=id).first()
            form = UserEditForm(obj=record)
        else:
            form = UserEditForm(request.form)
        return render_template('useredit.html', form=form, error=error, id=",".join(opt))

    if request.method == 'POST' and form.validate():
        #Insert check here for admin, or to verify user is editing his acct.
        if record:
            form.populate_obj(record)
            print record.admin
        else:
            record = User()
            db_session.add(record)
        form.populate_obj(record)
        db_session.commit()
        if exit_if_last(id, opt):
            return redirect(url_for('userlist'))
        else:
            return redirect(url_for('useredit', error=error, id=",".join(opt)))

@app.route('/user/create', methods=['GET', 'POST'])
@login_required
@check_admin
def studentcreate():
    form = UserEditForm()

    if request.method == 'GET':
        return render_template('useredit.html', form=form, error=error)

    if request.method == 'POST' and form.validate():
        record = db_session.query(User).filter_by(email=form.email.data).first()
        if record:
            error.append('User already exists.')
        else:
            record = User()
            db_session.add(record)
            form.populate_obj(record)
            db_session.commit()
    return redirect(url_for('useredit'))

@app.route('/student/edit', methods=['GET', 'POST'])
@login_required
@check_admin
def studentedit():
    opt = []
    record=None
    tempid=None
    id=None
    form = StudentEditForm(request.form)

    try:
        opt = request.args.get('id').split(",")
        id=next(iter(opt))
        if not opt:
            return redirect(url_for('index'))
    except:
        error.append('No ID was present. Aborting.')
        return redirect(url_for('index'))

    try:
        record = db_session.query(Student).filter_by(id=id).first()
        if record == None:
            if exit_if_last(id, opt):
                return redirect(url_for('index'))
    except:
        error.append('User does not exist.')
        if exit_if_last(id, opt):
            return redirect(url_for('index'))

    if request.method == 'GET':
        if record is not None:
            #record = db_session.query(Student).filter_by(id=tempid).first()
            form = StudentEditForm(obj=record)
        else:
            form = StudentEditForm(request.form)
        return render_template('studentedit.html', form=form, error=error, id=",".join(opt))

    if request.method == 'POST' and form.validate():
        print(record, id)

        #Insert check here for admin, or to verify student is editing his acct.
        if record:
            form.populate_obj(record)
        else:
            record = Student()
            db_session.add(record)
        form.populate_obj(record)

        #record.name="%s.%s" % (form.firstname.data, form.lastname.data)
        db_session.commit()
        if exit_if_last(id, opt):
            return redirect(url_for('studentlist'))
        else:
            return redirect(url_for('studentedit', id=",".join(opt)))

@app.route('/student/create', methods=['GET', 'POST'])
@login_required
@check_admin
def studentcreate():
    form = StudentEditForm()

    if request.method == 'GET':
        return render_template('studentedit.html', form=form, error=error)

    if request.method == 'POST' and form.validate():
        record = db_session.query(Student).filter_by(email=form.email.data).first()
        if record:
            error.append('User already exists.')
        else:
            record = Student()
            db_session.add(record)
            form.populate_obj(record)
            db_session.commit()
    return redirect(url_for('studentedit'))

@app.route('/user/pass/<int:id>', methods=['GET', 'POST'])
@login_required
def changepass(id):
    record = db_session.query(User).filter_by(id=id).first()
    form = UserPasswordForm()
    if request.method == 'POST' and form.validate():
        ph = PasswordHasher()
        password = ph.hash(form.password.data)
        record.password=password
        db_session.commit()
        return redirect(url_for('pickstudent',id=id))
    if request.method == 'GET' and form.validate():
        return render_template('changepass.html', form=form, error=error, userid=userid)

@app.route('/pick', methods=['GET', 'POST'])
@login_required
def pickstudent():
    def exit_if_last(id, opt):
        try:
            opt.pop(0)
        except:
            return True
        if opt is None or not opt:
            print('opt is empty')
            return True
        return False

    #print(request.args)
    opt=[]
    error=[]
    year=None
    try:
        opt = request.args.get('id').split(",")
        id=next(iter(opt))
        if not opt:
            return redirect(url_for('index'))
    except:
        error.append('No ID was present. Aborting.')
        return redirect(url_for('index'))

    try:
        user = db_session.query(User).filter_by(id=id).first()
        year = int(user.class_year)
        if user == None:
            if exit_if_last(id, opt):
                return redirect(url_for('index'))
    except:
        error.append('User does not exist.')
        print(error)
        if exit_if_last(id, opt):
            return redirect(url_for('index'))

    print(error)
        #Insert check here for admin, or to verify student is editing his acct.

    form = PickStudentForm(request.form)
    #Don't let someone snag a used record!
    form.students.choices = [(student.id, ('%s %s' % (student.firstname, student.lastname))) for student in db_session.query(Student).filter_by(class_year=year, userid=None)]
    form.students.choices.insert(0, (-1, "Create a new record."))

    #Already tied? Back to student edit form. This works.
    temprecord=db_session.query(Student).filter_by(userid=id).first()
    if temprecord:
        if exit_if_last(id, opt):
            return redirect(url_for('index'))
        return redirect(url_for('pickstudent', error=error, id=",".join(opt)))

    if request.method == 'GET':
        print(id, opt, user)
        return render_template('pickstudent.html', form=form, id=",".join(opt), email=user.email)

    if request.method == 'POST': # and form.validate():
        studentid=int(form.students.data)
        print('studentid is %s' % studentid)
        #choice can be 0. none maybe?
        if studentid == -1:
            print('new record is being created %s' % form.students.data)
            print('dumping out.')
            return redirect(url_for('studentedit'))

        studentid=form.students.data
        studentrecord = db_session.query(Student).filter_by(id=studentid).first()

        if studentrecord:
            studentrecord.userid=id
        db_session.commit()
        #Check to see if done, redirect to studentedit if so. Else, back to tie. This works.
        if exit_if_last(id, opt):
            print('Last record, exiting.')
            return redirect(url_for('index'))

    return redirect(url_for('pickstudent', error=error, id=",".join(opt)))

#@app.route('/user/list')
#def userjson():
#    values=['email', 'id']
#    users = db_session.query(User.email, User.id).all()#(User.email, User.id)
#    resultset = [dict(zip(values, row)) for row in users]
#    return(json.dumps(resultset))
#
#@app.route('/student/list')
#def studentjson():
#    values=['email', 'id']
#    students = db_session.query(Student.name, Student.id).all()
#    resultset = [dict(zip(values, row)) for row in students]
#    return(json.dumps(resultset))

@app.route('/secret', methods=['GET'])
@login_required
@check_admin
def secret():
    print('ok')
    return('ok')
    #return 'This is a secret page. You are logged in as {}'.format(current_user.username)

@app.route('/user/confirm/<token>')
def confirm_email(token):
    try:
        email = ts.loads(token, salt="email-confirm-key", max_age=86400)
    except:
        abort(404)

    user = db_session.query(User).filter_by(email=email).first()
    user.email_confirmed = True

    db_session.add(user)
    db_session.commit()

    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    try:
        form = UserRegisterForm(request.form)
        if request.method == 'POST' and form.validate():
            user = User()

            ph = PasswordHasher()

            user.email = form.email.data
            user.password = ph.hash(form.password.data)
            user.class_year = form.class_year.data

            db_session.add(user)
            db_session.commit()

            subject = "Confirm your email"
            token = ts.dumps(user.email, salt='email-confirm-key')
            confirm_url = url_for(
                'confirm_email',
                token=token,
                _external=True)

            html = render_template(
                'email/activate.html',
                confirm_url=confirm_url)
            #print(html)
            email = SendEmail(to=user.email, subject=subject)
            email.html(html)
            email.send()

            return redirect(url_for("index"))

    except Exception as e:
        #return(str(e))
        print('whoops.')

    return render_template('register.html', form=form, error=error)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/classes', methods=['GET'])
def classes():
    if request.method == 'GET':
        years = sorted([year for year, in db_session.query(Student.class_year.distinct()).all()])
    return render_template('classes.html', years=years)

@app.route('/classes/<int:selected_year>', methods=['GET', 'POST'])
def show_year(selected_year):
    if request.method == 'GET':
        student_list=[]
        #students = db_session.query(Student.lastname, (Student.firstname + '.' + Student.lastname), Student.images).filter_by(class_year = selected_year)#(Student.email, Student.id)
        students = Student.show_students_by_year(class_year = selected_year)
        values=['lastname', 'name', 'images', 'id']
        resultset = list([dict(zip(values, row)) for row in students])
    student_list=sorted(resultset, key=operator.itemgetter('lastname'))
    return render_template('show_class.html', year=selected_year, students=resultset)
    #return render_template('show_class.html', year=2022, students=resultset)

@app.route('/classes/<int:selected_year>/<string:name>')
def show_user(selected_year, name):
        #try:
            student={}
            firstname = name.split('.')[0]
            lastname = name.split('.')[1]
            students = Student.show_students(class_year = selected_year, firstname=firstname, lastname=lastname)
            student=students[0]
            filedir='%s%s/' % (UPLOAD_FOLDER,students[0].id)
            print filedir
            #resized_url = resize('https://pyalumni.dunlops.us/static/images/students/7/Screen_Shot_2017-03-08_at_9.06.11_PM.png', '300x300', fill=1)
            #print resized_url
            images=[]
            if os.path.isdir(filedir):
                images = [ file for file in os.listdir(filedir) ]
                print(list(images))
        #except:
            #return redirect(url_for('index'))
            return render_template('show_users.html', student=student, images=images, id=student.id)

@app.route('/upload/<int:id>', methods=['GET', 'POST'])
@login_required
def uploaded_file(id):
    student = db_session.query(Student).filter_by(id=id).first()#(Student.email, Student.id)
    user = db_session.query(User).filter_by(email=current_user.email).first()#(Student.email, Student.id)
    #print ('student.userid is %s, cu is %s, user.id is %s' % (student.userid, current_user, user.id))
    if user.id == student.userid or user.is_admin:
        print (id, student.id, student.userid, current_user.id, current_user.admin)
    else:
        print('does not match.')
        return redirect(url_for('index'))

    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filepath = app.config['UPLOAD_FOLDER'] + '/' + str(id) + '/'
            filename = secure_filename(file.filename)
            print student
            print student.images
            imagepath=filepath + filename
            print imagepath
            try:
                os.stat(filepath)
            except:
                os.mkdir(filepath)
            file.save(os.path.join(filepath, filename))
            student.images.append(imagepath)
            return redirect(url_for('uploaded_file',filename=filename,id=id))
    return render_template('upload.html', id=id)

@app.route('/student/image/<int:id>', methods=['GET', 'POST'])
@login_required
def change_image(id):
    student = db_session.query(Student).filter_by(id=id).first()#(Student.email, Student.id)
    user = db_session.query(User).filter_by(email=current_user.email).first()#(Student.email, Student.id)

    if user.id == student.userid or user.is_admin:
        #print (id, student.id, student.userid, current_user.id, current_user.admin)
        a=None
    else:
        print('does not match.')
        return redirect(url_for('index'))
    filepath='%s/%s' % ('/var/www/pyalumni/app/static/images/students', id)

    if os.path.isdir(filepath):
        images = [ file for file in os.listdir(filepath) ]
        if images is not None:
            form = StudentChangeImage(images=images)
            form.image.choices = [(image, image) for image in images]
            #print(list(form.image.choices))
        else:
            form = StudentChangeImage()
    else:
        form = StudentChangeImage()
        #except:
            #return redirect(url_for('index'))
    if request.method == 'POST':
            print student.images
            print student.id
            #print 'ok'
            form = StudentChangeImage(request.form)

            if form.deletephoto.data:
                imagename=form.image.data
                imagepath="/".join([filepath, imagename])
                print imagepath
                try:
                    os.remove(imagepath)
                except OSError:
                    pass

            if form.setphoto.data:
                print form.image.data
                student.images=form.image.data
                db_session.commit()

            return redirect(url_for('change_image', id=id))


    return render_template('change_image.html', form=form, id=id)


@app.route('/upload/student', methods=['GET', 'POST'])
@login_required
def upload_student():
    students = db_session.query(Student.id,Student.firstname,Student.lastname,Student.class_year).all()#(Student.email, Student.id)
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file:
            input_file = csv.reader(request.files['file'], delimiter='|')
            keys=['name', 'firstname', 'lastname', 'bio', 'birthday', 'businesswebsite', 'photosite', 'website', 'employer', 'kids', 'location', 'email', 'obit', 'spouse', 'updated', 'class_year', 'image']
            records=[]
            for row in input_file:
                firstname = row[0].split('.')[0]
                lastname = row[0].split('.')[1]
                values=[row[0], firstname, lastname, row[12], row[8], row[6], row[4], row[7], row[11], row[10], row[4], row[2], row[13], row[9], row[3], int(row[16]), row[15]]
                line=([dict(zip(keys, values))])
                records.append(line)
            Student.process_updates(records)
    return render_template('upload_student.html')

@app.route('/upload/images', methods=['GET', 'POST'])
@login_required
def upload_images():
    students = db_session.query(Student).all()#(Student.email, Student.id)
    filedir='/var/www/pyalumni/app/images'
    #if request.method == 'POST':
#    for student in students:
    if os.path.isdir(filedir):
        dirs = [ dir for dir in os.listdir(filedir) ]
        for imageyear in dirs:
            if int(imageyear) > 26 and int(imageyear) <= 99:
                fullimageyear=int(imageyear)+1900
            elif int(imageyear) < 27 and int(imageyear) >= 00:
                fullimageyear=int(imageyear)+2000
            else:
                fullimageyear=0
            #print fullimageyear
            dirpath='/'.join([filedir, imageyear])
            images = [ file for file in os.listdir(dirpath) ]
            name=''
            for image in images:
                #print image
                match = re.match(r"(.*)\..*\..*", image)
                #print match.group(1)
                if match is not None:
                    name=match.group(1)
                    print name
                fullpath='%s/%s' % (dirpath, image)
                #print fullpath
                for student in students:
                    if student.class_year==fullimageyear and student.name == name:
                        newpath='%s/%s' % ('/var/www/pyalumni/app/static/images/students', student.id)
                        newimg='%s/%s' % (newpath, image)
                        if not os.path.exists(newpath):
                            os.makedirs(newpath)
                        #print(newpath)
                        if not os.path.exists(newimg):
                            shutil.copy(fullpath, newimg)
                        showname='%s.old.jpg' % (name)
                        if showname is not None:
                            student.images=showname
                            #print(fullpath, newpath)
        db_session.commit()

    return render_template('upload_images.html')
