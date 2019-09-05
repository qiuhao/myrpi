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
        'var refreshtimer=null;'+\
        'function displayClock(num){'+\
        '    if(num<10){'+\
        '        return "0"+num;'+\
        '    }'+\
        '    else{'+\
        '        return num;'+\
        '    }'+\
        '}'+\
        'function refresh(){'+\
        '    location.reload();'+\
        '    refreshtimer=setTimeout("refresh()",15000);'+\
        '}'+\
        'function stopClock(){'+\
        '    clearTimeout(timer);'+\
        '}'+\
        'function startClock(){'+\
        '    var time =new Date();'+\
        '    var hours=displayClock(time.getHours())+":";'+\
        '    var minutes=displayClock(time.getMinutes())+":";'+\
        '    var seconds=displayClock(time.getSeconds());'+\
        '    document.getElementById("show").innerHTML=hours+minutes+seconds;'+\
        '    timer=setTimeout("startClock()",1000);'+\
        '}'+\
        'function onload(){'+\
        '    startClock();'+\
        '    refreshtimer=setTimeout("refresh()",15000);'+\
        '}'+\
        'function onunload(){'+\
        '    stopClock();'+\
        '    clearTimeout(refreshtimer);'+\
        '}'+\
    '</script>'+\
    '</head><body onload="onload()" onunload="onunload()">'+\
    '<div id="show" style="font-size:24px;color:#4213C9;text-align:left"></div>'+\
    '<div class=\'table\'>'+\
        '<div class=\'table-tr\'>'+\
            '<div class=\'table-td\'>设备名</div>'+\
            '<div class=\'table-td\'>型号</div>'+\
            '<div class=\'table-td\'>CPU</div>'+\
            '<div class=\'table-td\'>内存</div>'+\
            '<div class=\'table-td\'>CPU使用率/<br>主频/温度</div>'+\
            '<div class=\'table-td\'>局域网IP</div>'+\
            '<div class=\'table-td\'>外网IP</div>'+\
            '<div class=\'table-td\'>上一次更新</div>'+\
            '<div class=\'table-td\'>脚本<br>版本</div>'+\
        '</div>'

    curtime=int(time.time())
    devices=zkc.get_children(nodepath)
    devices.sort()
    for dev in devices:
        utime=int(float(zkc.get(nodepath+'/'+dev+'/'+'updatetime')[0]))
        if curtime <= utime + 3600*24:
            html+='<div class=\'table-tr\'>'
            html+='<div class=\'table-td\'>'+dev+'</div>'

            try:
                model=zkc.get(nodepath+'/'+dev+'/'+'model')
                html+='<div class=\'table-td\'>'+model[0].decode()+'</div>'
            except kazoo.exceptions.NoNodeError:
                html+='<div class=\'table-td\'>'+''+'</div>'

            try:
                cpu=zkc.get(nodepath+'/'+dev+'/'+'cpu')
                cpucore=zkc.get(nodepath+'/'+dev+'/'+'cpucore')
                cpuarch=zkc.get(nodepath+'/'+dev+'/'+'cpuarch')
                if len(cpu[0].decode()) == 0:
                    html+='<div class=\'table-td\'>'+cpuarch[0].decode()+'</div>'
                else:
                    html+='<div class=\'table-td\'>'+cpu[0].decode()+'<br>'+cpucore[0].decode()+'-core, '+cpuarch[0].decode()+'</div>'
            except kazoo.exceptions.NoNodeError:
                html+='<div class=\'table-td\'>'+''+'</div>'

            try:
                memtotal=zkc.get(nodepath+'/'+dev+'/'+'memtotal')
                memfree=zkc.get(nodepath+'/'+dev+'/'+'memfree')
                html+='<div class=\'table-td\'>'
                imt=int(int(memtotal[0].decode())/1024)
                imf=int(int(memfree[0].decode())/1024)
                if imf > 2048:
                    html+=str(int(imf*10/1024)/10)+'GB'
                else:
                    html+=str(imf)+'MB'
                html+=' free/<br>'
                if imt > 2048:
                    html+=str(int(imt*10/1024)/10)+'GB'
                else:
                    html+=str(imt)+'MB'
                html+=" total</div>"
            except kazoo.exceptions.NoNodeError:
                html+='<div class=\'table-td\'>'+''+'</div>'

            try:
                temperature=zkc.get(nodepath+'/'+dev+'/'+'temperature')
                usage=zkc.get(nodepath+'/'+dev+'/'+'cpuusage')
                freq=zkc.get(nodepath+'/'+dev+'/'+'cpufreq')
                html+='<div class="table-td">'+usage[0].decode()+'%'
                if len(freq[0].decode()) is not 0:
                    html+='<br>'+freq[0].decode()+'MHz'
                if len(temperature[0].decode()) is not 0:
                    html+='<br>'+temperature[0].decode()
                html+='</div>'
            except kazoo.exceptions.NoNodeError:
                html+='<div class=\'table-td\'>'+''+'</div>'

            html+='<div class=\'table-td\'>'
            try:
                lip=zkc.get(nodepath+'/'+dev+'/'+'localip')[0].decode().replace("\n", "<br>")
                html+=lip
                if len(lip) is not 0:
                    html+='<br>'
            except kazoo.exceptions.NoNodeError:
                noop = True
                
            try:
                lipv6=zkc.get(nodepath+'/'+dev+'/'+'localipv6')[0].decode().replace("\n", "<br>")
                html+=lipv6
                if len(lipv6) is not 0:
                    html+='<br>'
            except kazoo.exceptions.NoNodeError:
                noop = True
            
            try:
                lwip=zkc.get(nodepath+'/'+dev+'/'+'localwip')[0].decode().replace("\n", "<br>")
                html+=lwip
                if len(lwip) is not 0:
                    html+='<br>'
            except kazoo.exceptions.NoNodeError:
                noop = True
            
            try:
                lwipv6=zkc.get(nodepath+'/'+dev+'/'+'localwipv6')[0].decode().replace("\n", "<br>")
                html+=lwipv6
            except kazoo.exceptions.NoNodeError:
                noop = True
            
            html+='</div>'
            
            html+='<div class=\'table-td\'>'+zkc.get(nodepath+'/'+dev+'/'+'externalip')[0].decode()+'</div>'
            html+='<div class=\'table-td\'>'
            
            if curtime <= utime or utime is None:
                html+='无效'
            elif curtime < utime+60:
                html+=str(int((curtime-utime))%60)+'秒前'
            elif curtime < utime+3600:
                html+=str(int((curtime-utime)/60))+'分钟'+str((curtime-utime)%60)+'秒前'
            elif curtime < utime+3600*24:
                h=int((curtime-utime)/3600)
                html+=str(h)+'小时'+str(int((curtime-utime)/60)-h*60)+'分钟'+str((curtime-utime)%60)+'秒前'
            else:
                h=int((curtime-utime)/3600)
                d=int(h/24)
                html+=str(d)+'天'+str(h-d*24)+'小时'+str(int((curtime-utime)/60)-h*60)+'分钟'+str((curtime-utime)%60)+'秒前'
            html+='</div>'

            try:
                scriptver=zkc.get(nodepath+'/'+dev+'/'+'scriptver')[0].decode()
                html+='<div class=\'table-td\'>'+scriptver+'</div>'
            except kazoo.exceptions.NoNodeError:
                html+='<div class=\'table-td\'></div>'

            html+='</div>'

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
    zkc.ensure_path(folder+"/localipv6")
    zkc.ensure_path(folder+"/localwip")
    zkc.ensure_path(folder+"/localwipv6")
    zkc.ensure_path(folder+"/externalip")
    zkc.ensure_path(folder+"/cpu")
    zkc.ensure_path(folder+"/cpucore")
    zkc.ensure_path(folder+"/cpuarch")
    zkc.ensure_path(folder+"/cpuusage")
    zkc.ensure_path(folder+"/memtotal")
    zkc.ensure_path(folder+"/memfree")
    zkc.ensure_path(folder+"/model")
    zkc.ensure_path(folder+"/temperature")
    zkc.ensure_path(folder+"/cpufreq")
    zkc.ensure_path(folder+"/scriptver")

    timestamp=zkc.get(folder+"/updatetime")
    curtime=time.time()

    localip=_dict['ip']
    if localip is None:
        zkc.set(folder+"/localip", b'')
    else:
        if localip.find('addr:') is -1:
            vlip=localip.encode('utf-8')
        else:
            vlip=localip[5:].encode('utf-8')
        zkc.set(folder+"/localip", vlip)

    localipv6=_dict['ipv6']
    if localipv6 is None:
        zkc.set(folder+"/localipv6", b'')
    else:
        if localipv6.find('addr:') is -1:
            vlip=localipv6.encode('utf-8')
        else:
            vlip=localipv6[5:].encode('utf-8')
        zkc.set(folder+"/localipv6", vlip)

    localwip=_dict['wip']
    if localwip is None:
        zkc.set(folder+"/localwip", b'')
    else:
        if localwip.find('addr:') is -1:
            vlip=localwip.encode('utf-8')
        else:
            vlip=localwip[5:].encode('utf-8')
        zkc.set(folder+"/localwip", vlip)

    localwipv6=_dict['wipv6']
    if localwipv6 is None:
        zkc.set(folder+"/localwipv6", b'')
    else:
        if localwipv6.find('addr:') is -1:
            vlip=localwipv6.encode('utf-8')
        else:
            vlip=localwipv6[5:].encode('utf-8')
        zkc.set(folder+"/localwipv6", vlip)

    zkc.set(folder+"/updatetime", str(curtime).encode('utf-8'))
    zkc.set(folder+"/cpu", _dict['cpu'].encode('utf-8'))
    zkc.set(folder+"/cpuarch", _dict['arch'].encode('utf-8'))
    zkc.set(folder+"/model", _dict['model'].encode('utf-8'))
    zkc.set(folder+"/temperature", _dict['temperature'].encode('utf-8'))

    print(_dict['usage'])
    zkc.set(folder+"/cpuusage", str(_dict['usage']).encode('utf-8'))
    zkc.set(folder+"/cpucore", str(_dict['core']).encode('utf-8'))
    zkc.set(folder+"/memtotal", str(_dict['mem']).encode('utf-8'))
    zkc.set(folder+"/memfree", str(_dict['memf']).encode('utf-8'))

    if 'freq' in _dict:
        zkc.set(folder+"/cpufreq", str(_dict['freq']/1000000).encode('utf-8'))

    if 'scriptver' in _dict:
        zkc.set(folder+"/scriptver", str(_dict['scriptver']).encode('utf-8'))

    realip=request.environ.get('HTTP_X_REAL_IP')

    if realip is None:
        zkc.set(folder+"/externalip", request.get('REMOTE_ADDR').encode('utf-8'))
    else:
        zkc.set(folder+"/externalip", realip.encode('utf-8'))

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
