#coding=utf-8
 
import os
import bottle as bottle
from bottle import *
import json
from urllib.parse import urlparse
from kazoo.client import KazooClient
import kazoo.client
from furl import furl

nodepath='utility/rpi_status'
zksvr='test.qiuhao.online:2181'

@route('/rpi_status/', method='GET')
def status():
    html='<!DOCTYPE html><html><head>'+\
    '<meta charset=\'UTF-8\'>'+\
    '<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">'+\
    '<meta http-equiv="X-UA-Compatible" content="IE=8">'+\
    '<meta http-equiv="Expires" content="0">'+\
    '<meta http-equiv="Pragma" content="no-cache">'+\
    '<meta http-equiv="Cache-control" content="no-cache">'+\
    '<meta http-equiv="Cache" content="no-cache">'+\
    '<style>'+\
    '.table, .table * {margin: 0 auto; padding: 0;font-size: 14px;font-family: Arial, 宋体, Helvetica, sans-serif;}'+\
    '.table {display: table; width: 100%; border-collapse: collapse; } '+\
    '.table-tr {display: table-row; height: 30px;}   '+\
    '.table-th {display: table-cell; height: 100%;text-align: center;vertical-align: middle; border: solid 2px #BDBDBD;}   '+\
    '.table-td {display: table-cell; height: 100%;text-align: center;vertical-align: middle; border: solid 1px #BDBDBD;}   '+\
    '</style>'+\
    '<script type="text/javascript">'+\
        'var timer=null;'+\
        'function refresh(){'+\
        '    location.reload();'+\
        '    timer=setTimeout("refresh()",5000);'+\
        '}'+\
        'function stopClock(){'+\
        '    clearTimeout(timer);'+\
        '}'+\
        'function startClock(){'+\
        '    timer=setTimeout("refresh()",5000);'+\
        '}'+\
    '</script>'+\
    '</head><body onload="startClock()" onunload="stopClock()">'+\
    '<div class=\'table\'>'+\
        '<div class=\'table-tr\'>'+\
            '<div class=\'table-td\'>设备名</div>'+\
            '<div class=\'table-td\'>局域网IP</div>'+\
            '<div class=\'table-td\'>外网IP</div>'+\
            '<div class=\'table-td\'>上一次更新</div>'+\
        '</div>'

    curtime=int(time.time())
    devices=zkc.get_children(nodepath)
    print(str(devices))
    for dev in devices:
        html+='<div class=\'table-tr\'>'
        html+='<div class=\'table-td\'>'+dev+'</div>'
        html+='<div class=\'table-td\'>'+zkc.get(nodepath+'/'+dev+'/'+'localip')[0].decode()+'</div>'
        html+='<div class=\'table-td\'>'+zkc.get(nodepath+'/'+dev+'/'+'externalip')[0].decode()+'</div>'
        html+='<div class=\'table-td\'>'
        utime=int(float(zkc.get(nodepath+'/'+dev+'/'+'updatetime')[0]))
        if curtime <= utime or utime is None:
            html+='无效'
        elif curtime < utime+60:
            html+=str(int((curtime-utime))%60)+'秒前'
        elif curtime < utime+3600:
            html+=str(int((curtime-utime)/60))+'分钟'+str((curtime-utime)%60)+'秒前'
        else:
            html+=str(int((curtime-utime)/3600))+'小时'+str(int((curtime-utime)/60))+'分钟'+str((curtime-utime)%60)+'秒前'
        html+='</div></div>'

    html+='</div></body></html>'
    return HTTPResponse(html, 200, {})

@route('/rpi_status/', method='POST')
def status_report():
    body=request.body.read().decode()
    _dict=json.loads(body)
    print(str(_dict))
    if _dict is None or 'host' not in _dict or 'ip' not in _dict:
        return HTTPResponse(None, 415, {})

    folder=nodepath+"/"+_dict['host']
    zkc.ensure_path(folder)
    zkc.ensure_path(folder+"/updatetime")
    zkc.ensure_path(folder+"/localip")
    zkc.ensure_path(folder+"/externalip")

    timestamp=zkc.get(folder+"/updatetime")
    curtime=time.time()

    realip=request.environ.get('HTTP_X_REAL_IP')
    print(str(request.environ))

    zkc.set(folder+"/updatetime", str(curtime).encode('utf-8'))
    zkc.set(folder+"/localip", _dict['ip'].encode('utf-8'))

    if realip is None:
        zkc.set(folder+"/externalip", request.get('REMOTE_ADDR').encode('utf-8'))
    else:
        zkc.set(folder+"/externalip", realip.encode('utf-8'))

    timestamp=zkc.get(folder+"/updatetime")
    lip=zkc.get(folder+"/localip")
    wip=zkc.get(folder+"/externalip")

    print("record: %s: %s, %s" % (_dict['host'], lip[0], wip[0]))

    return HTTPResponse(None, 200, {})

@route('/rpi_status/report', method='GET')
def status_report():
    f=furl(request.url)
    print(str(f))
    if f.args is None or 'host' not in f.args or 'ip' not in f.args:
        return HTTPResponse(None, 415, {})

    folder=nodepath+"/"+f.args['host']
    zkc.ensure_path(folder)
    zkc.ensure_path(folder+"/updatetime")
    zkc.ensure_path(folder+"/localip")
    zkc.ensure_path(folder+"/externalip")

    timestamp=zkc.get(folder+"/updatetime")
    curtime=time.time()

    realip=request.environ.get('HTTP_X_REAL_IP')
    print(str(request.environ))

    zkc.set(folder+"/updatetime", str(curtime).encode('utf-8'))
    zkc.set(folder+"/localip", f.args['ip'].encode('utf-8'))

    if realip is None:
        zkc.set(folder+"/externalip", request.get('REMOTE_ADDR').encode('utf-8'))
    else:
        zkc.set(folder+"/externalip", realip.encode('utf-8'))

    timestamp=zkc.get(folder+"/updatetime")
    lip=zkc.get(folder+"/localip")
    wip=zkc.get(folder+"/externalip")

    print("record: %s: %s, %s" % (f.args['host'], lip[0], wip[0]))

    return HTTPResponse(None, 200, {})

def main():
    global zkc, nodepath
    zkc = KazooClient(hosts=zksvr)
    zkc.start()
    zkc.ensure_path(nodepath)

if __name__ == '__main__':
    main()
    bottle.run(server='wsgiref', host='0.0.0.0', port='23912', reloader=True)
