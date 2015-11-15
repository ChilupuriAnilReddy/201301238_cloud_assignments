from flask import Flask
from flask import request
from flask import json 
from json import JSONDecoder
from json import JSONEncoder
from flask import jsonify
import collections
import libvirt
import os
import sys


app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False


@app.route('/')
def hello_world():
	print len(conn.listDomainsID())
	return 'Hello World!'

@app.route('/vm/create', methods=['GET', 'POST'])
def vmcreate():
	name  =  request.args.get('name')
	typ  = int(request.args.get('instance_type'))
	imgid  = int(request.args.get('image_id'))
	fileopen = open("flavor_file","rw")
	read = fileopen.read()
	dic = json.loads(read)
	cpu = (dic['types'][typ-1]['cpu'])
	ram = (dic['types'][typ-1]['ram'])
	disk = (dic['types'][typ-1]['disk'])
	flag = 0
	pmid = 0
	pmlistopen = open('pm_file','r')
	for line in pmlistopen:
		pmid = pmid + 1
		print line.strip("\n")
		requiredip = line.strip("\n")
		conn = libvirt.open("qemu+ssh://"+line.strip("\n")+"/system")
		#conn = libvirt.open("qemu:///system")
		print conn
		x = conn.getInfo()
		z = conn.getFreeMemory()
		avacpu = x[2]
		avaram = z/1000000
		if (avacpu >= cpu ) and (avaram >= ram):
			flag = 1
			break

	if flag==1:
		print conn
		try:
			id_assign = str(max(conn.listDomainsID())+1)
		except:
			id_assign = str(1)
		name = str(name)
		ram = str(ram)
		cpu = str(cpu)
		imagelistopen = open('image_file','r')
		i = 0
		for line in imagelistopen:
			i = i + 1
			if i==imgid:
				location=line.strip("\n")
				break;
		os.system("scp " +" " + location + " "+ requiredip.strip("\n") +":~/")
		name111 = location.strip("\n")
		name111= name111.split("/");
		nameofos= name111[len(name111)-1]
		username = requiredip.strip("\n").split("@")[0]
		location = "/home/"+username+"/"+str(nameofos)
		print location
		#os.system(" ssh " + requiredip +" chmod 777 " + location)

		a = "<domain type='qemu' id='"+id_assign+"'><name>"+name+"</name><memory unit='KiB'>"+ram+"</memory><vcpu placement='static'>"+cpu+"</vcpu><os><type arch='x86_64' machine='pc-i440fx-trusty'>hvm</type></os><devices><disk type='file' device='cdrom'><source file='"+str(location)+"'/><target dev='hdc' bus='ide'/></disk></devices></domain>"
		try:
			conn.defineXML(a)
			dom = conn.lookupByName(name)
			dom.create()
			dom = conn.lookupByName(name)
			idd = dom.ID()
			#print idd
			id_assign = str(idd)
			fileopen = open("vmcreated","a")
			s = str(id_assign) + "\t" +str(name)+"\t"+str(typ)+"\t" + str(pmid) + "\n" 
			fileopen.write(s)
			fileopen.close()
			status = json.loads('{"status":'+str(id_assign)+'}') 
			return jsonify(status) 
		except:
			status = json.loads('{"status":0}') 
			return jsonify(status)
	else:
		status = json.loads('{"status":0}') 
		return jsonify(status)

	


@app.route('/vm/query',methods=['GET'])
def vmquery():
	vmid = request.args.get('vmid')
	flag = 0
	try:
		fileopen  = open('vmcreated','ra')
	except:
		status = json.loads('{"status":0}') 
		return jsonify(status)
	for line in fileopen:
		line = line.split()
		if line[0] == vmid:
			flag = 1
			break
	if flag == 0:
		status = json.loads('{"status":0}') 
		return jsonify(status)
	else:
		vmdetails={}
		vmdetails["vmid"]=int(line[0])
		vmdetails["name"]=line[1]
		vmdetails["instance_type"]=int(line[2])
		vmdetails["pmid"]=int(line[3]) 
		return jsonify(vmdetails)
	


@app.route('/vm/destroy',methods=['GET'])
def vmdestroy():
	vmid = request.args.get('vmid')
	flag = 0
	cnt = 0
	try:
		vmcreatedfileopen  = open('vmcreated','r')
	except:
		status = json.loads('{"status":0}') 
		return jsonify(status)
	for line in vmcreatedfileopen:
		cnt = cnt + 1
		line = line.split()
		try:
			if int(line[0]) == int(vmid):
				flag = 1
				requiredname = line[1]
				requiredpmid = line[3]
				break
		except:
			status = json.loads('{"status":0}') 
			return jsonify(status)
	vmcreatedfileopen.close()

	if flag == 0:
		status = json.loads('{"status":0}') 
		return jsonify(status)
	else:
		pmlistopen = open('pm_file','r')
		i = 0
		flag = 0
		print requiredpmid
		for line in pmlistopen:
			print line.strip("\n")
			i = i +1
			if int(i)==int(requiredpmid):
				print "yyy"
				flag =1
				break
		print flag
		if flag==1:
			print line.strip("\n")
			conn = libvirt.open("qemu+ssh://"+line.strip("\n")+"/system")
			#conn = libvirt.open("qemu:///system")
			print conn
			try:
				dom = conn.lookupByName(requiredname)
				dom.destroy()
				dom.undefine()
			except:
				status = json.loads('{"status":0}') 
				return jsonify(status)
			fileopen1 = open('temp','w')
			fileopen  = open('vmcreated','r')
			i = 0;
			for line in fileopen:
				i = i + 1
				if i!=cnt:
					fileopen1.write(line)
			fileopen.close()
			fileopen1.close()
			fileopen1 = open('temp','r')
			fileopen  = open('vmcreated','w')
			for line in fileopen1:
				print line
				fileopen.write(line)
			status = json.loads('{"status":1}') 
			return jsonify(status)
		else:
			print flag
			status = json.loads('{"status":0}') 
			return jsonify(status)


		

@app.route('/vm/types')
def vmtypes():
	fileopen = open("flavor_file","rw")
	read = json.loads(fileopen.read(),object_pairs_hook=collections.OrderedDict) 
	return jsonify(read)
	


@app.route('/pm/lists',methods=['GET'])
def pmlists():
	pmlistopen = open('pm_file','r')
	#pmlistread = pmlistopen.read()
	pmlistdict = {}
	pmlistdict["pmids"]=[]
	print pmlistdict
	i = 1
	for line in pmlistopen:
		print line
		pmlistdict["pmids"].append((i))
		i=i+1
	return jsonify(pmlistdict)

@app.route('/pm/listvms',methods=['GET'])
def listvms():
	pmid = request.args.get('pmid')
	try:
		pmfileopen = open('vmcreated','r')
	except:
		status = json.loads('{"vmids":0}') 
		return jsonify(status)
	i = 0
	flag=0
	status={}
	status["vmid"]=[]
	for line in pmfileopen:
		i = i + 1
		line = line.strip("\n")
		line = line.split()
		if int(line[3])==int(pmid):
			flag = 1
			status["vmid"].append(int(line[0]))
	if flag==0:
		status = json.loads('{"vmids":0}')
		return jsonify(status)
	else:
		try:
			#conn2 = libvirt.open("qemu+ssh://"+line.strip("\n")+"/system")
			#print conn
			#k = str(conn2.listDomainsID())
			#status = json.loads('{"vmids":'+str(k)+'}')
			return jsonify(status)
		except:
			status = json.loads('{"vmids":0}')
			return jsonify(status)

@app.route('/pm/query',methods=['GET'])
def pmquery():
	pmid = request.args.get('pmid')
	pmfileopen = open('pm_file','r')
	i = 0
	flag=0
	for line in pmfileopen:
		i = i + 1
		if i==int(pmid):
			flag=1
			break
	if flag==0:
		status = json.loads('{"status":0}')
		return jsonify(status)
	else:
		print "hello11"
		print line.strip("\n")
		try:
			conn1 = libvirt.open("qemu+ssh://"+line.strip("\n")+"/system")
			z = conn1.numOfDomains()
			print z
			x = conn1.getInfo()
			print x
			#print conn1.getCapabilities()
			z1= conn1.getFreeMemory()
			os.system(" ssh " + line.strip("\n") +" df --total -TH --exclude-type=tmpfs | awk '{print $3}' | tail -n 1 | cut -b -5 > pmdata1")
			os.system(" ssh " + line.strip("\n") +" df --total -TH --exclude-type=tmpfs | awk '{print $5}' | tail -n 1 | cut -b -5 > pmdata2")
			#print conn1.getSysinfo()
			#print conn1.vcpus()
			#print conn1.maxMemory()
			#print conn1.getCPUMap()
			#print conn1.getCPUStats(1,0)
			#print conn1.getCPUStats(2,0)
			#print conn1.getCPUStats(3,0)
			written = 0;
			"""for id1 in conn1.listDomainsID():
				domm = conn1.lookupByID(id1)
				stats = domm.blockStats()
				written += stats[3]"""

			print conn1.getCPUMap()
			fileopenx = open('pmdata1','r')
			total = fileopenx.read().strip("\n")
			fileopenx = open('pmdata2','r')
			free = fileopenx.read().strip("\n")
			pmquerystatus={}
			capacitydetails={}
			capacitydetails["cpu"]= x[2]
			capacitydetails["ram"]= int(x[1])
			capacitydetails["disk"]= total
			freedetails={}
			freedetails["cpu"]= x[2]
			freedetails["ram"]= z1/1000000
			freedetails["disk"]= free
			print capacitydetails
			print freedetails
			pmquerystatus["pmid"] = pmid
			pmquerystatus["capacity"]=capacitydetails
			pmquerystatus["free"]=freedetails
			pmquerystatus["vms"]=z
			print pmquerystatus
			
			#print conn1.getCPUStats(4,0)
			#status = ({"pmid":'+str(pmid)+',"capacity":{"cpu": '+str(x[2])+',"ram": '+ str(x[1])+' ,"disk": 160},"free":{"cpu": 2,"ram": '+str(z1/1000000)+',"disk": 157},"vms":'+str(z)+'})
			#print status
			#print json.loads(status,object_pairs_hook=collections.OrderedDict)
			return jsonify(pmquerystatus)
		except:
			status = json.loads('{"status":0}')
			return jsonify(status)


@app.route('/image/list',methods=['GET'])
def imagelists():
	imagelistopen = open('image_file','r')
	#imagelistread = imagelistopen.read()
	imagelistdict = {}
	imagelistdict["images"]=[]
	i = 1
	for line in imagelistopen:
		print line
		line = line.strip("\n")
		splitedline = line.split("/")
		nameofos = splitedline[len(splitedline)-1]
		if nameofos[len(nameofos)-1] == "\n":
			nameofos=nameofos[:-5]
		else:
			nameofos=nameofos[:-4]
		print splitedline
		tempdict={}
		tempdict["id"]=i
		tempdict["name"]=nameofos
		imagelistdict["images"].append(tempdict)
		i=i+1
	return jsonify(imagelistdict)


if __name__ == '__main__':
	conn=libvirt.open("qemu:///system")
	app.run(debug=True)
