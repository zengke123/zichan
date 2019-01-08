from web_init import create_app, db
from sqlalchemy import distinct
from flask import request, session, jsonify
from flask import render_template, redirect, url_for, send_from_directory
from models import Host


app = create_app()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/hardware')
def hardware():
    show_cols = [('平台', 'platform'), ('集群', 'cluster'), ('主机', 'hostname'), ('设备类型', 'device_type'),
                 ('设备厂家', 'manufacturer'), ('设备型号', 'device_model'), ('序列号', 'serial'),
                 ('机房', 'engine_room'), ('机架', 'frame_number'), ('电源柜', 'power_frame_number'),
                 ('入网时间', 'net_time'), ('过保时间', 'period'), ('状态', 'status')]
    platforms = db.session.query(distinct(Host.platform)).all()
    device_types = db.session.query(distinct(Host.device_type)).all()
    platform = [x[0] for x in platforms]
    device_type = [x[0] for x in device_types]
    return render_template('hardwareInfo.html', platform=platform, device_type=device_type, show_cols=show_cols)


@app.route('/get_cluster', methods=["GET", "POST"])
def get_cluster():
    platforms = request.form.get('data')
    clusters = db.session.query(distinct(Host.cluster)).filter(Host.platform == platforms).all()
    rooms = db.session.query(distinct(Host.engine_room)).filter(Host.platform == platforms).all()
    cluster = [x[0] for x in clusters]
    engine_room = [x[0] for x in rooms]
    result = {
        "cluster": cluster,
        "engine_room": engine_room
    }
    return jsonify(result)


@app.route('/get_detail', methods=["GET", "POST"])
def get_detail():
    temp = ["选择平台", "选择机房", "选择网元", "选择设备类型"]
    pt = request.form.get('pt')
    jf = request.form.get('jf')
    jq = request.form.get('jq')
    lx = request.form.get('lx')
    zj = request.form.get('zj')
    kw_temp = {
        "platform": pt if pt and pt not in temp else None,
        "engine_room": jf if jf and jf not in temp else None,
        "cluster": jq if jq and jq not in temp else None,
        "device_type": lx if lx and lx not in temp else None,
        "hostname": zj if zj and zj not in temp else None
    }
    kw = {k: v for k, v in kw_temp.items() if v}
    hosts = db.session.query(Host).filter_by(**kw).all()
    datas = []
    for host in hosts:
        datas.append(host.to_json())
    result = {
        "flag": "success",
        "hosts": datas
    }
    return jsonify(result)


@app.route('/get_detail_id', methods=["GET", "POST"])
def get_detail_id():
    device_id = request.form.get('id')
    host_info = db.session.query(Host).filter(Host.id == device_id).one()
    result = {
        "flag": "success",
        "hosts": host_info.to_json()
    }
    return jsonify(result)


@app.route('/modify_by_id', methods=["GET", "POST"])
def modify_by_id():
    datas = request.get_json()
    try:
        device_id = datas.get('id')
        db.session.query(Host).filter(Host.id == device_id).update(datas)
        db.session.commit()
    except Exception as e:
        print(str(e))
    # request中要求的数据格式为json，为其他会导致前端执行success不成功
    result = {"flag": "success"}
    return jsonify(result)


@app.route('/delete_by_id', methods=["GET", "POST"])
def delete_by_id():
    device_id = request.form.get('id')
    try:
        to_delete = Host.query.filter(Host.id == device_id).first()
        db.session.delete(to_delete)
        db.session.commit()
        result = {"flag": "success"}
    except Exception as e:
        print(str(e))
        result = {"flag": "fail"}
    return jsonify(result)


@app.route('/software')
def software():
    return render_template('softwareInfo.html')


@app.route('/capacity')
def capacity():
    return render_template('capacityInfo.html')


@app.route('/custom')
def custom():
    return render_template('customInfo.html')


if __name__ == '__main__':
    app.run()
