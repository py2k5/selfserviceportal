from flask import Blueprint, render_template
from flask import Flask,request
import subprocess
from flask import current_app

zabbix = Blueprint('zabbix', __name__)

@zabbix.route('/autoregister', methods=['GET','POST'] )
def autoregister():
    current_app.logger.debug("Function {} is called ".format(autoregister.__name__))
    if request.method == 'GET':
        return render_template('zabbix/autoregister.html')
    if request.method == 'POST':

        #return str(request.form)
        buttn = request.form['button']
        host_or_group_name = request.form['host_or_grp_name']
        host_or_grp_radio = request.form['zbxradio']
        try:
            maintenance = request.form['maintenance']
        except:
            maintenance = 'off'

        if not host_or_group_name:
            current_app.logger.error("Hostname field can not be left blank. Please input a valid hostname")
            data = { 'Error': "Host or Group can not be left blank. Please input a valid value" }
            return render_template('zabbix/autoregister_result.html', output=data)

        cmd = None
        if host_or_grp_radio == 'host': #{

            try:
                if buttn == 'validate':
                    cmd = '''/usr/local/etc/zbxAdm/2.2/scripts/autoregister.pl -validatehost {}'''.format(host_or_group_name)
                else:
                    if maintenance == 'on': 
                        cmd = '''/usr/local/etc/zbxAdm/2.2/scripts/autoregister.pl -updatehost {} -addmaintenance'''.format(host_or_group_name)
                    else:
                        cmd = '''/usr/local/etc/zbxAdm/2.2/scripts/autoregister.pl -updatehost {}'''.format(host_or_group_name)
                    #cmd = '''/usr/local/etc/zbxAdm/2.2/scripts/autoregister.pl -updatehost test'''   ##for testing using a test host
    
            except:
                current_app.logger.info("Autoregister failed to execute")
                return "Could not execute"
        #}
        else: #{
            try:
                if buttn == 'validate':
                    cmd = '''/usr/local/etc/zbxAdm/2.2/scripts/autoregister.pl -validategroup {}'''.format(host_or_group_name)
                else:
                    if maintenance == 'on': 
                        cmd = '''/usr/local/etc/zbxAdm/2.2/scripts/autoregister.pl -updategroup {} -addmaintenance'''.format(host_or_group_name)
                    else:
                        cmd = '''/usr/local/etc/zbxAdm/2.2/scripts/autoregister.pl -updategroup {}'''.format(host_or_group_name)
                    #cmd = '''/usr/local/etc/zbxAdm/2.2/scripts/autoregister.pl -updatehost test'''   ##for testing using a test host
    
            except:
                return "Could not execute"
        #}
        prog = subprocess.Popen(["ssh", "zabbix@hostname", cmd], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out,err = prog.communicate()
        data = "{} {}".format(out,err)
        return render_template('zabbix/autoregister_result.html', output=data)
            

