from flask import Flask
from flask import request
from flask import json 
from json import JSONDecoder
from json import JSONEncoder
from flask import jsonify
import collections
import libvirt
import os
import rbd
import sys
import rados
from random import choice



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
		avaram = z/1000
		print "ava cpu",avacpu
		print "ava ram",avaram
		print "cpu ",cpu
		print "ram",ram*512
		if (avacpu >= cpu ) and (avaram >= int(ram)):
			flag = 1
			break

	if flag==1:
		print conn
		try:
			id_assign = str(max(conn.listDomainsID())+1)
		except:
			id_assign = str(1)
		name = str(name)
		ram = ram*1024
		ram = str(ram)
		cpu = str(cpu)
		imagelistopen = open('image_file','r')
		i = 0
		for line in imagelistopen:
			i = i + 1
			if i==imgid:
				location=line.strip("\n")
				break;
		name111 = location.strip("\n")
		name111= name111.split("/");
		nameofos= name111[len(name111)-1]
		os.system( "ssh " + requiredip.strip("\n") +" rm -r " + nameofos)		
		os.system("scp " +" " + location + " "+ requiredip.strip("\n") +":~/")
		print "scp " +" " + location + " "+ requiredip.strip("\n") +":~/"
		username = requiredip.strip("\n").split("@")[0]
		location = "/home/"+username+"/"+str(nameofos)
		print location
		#os.system(" ssh " + requiredip +" chmod 777 " + location)

		#a = "<domain type='qemu' id='"+id_assign+"'><name>"+name+"</name><memory unit='KiB'>"+ram+"</memory><vcpu placement='static'>"+cpu+"</vcpu><os><type arch='x86_64' machine='pc-i440fx-trusty'>hvm</type></os><devices><disk type='file' device='cdrom'><source file='"+str(location)+"'/><target dev='hdc' bus='ide'/></disk><graphics type='vnc' port='-1'/></devices></domain>"
		a = """<domain type='qemu' id='%s'><name>%s</name><memory unit='KiB'>%s</memory><vcpu>%s</vcpu><os><type arch='x86_64' machine='pc-1.1'>hvm</type><boot dev='cdrom'/><boot dev='hd'/></os><features><acpi/><apic/><pae/></features><clock offset='utc'/><on_poweroff>destroy</on_poweroff><on_reboot>restart</on_reboot><on_crash>restart</on_crash><devices><emulator>/usr/bin/kvm-spice</emulator><disk type='file' device='cdrom'><driver name='qemu' type='raw'/><target dev='hda' bus='ide'/></disk><disk type='file' device='cdrom'><driver name='qemu' type='raw'/><source file='%s'/><target dev='hdc' bus='ide'/><readonly/></disk><graphics type='spice' port='5900' autoport='yes' listen='127.0.0.1'><listen type='address' address='127.0.0.1'/> </graphics></devices></domain>"""% (str(id_assign), str(name), str(int(ram)), cpu, str(location))
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


@app.route('/volume/create',methods=['GET'])
def volumecreate():
	name=request.args.get('name')
	size=request.args.get('size')
	try:
		fileopen = open('volumecreated','r');
	except:
		fileopen = open('volumecreated','w')
		fileopen = open('volumecreated','r')
	flag=0;
	maxi=10;
	for line in fileopen:
		print line
		line = line.strip("\n").split()
		print line
		if maxi < int(line[1]):
			maxi=int(line[1])
		if(line[0]==name):
			flag=1
			break
	fileopen.close()
	if flag==1:
		status = json.loads('{"status":0}')
		return jsonify(status)
	else:
		print "YESSSSSSSS"
		POOL_NAME = 'pool-anil1'
		CONF_FILE = '/etc/ceph/ceph.conf'
		radosConnection = rados.Rados(conffile=CONF_FILE)
		radosConnection.connect()
		if POOL_NAME not in radosConnection.list_pools(): 
			print " HELLO"                               
			radosConnection.create_pool(POOL_NAME)
		ioctx = radosConnection.open_ioctx(POOL_NAME)
		rbdInstance = rbd.RBD()
		try:
			#storage_pool_xml = '<pool type="dir"><name>anil</name><uuid>33a5c045-645a-2c00-e56b-927cdf34e17a</uuid><target><path>/home/anilreddy/Desktop/anil</path></target></pool>'
			#storage_vol_xml = '<volume><name>'+str(name)+'</name><allocation>0</allocation><capacity unit="G">1</capacity><target><path>/home/anilreddy/Desktop/anil/'+str(name)+'.img</path></target></volume>'
			#conn = libvirt.open("qemu:///system")
			#pool = conn.storagePoolDefineXML(storage_pool_xml,0)
			#if pool.isActive():
			#	z=1
			#else:
			#	pool.build()
			#	pool.create()
			#vol = pool.createXML(storage_vol_xml)
			print "YYYYYYYY0"
			size = int(size)
			name = str(name)
			print name
			rbdInstance.create(ioctx,name,size)
			print "YYYYYYYY"
		#os.system("sudo rbd create"+name+"--size"+size+"-k /etc/ceph/ceph.client.admin.keyring")
		#os.system("sudo modprobe rbd")
			os.system('sudo rbd map %s --pool %s --name client.admin '%(name,POOL_NAME))
			print "YYYYYYYY1"
			fileopen = open('volumecreated','a')
			sta = "Available"
			vid = "None"
			print str(getDeviceName())
			wt = name + "\t" + str(maxi+1) + "\t" + sta + "\t" + vid + "\t" + str(size) + "\t" + str(getDeviceName()) + "\n"
			print wt
			fileopen.write(wt)
			status = json.loads('{"status":'+str(maxi+1)+'}') 
			return jsonify(status)
		except:
			status = json.loads('{"status":'+str(0)+'}') 
			return jsonify(status)


@app.route('/volume/query',methods=['GET'])
def volumequery():
	volumeid=request.args.get('volumeid')
	try:
		fileopen = open('volumecreated','r')
	except:
		status={}
		kk = "volumeid " +str(volumeid)+" doesnot exits "
		status['error']= kk 
		return jsonify(status)
	required_pmid=-1
	for line in fileopen:
		line = line.strip("\n").split()
		if int(line[1])==int(volumeid):
			required_pmid = 1
			required_status = line[2]
			require_vid = line[3]
			required_name = line[0]
			required_size = line[4]
			break
	if required_pmid==-1:
		status={}
		kk = "volumeid " +str(volumeid)+" doesnot exits "
		status['error']= kk
		#status = json.loads(status) 
		return jsonify(status)
	else:
		#conn = libvirt.open("qemu:///system")
		#pool = conn.storagePoolLookupByName('anil')
		#vol  = pool.storageVolLookupByName(required_name) 
		status={}
		status['volumeid']=volumeid
		status['name']=required_name
		status['size']=required_size
		status['status']=required_status
		status['vmid']=require_vid
		return jsonify(status)




	return volumeid

@app.route('/volume/destroy',methods=['GET'])
def volumedestroy():
	volumeid=request.args.get('volumeid')
	flag = 0
	cnt = 0
	try:
		volumecreatedfileopen  = open('volumecreated','r')
	except:
		status = json.loads('{"status":0}') 
		return jsonify(status)
	for line in volumecreatedfileopen:
		cnt = cnt + 1
		line = line.split()
		try:
			if int(line[1]) == int(volumeid):
				flag = 1
				requiredname = line[0]
				break
		except:
			status = json.loads('{"status":0}') 
			return jsonify(status)

	if flag == 0:
		status = json.loads('{"status":0}') 
		return jsonify(status)
	else:
		#pmlistopen = open('pm_file','r')
		#i = 0
		#flag = 0
		#print requiredpmid
		#for line in pmlistopen:
		#	print line.strip("\n")
		#	i = i +1
		#	if int(i)==int(requiredpmid):
		#		print "yyy"
		#		flag =1
		#		break
		#print flag
		flag=1
		if flag==1:
			#print line.strip("\n")
			#conn = libvirt.open("qemu+ssh://"+line.strip("\n")+"/system")
			#conn = libvirt.open("qemu:///system")
			print conn
			try:
				imageName = str(requiredname)
				POOL_NAME = 'pool-anil1'
				CONF_FILE = '/etc/ceph/ceph.conf'
				radosConnection = rados.Rados(conffile=CONF_FILE)
				radosConnection.connect()
				ioctx = radosConnection.open_ioctx(POOL_NAME)
				rbdInstance = rbd.RBD()
				os.system('sudo rbd unmap /dev/rbd/%s/%s'%(POOL_NAME,imageName))
				rbdInstance.remove(ioctx,imageName)
				#pool = conn.storagePoolLookupByName('anil')
				#vol  = pool.storageVolLookupByName(requiredname) 
				#vol.delete()
				#dom = conn.lookupByName(requiredname)
				#dom.destroy()
				#dom.undefine()
			except:
				status = json.loads('{"status":0}') 
				return jsonify(status)
			fileopen1 = open('temp1','w')
			fileopen  = open('volumecreated','r')
			print  "OOOOO"
			print cnt
			i = 0;
			for line in fileopen:
				print line
				i = i + 1
				if i!=cnt:
					fileopen1.write(line)
			fileopen.close()
			fileopen1.close()
			fileopen1 = open('temp1','r')
			fileopen  = open('volumecreated','w')
			for line in fileopen1:
				print line
				fileopen.write(line)
			status = json.loads('{"status":1}') 
			return jsonify(status)
		else:
			print flag
			status = json.loads('{"status":0}') 
			return jsonify(status)

	"""volumecreatedfileopen.close()
	conn = libvirt.open("qemu:///system")
	pool = conn.storagePoolLookupByName('anil')
	#pool.undefine()
	print pool.listAllVolumes(0)
	print pool.listVolumes()
	vol  = pool.storageVolLookupByName(volumeid) 
	vol.delete()
	status = json.loads('{"status":1}')
	return jsonify(status)"""


def getDeviceName():
	alpha = choice('efghijklmnopqrstuvwxyz')
	numeric = choice([x for x in range(1,10)])
	return 'sd' + str(alpha) + str(numeric)	
	 	

@app.route('/volume/attach',methods=['GET'])
def volumeattach():
	vmid=request.args.get('vmid')
	volumeid=request.args.get('volumeid')
	try:
		fileopen  = open('vmcreated','ra')
	except:
		status = json.loads('{"status":0}') 
		return jsonify(status)
	for line in fileopen:
		line = line.split()
		if line[0] == vmid:
			requiredpmid = int(line[3])
			vmname = str(line[1])
			flag = 1
			break
	if flag == 0:
		status = json.loads('{"status":0}') 
		return jsonify(status)

	try:
		fileopen = open('volumecreated','r')
	except:
		status={}
		kk = "volumeid " +str(volumeid)+" doesnot exits "
		status['error']= kk 
		return jsonify(status)
	required_pmid=-1
	cnt =0
	for line in fileopen:
		cnt = cnt + 1
		line = line.strip("\n").split()
		if int(line[1])==int(volumeid) and str(line[2])==str("Available"):
			required_pmid = 1
			required_status = line[2]
			require_vid = line[3]
			required_name = line[0]
			required_size = line[4]
			required_device_name = str(line[5]) 
			break
	if required_pmid==-1:
		status={}
		kk = "volumeid " +str(volumeid)+" doesnot exits "
		status['error']= kk
		#status = json.loads(status) 
		return jsonify(status)
	imageName = str(required_name)

	pmlistopen = open('pm_file','r')
	pmid = 0;
	for line in pmlistopen:
		pmid = pmid + 1
		if(requiredpmid==pmid):
			print line.strip("\n")
			requiredip = line.strip("\n")
			conn = libvirt.open("qemu+ssh://"+line.strip("\n")+"/system")
	POOL_NAME = 'pool-anil1'
	dom = conn.lookupByName(vmname)
	BLOCK_CONFIG_XML = 'attach.xml'
	host = "10.1.36.128"
	configXML = """<disk type='block' device='disk'><driver name='qemu' type='raw'/><source protocol='rbd' dev='/dev/rbd/%s/%s'><host name='%s' port='6789'/></source><target dev='%s' bus='virtio'/><address type='pci' domain='0x0000' bus='0x00' slot='0x05' function='0x0'/></disk>"""%(POOL_NAME, imageName, host, required_device_name)
	try:
		dom.attachDevice(configXML)
		conn.close()
	except Exception,e:
		conn.close()
		print str(e)
		return jsonify(statu1s=0)
	fileopen1 = open('temp2','w')
	fileopen  = open('volumecreated','r')
	print  "OOOOO"
	print cnt
	i = 0;
	for line in fileopen:
		print line
		i = i + 1
		if i!=cnt:
			fileopen1.write(line)
		else:
			line=line.strip("\n").split()
			a = line[0] + "\t" + line[1] + "\t" + str("Attached") + "\t" + str(vmid) + "\t" + line[4] + "\t" + line[5] + "\n"
 			fileopen1.write(a) 
	fileopen.close()
	fileopen1.close()
	fileopen1 = open('temp2','r')
	fileopen  = open('volumecreated','w')
	for line in fileopen1:
		print line
		fileopen.write(line)
	status = json.loads('{"status":1}')  
	return jsonify(status)


@app.route('/volume/detach',methods=['GET'])
def volumedetach():
	volumeid=request.args.get('volumeid')
	try:
		fileopen = open('volumecreated','r')
	except:
		status={}
		kk = "volumeid " +str(volumeid)+" doesnot exits "
		status['error']= kk 
		return jsonify(status)
	required_pmid=-1
	cnt =0
	for line in fileopen:
		cnt = cnt + 1
		line = line.strip("\n").split()
		if int(line[1])==int(volumeid):
			required_pmid = 1
			required_status = line[2]
			require_vid = line[3]
			vmid = require_vid
			required_name = line[0]
			required_size = line[4]
			required_device_name = str(line[5]) 
			break
	if required_pmid==-1:
		status={}
		kk = "volumeid " +str(volumeid)+" doesnot exits "
		status['error']= kk
		#status = json.loads(status) 
		return jsonify(status)
	if required_status==str("Attached"):
		try:
			fileopen  = open('vmcreated','ra')
		except:
			status = json.loads('{"status":0}') 
			return jsonify(status)
		for line in fileopen:
			line = line.split()
			if line[0] == vmid:
				requiredpmid = int(line[3])
				vmname = str(line[1])
				flag = 1
				break
		if flag == 0:
			status = json.loads('{"status":0}') 
			return jsonify(status)
		imageName = str(required_name)

		pmlistopen = open('pm_file','r')
		pmid = 0;
		for line in pmlistopen:
			pmid = pmid + 1
			if(requiredpmid==pmid):
				print line.strip("\n")
				requiredip = line.strip("\n")
				conn = libvirt.open("qemu+ssh://"+line.strip("\n")+"/system")
		POOL_NAME = 'pool-anil1'
		dom = conn.lookupByName(vmname)
		BLOCK_CONFIG_XML = 'attach.xml'
		host = "10.1.36.128"
		configXML = """<disk type='block' device='disk'><driver name='qemu' type='raw'/><source protocol='rbd' dev='/dev/rbd/%s/%s'><host name='%s' port='6789'/></source><target dev='%s' bus='virtio'/><address type='pci' domain='0x0000' bus='0x00' slot='0x05' function='0x0'/></disk>"""%(POOL_NAME, imageName, host, required_device_name)
		try:
			dom.detachDevice(configXML)
			conn.close()
		except:
			conn.close()
			return jsonify(status=0)

		fileopen1 = open('temp3','w')
		fileopen  = open('volumecreated','r')
		print  "OOOOO"
		print cnt
		i = 0;
		for line in fileopen:
			print line
			i = i + 1
			if i!=cnt:
				fileopen1.write(line)
			else:
				line=line.strip("\n").split()
				a = line[0] + "\t" + line[1] + "\t" + str("Available") + "\t" + str("None") + "\t" + line[4] + "\t" + line[5] + "\n"
 				fileopen1.write(a) 
		fileopen.close()
		fileopen1.close()
		fileopen1 = open('temp3','r')
		fileopen  = open('volumecreated','w')
		for line in fileopen1:
			print line
			fileopen.write(line)
		status = json.loads('{"status":1}')  
	return jsonify(status) 






if __name__ == '__main__':
	conn=libvirt.open("qemu:///system")
	app.run(debug=True)
