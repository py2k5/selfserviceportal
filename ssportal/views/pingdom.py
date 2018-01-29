from flask import Flask,render_template,request
from flask import Blueprint
from flask import current_app
import os
import subprocess 
import requests
import json
import sys

master_DC = { 'DC02' : 'DC2' , 'DC04': 'DC4', 'DC08':'DC8', 'TEST' : 'TEST' }


pingdomApiUrl = 'https://api.pingdom.com/api/2.0/checks'
auth = ('test@email.com', 'password1')
headers = {'App-Key': 'xxxxxxxxxxx','Account-Email':'xxxxxxxx@email.com'}

pingdom = Blueprint('pingdom', __name__)

def pause_resume_pingdom(chk_name,action):
    
    current_app.logger.debug("Function {} is called ".format(pause_resume_pingdom.__name__))
    response = requests.get(pingdomApiUrl, auth=auth, headers=headers)
    checks_parsed = json.loads(response.text)
    chk_data = checks_parsed['checks']
    chk_id = '0'
    for x in chk_data:
        if x['name'] == chk_name:
            chk_id = x['id']
            break
    
    if chk_id == '0':
        return 'Check not found, please enter correct name'
    
        
    apiPutUrl = pingdomApiUrl + '/' + str(chk_id)
    if action.lower() == 'pause':
        data = 'paused=true'
    elif action.lower() == 'resume':
        data = 'paused=false'

    response = requests.put(apiPutUrl, auth=auth, data=data, headers=headers)
    response_parsed = json.loads(response.text)
    #response_parsed = "Demo test"
    current_app.logger.info("Returned status : {} ".format(response_parsed))
    if 'message' in response_parsed and response_parsed['message'] == 'Modification of check was successful!':
        current_app.logger.info('successfully {}d!'.format(action))
        return 'successfully {}d!'.format(action)
    else:
        return response_parsed

def filterDCsProdsInPingdom(chk_data):
    current_app.logger.debug("Function {} is called ".format(filterDCsProdsInPingdom.__name__))
    import re
    result = {}
    DCS = set()
    products = set()
    for x in chk_data:
        name = x['name'] 
        try:
            #[IGNORE][DC14:PAY] PROD:Purdue University
            DC = re.search('\[(.*?):', name).group(1)
            DC = re.sub('IGNORE\]\s*\[*', '',DC)
            DC_upper = DC.upper()
            try:
                DC = master_DC[DC_upper]
            except:
                DC = DC_upper

        except AttributeError:
            DC = "OTHERS"

        ##create unique set of DCs
        DCS.add(DC)
        result[DC] = result.get(DC, {})



        try:
            product = re.search(':(.*?)\]', name).group(1)
            product = product.upper()
        except AttributeError:
            product = "OTHERS"

        ##create unique set of products
        products.add(product)
        result[DC][product] = result[DC].get(product, [])
        ##continue buliding result dict with product key

        result[DC][product].append(name)

    return result,sorted(DCS),sorted(products)

@pingdom.route('/pingdomadmin', methods=['GET','POST'])
@pingdom.route('/pingdomfilter', methods=['GET','POST'])
def getPingdomChecks():

    current_app.logger.debug("Function {} is called ".format(getPingdomChecks.__name__))
    try:
        response = requests.get(pingdomApiUrl, auth=auth, headers=headers)
        checks_parsed = json.loads(response.text)
        chk_data = checks_parsed['checks']
        filter_result, dcs, products = filterDCsProdsInPingdom(chk_data)
        #current_app.logger.error(filter_result,dcs,products)
    except Exception as e:
        current_app.logger.error("Can not execute pingdom API")
        return "Can not execute pingdom API"
    if request.method == 'GET':
        checks = []
        #for x in chk_data:
        #    checks.append(x['name'])
        try:
            checks = filter_result[dcs[0]][products[0]]
        except:
            current_app.logger.error("No products found for this Datacenter")
            checks = None

        return render_template('pingdom/pingdomfilter.html',data={ 'dcs' : dcs, 'products' : products , 'checks' : checks } )
    elif request.method == 'POST':
        button = request.form.get('button')
        dc = str(request.form.get('datacenter'))
        product = str(request.form.get('product'))
        if button == 'filter' :
            try: 
                checks = filter_result[dc][product]
            except:
                current_app.logger.error("No products found for this Datacenter")
                checks = "No products found for this Datacenter"
            return render_template('pingdom/pingdomfilter.html', data={ 'default_dc' : dc , 'default_product' : product, 'dcs' : dcs, 'products' : products, 'checks' : checks } )

        elif button == 'pause':
            #Add validation to see if already paused
            check_names= request.form.getlist('pingdomChkName')
            return_data = []
            for check_name in check_names:
                result = pause_resume_pingdom(check_name,'pause')
                #result = "test!!!!!!!!"
                return_data.append("""Status of check "{}" => [ {} ]""".format(check_name,result))
            return render_template('pingdom/pingdomadmin_result.html', data=return_data)
        elif button == 'resume':
            #Add validation to see if already ON
            check_names = request.form.getlist('pingdomChkName')
            return_data = []
            for check_name in check_names:
                result = pause_resume_pingdom(check_name,'resume')
                #result = "test!!!!!!!!"
                return_data.append("""Status of check "{}" => [ {} ]""".format(check_name,result))
            return render_template('pingdom/pingdomadmin_result.html', data=return_data)

