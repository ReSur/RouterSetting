import sys
import urllib2
import base64
import os
import time
import re
import signal

def Refresh(func, *args, **kw):
    signal.setitimer(signal.ITIMER_REAL, 3, 0)
    try:
        return func(*args, **kw)
    except:
        print '.'
        time.sleep(0.5)
        Refresh(func, *args, **kw)

def timeOut(b, c):
    print '..'
    raise RuntimeError()

class Router(object):
    def __init__(self, ip, username, password):
        self.ip = ip
        self.auth = base64.b64encode(username + ':' + password)
    def setting(self, url, data):
        headers = {
            'Authorization': 'Basic ' + self.auth
        }
        request = urllib2.Request( 'http://' + self.ip + '/cgi-bin-igd/' + url, data, headers)
        response = urllib2.urlopen(request)
        return response.read()
    def getStaus(self):
        connected = re.search(re.compile('connected\':\'(\d)\'', re.S), self.setting('igd_http_get_status_data.cgi', 'mode_name=igd_http_get_all_data&wlan_idx_num=0'))
        if connected:
            wan_connect_button_status = int(connected.group(1))
            print 'Connected code: %d' % wan_connect_button_status
            return wan_connect_button_status
    def workMode(self, code):
        print self.setting('opmode_StatusSet.cgi', 'opmode=' + code)
    def relayMode(self, ssid, password):
        print Refresh(self.setting, 'wan_work_mode_dhcp_set.cgi', 'mtu_value=1500&dns_ip_aa=&dns_ip_bb=&wan_op_mode=2&security_ap_reapter_mode=reapter&AP_SSID=' + ssid + '&AP_channel=none&wpaMode=WPA2_Only&KeySize0=40&keymode=asc&KeyVal1=&TxKey=1&wpaCipherSuite=AES&ap_wpa_mode=0&PreKeyVal=' + password + '&PreKeyVal_len=8&wpaGrpReKeyTime=86400&wlan_idx_num=0&data_only_save=wan_config')
        while True:
            print Refresh(self.setting, 'wan_connect_disconnect.cgi', 'wanid=1&linkstatus=0&wlan_idx_num=0&data_only_save=status_infotab')
            if self.getStaus():
                break

netcore = Router('192.168.1.1', 'ROUTER_USER', 'ROUTER_PASSWORD') # Modify here
signal.signal(signal.SIGALRM, timeOut)
if len(sys.argv) == 2 and sys.argv[1] in ('-b', '-r'):
    if sys.argv[1] == '-b':
        os.system('scselect Router')
        try:
            Refresh(netcore.workMode, '1')
        finally:
            os.system('scselect Automatic')
    elif sys.argv[1] == '-r':
        os.system('scselect Router')
        try:
            Refresh(netcore.workMode, '0')
            netcore.relayMode('WIFI_SSID', 'WIFI_PASSWORD') # Modify here
        finally:
            os.system('scselect Automatic')
else:
    print 'usage: python router.py -b/-r'