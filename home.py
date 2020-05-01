from flask import Flask, render_template, request, flash,session,redirect,url_for,make_response
from firebase_admin import credentials, firestore, initialize_app
import re

import random, string

app = Flask(__name__)

app.config['SECRET_KEY'] = '1456780765656546'

cred = credentials.Certificate('service.json')
default_app = initialize_app(cred)
db = firestore.client()

@app.route("/",methods=['GET', 'POST'])
def home():
    try:
        if session['id'].startswith("OTOD"):
            return redirect(url_for("distributor_home"))
        elif session['id'].startswith("OTOA"):
            return redirect(url_for("admin_home"))
        else:
            return redirect(url_for("customer_video"))


    except:

        return render_template("general.html")


#leader to accept the request and forward to distributor
@app.route("/leader_accept",methods=['GET', 'POST'])
def leader_accept():
    user_id=request.form['user_id']
    sign =db.collection('signup')
    n={"approve":"yes"}
    sign.document(user_id).update(n)
    return redirect(url_for("customer_video"))



#customer request accepted by distributor And Customer
#this route is meant to create the DB structure for levels and to the value from Signup to customers colection
@app.route('/cus_req_app',methods=['GET', 'POST'])
def cus_req_app():
    user_id = request.form['user_id']
    sign = db.collection('signup')
    s={"00":0}
    n={user_id:user_id}
    result = sign.document(user_id).get().to_dict()
    sign.document(user_id).delete()
    dis=db.collection("customer")
    dis.document(user_id).set(result)
    #dis.document("OTOD1234").collection("customer").document("OTOC"+str(result['id'])).set(result)
    #db.collection("customer").document("OTOC"+str(result['id'])).set(result)

    if result["leader_id"] == "0":

        try:
            o = db.collection("lev1").document(result['distributor_id'])
            t=o.get().to_dict()
            t1=len(t)
        except:
            t1=0


        if t1>0:
            o.update(n)
            o.update({"00": firestore.DELETE_FIELD})
        else:
            o.set(s)
            o.update(n)
            o.update({"00": firestore.DELETE_FIELD})
        k="lev"+str(2)
        db.collection(k).document(user_id).set(s)
        p={"lev":k}
        dis.document(user_id).update(p)
        return redirect(url_for("distributor_home"))
    else:
        x=db.collection("customer").document(result['leader_id']).get().to_dict()
        k=x['lev']
        try:
            o=db.collection(k).document(result['leader_id'])
            t=o.get().to_dict()
            t1=len(t)
        except:
            t1=0
        if t1>0:
            o.update(n)
            o.update({"00": firestore.DELETE_FIELD})
        else:
            o.set(s)
            o.update(n)
            o.update({"00": firestore.DELETE_FIELD})
        y=int(k[3:])+1
        z="lev"+str(y)
        db.collection(z).document(user_id).set(s)
        p={"lev":z}
        dis.document(user_id).update(p)
        return redirect(url_for("customer_video"))

@app.route('/logout')
def logout():
    session.clear()
    return render_template('general.html')


@app.route('/signin',methods=['POST'])
def signin():


    username = request.form['username']
    password = request.form['password']
    if username.startswith("OTOD"):
        dis = db.collection('distributor')
        result=dis.document(username).get().to_dict()
        k = 0
        try:
            k = len(result)
        except:
            pass

        if k == 0:
            return render_template('general.html', msg='Invalid Username/password')
        else:
            if result['Password']==password:
                session['dis']=result['Name']
                session['id'] = username

                return render_template("distributor/distributor.html")
            else:
                return render_template('general.html', msg='Invalid Username/password')
    elif username.startswith("OTOA"):
        dis = db.collection('admin')
        result = dis.document(username).get().to_dict()
        k = 0
        try:
            k = len(result)
        except:
            pass

        if k == 0:
            return render_template('general.html', msg='Invalid Username/password')
        else:
            if result['password'] == password:
                session['dis'] = result['name']
                session['id'] = username

                return render_template("admin/admin.html")
            else:
                return render_template('general.html', msg='Invalid Username/password')
    elif username.startswith("OTO"):
        dis = db.collection('customer')
        result = dis.document(username).get().to_dict()
        k = 0
        try:
            k = len(result)
        except:
            pass

        if k == 0:
            return render_template('general.html', msg='Invalid Username/password')
        else:
            if result['password'] == password:
                session['dis'] = result['username']
                session['id'] = username

                return render_template("customer/videos.html")
            else:
                return render_template('general.html', msg='Invalid Username/password')



    else:
        return render_template('general.html', msg='Invalid Username/password')

@app.route('/admin_disregister',methods=['POST'])
def admin_disregister():


    name = request.form['name']

    mobile = request.form['mobile']
    email = request.form['email']

    length = 7
    chars = string.ascii_letters + string.digits + '!@#$%^&*'

    rnd = random.SystemRandom()

    password=''.join(rnd.choice(chars) for i in range(length))
    sign = db.collection('distributor')


    result = [doc.to_dict() for doc in sign.stream()]
    k=0
    for i in result:
        if mobile==i['mobile']:
            k=1


    if k==0:
        c = db.collection('cid')

        id = c.document("count").get().to_dict()
        x=int(id['did'])+1
        c.document("count").update({"did":x})
        doc={"name":name,"mobile":mobile,"email":email,"id":x,"password":password}
        sign.document("OTOD"+str(x)).set(doc)
        return render_template('admin/add_distributor.html',msg='Registration  is done Successful;  Username - OTOD'+str(x)+"; Password - "+password)
    else:
        return render_template('admin/add_distributor.html', msg='Mobile number already exist')



@app.route('/signup',methods=['POST'])
def signup():


    username = request.form['username']
    dob = request.form['dob']
    fname = request.form['fname']
    addr = request.form['addr']
    mobile = request.form['mobile']
    email = request.form['email']
    introducer = request.form['introducer']
    length = 7
    chars = string.ascii_letters + string.digits + '!@#$%^&*'

    rnd = random.SystemRandom()

    password=''.join(rnd.choice(chars) for i in range(length))
    mob = db.collection('mobile')
    sign = db.collection('signup')

    result = mob.document(mobile).get().to_dict()
    k=0
    try:
        k=len(result)
    except:
        pass

    if k==0:
        if introducer.startswith("OTOD"):
            c = db.collection('distributor')
            id = c.document(introducer).get().to_dict()
            x=id['r_id']+1
            c.document(introducer).update({"r_id":x})
            n="OTO"+str(x)+introducer[3:]
            m={n:1}
            c.document(introducer).update(m)
            u_id=n+"C1"
            doc={"username":username,"dob":dob,"fname":fname,"addr":addr,"mobile":mobile,"email":email,"distributor_id":introducer,"leader_id":"0","r_id":x,"password":password,"user_id":u_id,"approve":"no"}
            doc1={"username":username,"mobile":mobile,"u_id":u_id}
            sign.document(u_id).set(doc)
            mob.document(mobile).set(doc1)
            return render_template('general.html',msg='Registration  is done Successful!  Username - '+n+"C1"+"; Password - "+password)
        else:
            txt=introducer
            n=re.split("O|D|C",txt)[2:]
            m="OTO"+n[0]+"D"+n[1]
            c = db.collection('customer')
            id = c.document(introducer).get().to_dict()
            x = id['distributor_id']
            d = db.collection('distributor')
            doc=d.document(x).get().to_dict()

            y = doc[m]+1
            a={m:y}
            d.document(x).update(a)
            u_id=m+"C"+str(y)
            doc = {"username": username, "dob": dob, "fname": fname, "addr": addr, "mobile": mobile, "email": email,
                   "distributor_id": x, "leader_id": introducer, "password": password, "user_id": u_id,"approve":"no"
                   }
            doc1 = {"username": username, "mobile": mobile, "u_id": u_id}
            sign.document(u_id).set(doc)
            mob.document(mobile).set(doc1)
            return render_template('general.html',
                                   msg='Registration  is done Successful!  Username - ' + u_id + "; Password - " + password)









    else:
        return render_template('general.html', msg='Mobile number already exist')


@app.route("/admin_home")
def admin_home():
    sign = db.collection('distributor')
    distributor = [doc.to_dict() for doc in sign.stream()]

    return render_template("admin/distributor.html",a=distributor)

@app.route("/add_distributor",methods=['GET', 'POST'])
def add_distributor():
    username = request.form['dname']
    dob = request.form['DOB']
    fname = request.form['fathersname']
    addr = request.form['address']
    mobile = request.form['mobile']
    email = request.form['email']
    length = 7
    chars = string.ascii_letters + string.digits + '!@#$%^&*'

    rnd = random.SystemRandom()

    password = ''.join(rnd.choice(chars) for i in range(length))
    a=db.collection("admin").document("OTOA1")
    x=a.get().to_dict()
    n=x['dis_count']+1
    doc1={"dis_count":n}
    a.update(doc1)
    m="OTOD"+str(n)
    doc = {"Name": username, "DOB": dob, "Fathersname": fname, "Address": addr, "Mobile": mobile, "Email": email,"Password":password,"u_id":m}
    db.collection('distributor').document(m).set(doc)
    return render_template("admin/add_distributor.html",msg='Registration  is done Successful!  Username - ' + m + "; Password - " + password)

@app.route("/admin_distributor")
def admin_distributor():
    c = db.collection('distributor')


    dis = [doc.to_dict() for doc in c.stream()]
    # docs = db.collection(u'Customer').stream()
    # a=[]
    # for doc in docs:
    #     print(u'{} => {}'.format(doc.id, doc.to_dict()))
    #     d=doc.to_dict()
    #     if d['Ref_id'] == " RhLyiEmF79LI7wk0IfbA":
    #         a.append(d)

    return render_template("admin/distributor.html",a=dis)


@app.route("/dis_home")
def distributor_home():
    sign = db.collection('signup')
    customer=[]
    for doc in sign.stream():
        n1=doc.to_dict()
        if n1['leader_id'] == '0' or n1['approve']=='yes':
            if n1['distributor_id'] == session['id']:
                customer.append(n1)

    #customer = [doc.to_dict() for doc in sign.stream()]
    print(customer)

    return render_template("distributor/distributor.html",customer=customer)

@app.route("/dis_customers")
def distributor_customer():
    c = db.collection('lev1')
    a=[]
    try:
        id = c.document(session['id']).get().to_dict()
        for i in id.values():
            n=db.collection("customer").document(i).get().to_dict()
            a.append(n)
    except:
        pass
        #cus = [doc.to_dict() for doc in id.stream()]
    # docs = db.collection(u'Customer').stream()
    # a=[]
    # for doc in docs:
    #     print(u'{} => {}'.format(doc.id, doc.to_dict()))
    #     d=doc.to_dict()
    #     if d['Ref_id'] == " RhLyiEmF79LI7wk0IfbA":
    #         a.append(d)

    return render_template("distributor/customers.html",a=a)

@app.route("/dis_buystocks")
def distributor_buystocks():
    return render_template("distributor/buystocks.html")

@app.route("/dis_editing")
def distributor_edit():
    doc_ref = db.collection(u'Distributor').document(u'0GG9Y70DBcs3Rya9pL3R')
    try:
        doc = doc_ref.get()
        print(u'Document data: {}'.format(doc.to_dict()))
    except Exception:
        print(u'No such document!')
    return render_template("distributor/editing.html",doc=doc.to_dict())

@app.route("/cus_request")
def customer_request():
    sign = db.collection('signup')
    customer = []
    for doc in sign.stream():
        n1 = doc.to_dict()
        if n1['leader_id'] == session['id']:
            customer.append(n1)

    # customer = [doc.to_dict() for doc in sign.stream()]

    return render_template("customer/request.html", customer=customer)


@app.route("/cus_editing")
def customer_editing():
    return render_template("customer/member.html")

@app.route("/cus_video")
def customer_video():
    return render_template("customer/videos.html")


@app.route("/cus_visitor")
def customer_visitor():
    l=session['id']
    x=db.collection("customer").document(l).get().to_dict()
    k=x["lev"]

    c = db.collection(k)
    a = []

    m = c.document(session['id']).get().to_dict()
    print(m)
    for i in m.values():
        try:
            n = db.collection("customer").document(i).get().to_dict()
            a.append(n)
        except:
            pass
    #
    return render_template("customer/visitors.html",a=a)





if __name__ == '__main__':
    app.run(debug=True)
