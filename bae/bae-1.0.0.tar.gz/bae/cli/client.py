#*- coding : utf-8 -*-
'''
Bae Client contains main apis for BAE

@Author    : zhangguanxing01@baidu.com
@Copyright : 2013 Baidu Inc. 
@Date      : 2013-07-26 11:09:00
'''

import sys
import re
import os
import time
import messages
import code_tool            
import shutil
import json

from   .messages          import g_messager
from   ..config.parser    import BaeParser
from   ..rest.rest        import BaeRest
from   ..config.constants import *
from   ..config.config    import *
from   ..errors           import *

class BaeClient:
    def __init__(self):
        pass
    def start(self):
        parser = BaeParser()
        if parser.debug:
            messages.DEBUG = True
            g_messager.debug("Debug mode ON")
        else:
            messages.DEBUG = False

        #Load Global Configs or Local App Configs
        #if cmd is not init or setup, config non-exist will considered an error
        try:
            self.globalconfig = BaeGlobalConfig()
            self.globalconfig.model.use_color = True
            self.globalconfig.load()
            #set global message settings
            g_messager.use_color = self.globalconfig.model.use_color
            g_messager.use_cn    = self.globalconfig.model.use_cn or False
            if parser.cmd == "login":
                raise BaeConfigError("Nothing")
            
            API_ENTRY = self.globalconfig.model.api_entry
            self.rest = BaeRest(access_token = self.globalconfig.model.user.access_token, debug = parser.debug)
            self._check_version()
        except (BaeConfigError, IOError):
            if parser.cmd != "login":
                g_messager.suggestion("Bae Configuration not founded or broken, please use '{prog} login' to "
                                   "init your bae environment"
                                   .format(prog=PROG_NAME))
                sys.exit(-1)
            else:
                self.rest = BaeRest(None, debug = parser.debug)
        try:
            self.appconfig = DevAppConfig()
            self.appconfig.load()
        except (BaeConfigError, IOError):
            if parser.cmd != "login" and parser.appcmd != "setup" and not parser.force:
                g_messager.suggestion("NO local app directory founded, Please visit "+\
                                   "{0} apply a appid and use '{1} app setup' ".format(DEVELOPER, PROG_NAME) +\
                                    "to connect current directory to bae")
                g_messager.exception()
                sys.exit(-1)
            else:
                g_messager.debug("Load app config done")

            #If User set appid mannualy, this means he didn't want any local cache
            self.appconfig = None

        subcmd = "parser.{0}cmd".format(parser.cmd)

        if eval (subcmd):
            fullcmd = "{0}_{1}".format(parser.cmd, eval(subcmd))
        else:
            fullcmd = parser.cmd

        try:
            #call subcmd functions
            getattr(self, fullcmd)(parser)
        except (BaeCliError, BaeRestError, BaeConfigError, KeyError, ValueError, TypeError, IOError):
            g_messager.exception()

    def _check_version(self):
        def cmp_version(a, b):
            return cmp(a.split('.'), b.split("."))

        try:
            data = {}
            data["tool_name"] = "cli"
            ret = self.rest.get(API_ENTRY + "/bae/bce/app/getVersionInfo", data = data)
            min_ver = ret["min_version"]
            cur_ver = ret["cur_version"]
            my_ver  = VERSION
            if cmp(my_ver, min_ver) < 0:
                g_messager.error("your BAE cli version is out of date, please run 'pip install bae --upgrade' to update")
                sys.exit(-1)
            if cmp(my_ver, cur_ver) < 0:
                g_messager.warning("new BAE cli version {0} availiable, please run 'pip install bae --upgrade'to update")
        except KeyError:
            pass

    def config(self, parser):
        try:
            k,v = parser.configitem.split("=")
            if v.lower() in ['y', 'yes', 'true', '1']:
                v = True
            elif v.lower() in ['n', 'no', 'false', '0']:
                v = False
            else:
                v = False

            setattr(self.globalconfig.model, k, v)
            self.globalconfig.save()
        except ValueError:
            g_messager.error("Config Format Error, Please use <Key>=<Value> pair (set one key once)")

    #Init Global Varaibles
    def login(self, parser):
        g_messager.trace("please visit %s to get a token" %(ONEKEY_ENTRY))
        access_token = g_messager.input("input your token:")
        self.globalconfig.model.user.access_token = access_token
        self.globalconfig.save()
        
        self.rest = BaeRest(access_token = access_token, debug = parser.debug)
        try:
            self._check_version()
            g_messager.trace("login success")
        except Exception:
            g_messager.warning("token is invalid")

    def app_support(self, parser):
        data = {}
        data['app_id'] = self._get_app_id(parser)

        ret = self.rest.get(API_ENTRY + "/bae/bce/app/precreate", data = data) 

        self.appconfig.model.solutions = [BaeSolution(_) for _ in ret["solutions"]]
        self.appconfig.save()

        g_messager.output("suppport language types:")
            
        for index, solution in enumerate(ret["solutions"]):
            g_messager.output("%d : %s" %(index+1, solution["name"]))
        self.appconfig.model.packages = [BasicPackage(_) for _ in ret["packageInfo"]["packlist"]]
        self.appconfig.save()
        g_messager.output("suppport packages:")
        index1=0
        self.supportpack={}
        for index, solution in enumerate(ret["packageInfo"]["packlist"]):
            if solution["type"] != "runtime":
                continue
            resources = []
            self.supportpack[index1]=solution
            index1+=1
            for k,v in solution["resource"].iteritems():
                resources.append(" %s %sM" %(k, v))
            g_messager.output("%d : %s" %(index+1, ",".join(resources)))
        userinfo=[ret["user"]]
        self.appconfig.model.userinfo = [BaeUserInfo(_) for _ in userinfo]
        self.appconfig.save()
    def app_setup(self, parser):
        if self.appconfig:
            answer=g_messager.yes_or_no("local app exists,clean up the .devapp file to setup again(Y) or  update app info(N) (Y/N):")
            if answer:
                cwd=os.getcwd()
                localdir= os.path.join(cwd,DEV_APP_CONFIG)
                try:
                    os.remove(localdir)
                except OSError, e:
                    g_messager.warning(str(e))
            else:
                parser.force = True
                self.app_update(parser)
                g_messager.trace("local app exists, try to update")
                return

        app_id = self._get_app_id(parser)
        #Require User Input a appid
        if not app_id:
            app_id = g_messager.input("please input your appid in baidu developer center (NOT BAE appid) : ")

        g_messager.output("your appid is {app_id}, BAE cli will setup this app in {curdir}".format(app_id = app_id, curdir= os.getcwd()))
        cwd = os.getcwd()
        self.appconfig = DevAppConfig(os.path.join(cwd, DEV_APP_CONFIG))

        try:
            self.appconfig.load_bae_app()
        except BaeConfigError:
            g_messager.warning("Load Bae Config Error, But setup will continued")

        self.appconfig.model.app_id   = app_id
        self.appconfig.bae_app_configs = self._app_cat(app_id)
        self.appconfig.save()

        for bae_app_config in self.appconfig.bae_app_configs:
            self._app_setup_bae(bae_app_config)

        #init support information
        self.app_support(parser)
        
    def app_update(self, parser):
        appid         = self._get_app_id(parser)
        bae_app_confs = self._get_bae_confs(appid, parser)
        if parser.force and self.appconfig:
            #TODO add delete logic
            #server_del_set = [conf for bae_app_confs if conf not in self.appconfig.bae_app_configs]
            #local_del_set  = [conf for self.appconfig.bae_app_configs if conf not in bae_app_confs]

            #for server_del_conf in server_del_set:
            #    g_messager.output("Local Cache {0} is Deleted in server side, would want delete local one?")
            pass

        if not bae_app_confs:
            return

        for bae_app_conf in bae_app_confs:
            self._app_setup_bae(bae_app_conf)
            bae_app_conf.save()

    def app_create(self, parser):
        app_id  =  self._get_app_id(parser)
        data = {}
        while True:
            appname = g_messager.input("input your appname")
            p = re.compile('^\w+$',re.S)
            if p.match(appname):
                if len(appname)<6 or len(appname)>32:
                     g_messager.output("Tips: The length of you appname should be in the range of [6~32]")
             
                else:
                    data["appname"]=appname
                    break
            else:
                g_messager.output("Tips: The  appname should be composed of numbers,letters and underline")
        data["version_type"] = g_messager.select("select code version tool" , ['svn', 'git'])[1]
        index, solution      = g_messager.select("programming language", self.appconfig.model.solutions, "name")
        data["solution"]     = solution.name
        data["solution_type"] = solution.type
        appid={}
        appid["app_id"] = app_id
        index_package, package = g_messager.select("package type", self.appconfig.model.packages, "resource",solution.packages,self.appconfig.model.userinfo)
        g_messager.output("The price of the package you choose is {0} yuan everyday".format(getattr(package,'price')))
        if data["solution_type"] == "web":
            while True:
                p = re.compile('^[A-Za-z0-9]+$',re.S)
                domain = g_messager.input("input your domain")
                if not domain:
                    g_messager.output("Warning:  domain can't be empty")
                elif not p.match(domain): 
                    g_messager.output("Warning:  The length of domain should be composed of numbers and small letters")
                elif len(domain)<6 or len(domain)>32:
                        g_messager.output("Warning:  The length of domain should be in the range of [6~32]")
                elif domain.endswith(".duapp.com"):
                        g_messager.output("Warning:  The length of domain should be in the range of [6~32] without .duapp.com")
                else:
                    temp={}
                    temp['domain']=domain
                    ret = self.rest.get(API_ENTRY + "/bae/bce/app/checkdomain", data=temp)
                    if "domain" in ret:
                        data["domain"]=ret["domain"]
                        break
                    else:
                        g_messager.output("Error:" + ret["error_msg"]) 
        data["name"]         = data["appname"]
        data["packageid"]    = str(index_package+100) #256M
        data["ins_num"]      = "1"
        requestid            = self._gen_request_id()
        data["requestid"]    = requestid
        data["app_id"]       = app_id
       
        ret = self.rest.get(API_ENTRY + "/bae/bce/app/createapp", data = data)
        new_bae_app = self._app_cat_bae(app_id, ret["bae_appid"])

        if self.appconfig:
            appdir = self.appconfig.appdir()
            self.appconfig.bae_app_configs.append(new_bae_app)
            self.appconfig.save()
            g_messager.trace("Starting create app, this may take several seconds...".format(ret["bae_appid"]))

        try:
            self._get_operation_log(requestid)
        except BaeCliError, e:
            g_messager.error(str(e))
        finally:
            self._app_setup_bae(new_bae_app)
            new_bae_app.save()

    def app_delete(self, parser):
        app_id       = self._get_app_id(parser)
        bae_app_conf = self._get_cur_bae_conf(app_id, parser)
        if not bae_app_conf:
            g_messager.error("%s not exists in local cache or in server" %(parser.baeappid))
            sys.exit(-1)

        data = {}
        data["app_id"]    = app_id
        data["bae_appid"] = bae_app_conf.model.appid   
        d_answer =False 
        if not parser.force:           
            answer=g_messager.yes_or_no("Do you want to delete the local app only( Don't delete the app on the BAE Sever) Y/N: ")
            if not answer:
                d_answer=g_messager.yes_or_no("WARNING!!! you will delete this app in the Server, this is UNRECOVERABLE action! Are "+\

                "you sure to delete this app Y/N:")
                if d_answer:
                    app_name = g_messager.input("please input the app's name {0}".format(bae_app_conf.model.appname))
                    if app_name != bae_app_conf.model.appname:
                        g_messager.warning("your input isn't right, delete bae app fail")
                        sys.exit(-1)
                    else:
                        ret = self.rest.get(API_ENTRY + "/bae/bce/app/delete", data = data) 
       
        else:
             ret = self.rest.get(API_ENTRY + "/bae/bce/app/delete", data = data)
        localdir = bae_app_conf.dirname()
        answer = False
        if localdir and os.path.exists(localdir):
            answer = g_messager.yes_or_no("Please make sure if we delete local_dir '{0}' (Y/N) :".format(localdir))
            if answer:
                try:
                    shutil.rmtree(localdir)
                except OSError, e:
                    g_messager.warning(str(e))
        if answer and d_answer:
            g_messager.trace("Delete " + ret["bae_appid"] + " with local_dir Success")
        elif answer and parser.force:
            g_messager.trace("Delete "+ret["bae_appid"]+"with local_dir Success")
        elif answer:
            g_messager.trace("Only delete the local_dir success")
        else:
            g_messager.trace("You give up deleting the local_dir")

    def _do_publish(self, bae_app_conf):
        data = {}
        data["bae_appid"] = bae_app_conf.model.appid
        data["url"]       = ""
        requestid         = self._gen_request_id()
        data["requestid"] = requestid

        ret = self.rest.get(API_ENTRY + "/bae/bce/app/republish", data = data)
        self._get_operation_log(requestid)

    def app_publish(self, parser):
        app_id        = self._get_app_id(parser)
        bae_app_conf  = self._get_cur_bae_conf(app_id, parser)
        
        if not bae_app_conf:
            g_messager.error("no local bae app found, please goto a bae app dir to publish code")
            sys.exit(-1)
        if not parser.local:
            self._do_publish(bae_app_conf)
        else:
            if bae_app_conf.model.lang_type == 'java':
                cmd = "bae_build %s %s %s"%(bae_app_conf.model.solution, bae_app_conf.dirname(), bae_app_conf.model.domain)
            else:
                cmd="bae_build %s %s %s"%(bae_app_conf.model.lang_type, bae_app_conf.dirname(), bae_app_conf.model.domain)
            os.system(cmd)
        
    def app_list(self, parser):
        if parser.detail:
            parser.force = True

        app_id        = self._get_app_id(parser)
        bae_app_confs = self._get_bae_confs(app_id, parser)

        if len(bae_app_confs) == 1:
            parser.single_list = True

        if parser.single_list:
            for bae_app_conf in bae_app_confs:
                g_messager.output(str(bae_app_conf.model)) 
        else:
            if parser.detail:
                print bae_app_detail_table("Application Detail Table", [bae_app_conf.model.tuple() for bae_app_conf in bae_app_confs])
            else:
                print bae_app_table("Application General Infos (use --detail to see more)", [bae_app_conf.model.tuple() for bae_app_conf in bae_app_confs])

        if not parser.force:
            self.appconfig.bae_app_configs = bae_app_confs
            self.appconfig.save()

    def service_list(self, parser):
        app_id  = self._get_app_id(parser)
        data    = {}

        data["app_id"] = app_id
        
        ret = self.rest.get(API_ENTRY + "/bae/service/usermgr/getServiceList", data = data)
        
        services    = [Service(service_conf) for service_conf in ret["serv_list"]]
        #add an index to each tuple
        service_tuple = [tuple([idx] + list(service)) for idx, service in 
                         (zip ([str(i) for i in range(1, len(services)+1)], [service.tuple() for service in services]))
                         ]
        
        print service_table("Bae Service list", service_tuple)

    def service_status(self, parser):
        app_id  = self._get_app_id(parser)
        data    = {}

        data["app_id"] = app_id

        ret = self.rest.get(API_ENTRY + "/bae/service/usermgr/getResourceList", data = data)
        resources = [Resource(resource_conf) for resource_conf in ret["resource_list"]]
        #This ugly code add index to a tuple
        resource_tuple = [tuple([idx] + list(resource)) for idx, resource in 
                         (zip ([str(i) for i in range(1, len(resources)+1)], [resource.tuple() for resource in resources]))
                         ]
        print resource_table("Your BAE Service List", resource_tuple)
        
    def service_create(self, parser):
        app_id  = self._get_app_id(parser)
        data    = {}

        
        ret = self.rest.get(API_ENTRY + "/bae/service/usermgr/getServiceList", data = data)
        services    = [Service(service_conf) for service_conf in ret["serv_list"]]
        service  = g_messager.select("Select a service", services)[1]
        data["service_name"]     = service.service_name  
        ret = self.rest.get(API_ENTRY + "/bae/service/usermgr/getServiceInfo",data=data)
        if service:
            #idx, package  = g_messager.select("Select a falvor", service.service_package) ### comments by pysqz
            data["service_name"]     = service.service_name
            #data["service_package"]  = idx-1 ### comments by pysqz
            data["service_package"]  = 1
            ret = self.rest.get(API_ENTRY + "/bae/service/usermgr/createResource", data = data)

        g_messager.success("Create service {0} success".format(service.service_name))
        for k, v in ret["resource_info"].iteritems():
            g_messager.output("{0} : {1}".format(k, v))

    def service_mysql(self, parser):
        def _progress(uri, flag = True):
            timeout = 300
            if uri.startswith("import"):
                status_info = {"1": "waiting", "2": "downloading", "3": "importing", "10": "imported", "-1": "fail to import"}
            else:
                status_info = {"1": "waiting", "2": "exporting", "3": "compressing", "4": "uploading", "10": "exported", "-1": "fail to export"}
            start_time = time.time() 
            while 1:
                job_status = self.rest.get(API_ENTRY + "/bae/sqld/db/" + uri, data = data)
                msg = status_info.get(job_status.get("job_status"), "")
                if job_status["job_status"] == "-1":
                    msg += "\t Err:%s"%job_status["errmsg"]
                g_messager.trace("Status: %s"%msg)
                if job_status["job_status"] in ["10", "-1"] or time.time() - start_time > timeout or not flag:
                    break
                time.sleep(1)  

        app_id = self._get_app_id(parser)
        data   = {}
        data["app_id"] = app_id

        ret = self.rest.get(API_ENTRY + "/bae/service/usermgr/getResourceList", data = data)
        database = filter(lambda x: x.service_name == "BaeMySQLService", [Resource(resource_conf) for resource_conf in ret["resource_list"]])
        if len(database) != 1:
            g_messager.warning("failed to get valid MySQL resource, please make sure your MySQL is enabled")
            sys.exit(-1)
        
        data["database_id"] = database[0].resource_name
        
        ### FIXME: the number of users' MySQL is more than 1, we also can deal with --db  
        #if not parser.database_id:
        #    g_messager.warning("please set argument '--db'")
        #    sys.exit(-1)
        #data["database_id"] = parser.database_id
        # comments by pysqz
     
        mysql_action = parser.mysqlaction 
        
        if mysql_action == "import":
            if parser.FROM.startswith("http://") or parser.FROM.startswith("https://"):
                data['url'] = parser.FROM
                rest_uri = "importTask" 
            else:
                if ":" not in parser.FROM:
                    g_messager.warning("please set bcs FROM with 'bucket:object'")
                    sys.exit(-1)
                data['bucket'], data['object'] = parser.FROM.split(":", 1)
                rest_uri = "importBCS"
            
            ret = self.rest.get(API_ENTRY + "/bae/sqld/db/" + rest_uri, data = data) 
            if ret.get("condition", -1) != 0:
                g_messager.error("failed to run mysql import, Err: %s"%ret["errmsg"])
                sys.exit(-1) 
                                   
            if parser.progress:
                _progress("importStat")
                                          
        elif mysql_action == "export":
            data['bucket'] = parser.TO
            data['compress'] = parser.format
                
            ret = self.rest.get(API_ENTRY + "/bae/sqld/db/exportTask", data = data)              
            if ret.get("condition", -1) != 0:
                g_messager.error("failed to run mysql export, Err: %s"%ret["errmsg"])
                sys.exit(-1)
 
            if parser.progress:
                _progress("exportStat")  

        elif mysql_action == "status":
            if not parser.JOB or parser.JOB not in ["import", "export"]:
                g_messager.warning("please set argument with 'import' or 'export'")
                sys.exit(-1)
            
            _progress("%sStat"%parser.JOB, False) 
             
        else:
            g_messager.error("invalid argument, just suportted (import | export | status)")

    def domain_list(self, parser):
        parser.force = True
        app_id       = self._get_app_id(parser)
        bae_app_conf = self._get_cur_bae_conf(app_id, parser)
        
        if bae_app_conf is None:
            g_messager.warning("please set baeappid or change to that directory")
            sys.exit(-1)
        if bae_app_conf.model.alias:
            g_messager.trace("domain alias: " + "||".join([str(alias) for alias in bae_app_conf.model.alias]))
        else:
            g_messager.warning("this app has no domain alias")

    def domain_add(self, parser):
        app_id       = self._get_app_id(parser)
        bae_app_conf = self._get_cur_bae_conf(app_id, parser)

        if not bae_app_conf:
            g_messager.error("Bae app not set or not exists in local cache")
            sys.exit(-1)

        data = {}
        data["alias_domain"] = parser.domain
        data["bae_appid"]   = bae_app_conf.model.appid
        ret = self.rest.get(API_ENTRY + "/bae/bce/app/adddomain", data = data)

        g_messager.trace("Bind to " + ret["alias_domain"] +" Success")

    def domain_delete(self, parser):
        app_id       = self._get_app_id(parser)
        bae_app_conf = self._get_cur_bae_conf(app_id, parser)

        if not bae_app_conf:
            g_messager.error("Bae app not set or not exists in local cache")
            sys.exit(-1)

        data = {}
        data["alias_domain"] = parser.domain
        data["bae_appid"]   = bae_app_conf.model.appid

        ret = self.rest.get(API_ENTRY + "/bae/bce/app/deldomain", data = data)

        g_messager.trace("Del domain alias" + ret["alias_domain"] +" Success")

    def instance_list(self, parser,flag=True):
        data = {}
        app_id        = self._get_app_id(parser)
        bae_app_conf  = self._get_cur_bae_conf(app_id,parser)

        if not bae_app_conf:
            g_messager.warning("Please use set baeappid or at least cd to a bae app directory")
            sys.exit(-1)

        data["bae_appid"] = bae_app_conf.model.appid

        ret = self.rest.get(API_ENTRY + "/bae/bce/app/catInsList", data = data)
        if flag:
            g_messager.output(str(BaeInstanceGroup(ret["ig_info"])))
        instances = [BaeInstance(ins).tuple() for ins in ret["ins_list"]]
        print instance_table("Instance List", instances)

    def instance_scale(self, parser):
        data = {}
        app_id       = self._get_app_id(parser)
        bae_app_conf = self._get_cur_bae_conf(app_id, parser)

        if not bae_app_conf:
            g_messager.warning("Please use set baeappid or at least cd to a bae app directory")
            sys.exit(-1)

        data["bae_appid"] = bae_app_conf.model.appid
        ret = self.rest.get(API_ENTRY + "/bae/bce/package/getapppackage", data = data)
        package_id=ret['content']['current']['packageid']
        ins_num = ret['content']['current']['insnum']
        package_id=package_id.split('+') 
        print "\n".join("Your current instance number(s) is {0} and package is {1}".format(ins_num,getattr(option,'resource')) for index,option in  enumerate(self.appconfig.model.packages) if getattr(option,'id')==package_id[0])        
        package_support = ret['content']['support']
        data["ins_num"]   = g_messager.input("input your scalnum")
        index_package, package       = g_messager.select("package type", self.appconfig.model.packages, "resource",package_support,self.appconfig.model.userinfo)
        data["packageid"]=str(index_package+100)
        g_messager.output("The price of the package is {0} yuan everday".format(getattr(package,'price')))
        ret = self.rest.get(API_ENTRY + "/bae/bce/package/setAppPackage", data = data)
        g_messager.trace("Scale instance number to {0} and change package Success".format(data['ins_num']))

        #self.instance_list(parser)

    def instance_restart(self, parser):
        data = {}
        app_id       = self._get_app_id(parser)
        bae_app_conf = self._get_cur_bae_conf(app_id, parser)

        if not bae_app_conf:
                g_messager.warning("Please use set baeappid or at least cd to a bae app directory")
                sys.exit(-1)

        if not parser.local:
            data["bae_appid"] = bae_app_conf.model.appid
            data["ins_ids"]   = json.dumps(parser.insids)
            ret = self.rest.get(API_ENTRY + "/bae/bce/app/restartIns", data = data)
            taskid = ret["taskid"]

            g_messager.trace("Restart success")
        else:
	    if bae_app_conf.model.lang_type == 'java':
                cmd = "bae_run %s start"%bae_app_conf.model.solution
            else:
                cmd = "bae_run %s start"%bae_app_conf.model.lang_type
            os.system(cmd)

    def instance_start(self, parser):
        data = {}
        app_id       = self._get_app_id(parser)
        bae_app_conf = self._get_cur_bae_conf(app_id, parser)

        if not bae_app_conf:
                g_messager.warning("Please use set baeappid or at least cd to a bae app directory")
                sys.exit(-1)
        if not parser.local:
            g_messager.trace("start your online server. Comming soon...")
        else:
	    if bae_app_conf.model.lang_type == 'java':
                cmd = "bae_run %s start"%bae_app_conf.model.solution
            else:
                cmd = "bae_run %s start"%bae_app_conf.model.lang_type
            os.system(cmd)

    def instance_stop(self, parser): 
        data = {}
        app_id       = self._get_app_id(parser)
        bae_app_conf = self._get_cur_bae_conf(app_id, parser)

        if not bae_app_conf:
                g_messager.warning("Please use set baeappid or at least cd to a bae app directory")
                sys.exit(-1)
        if not parser.local:
            g_messager.trace("stop your online server. Comming soon...")
        else:
	    if bae_app_conf.model.lang_type == 'java':
                cmd = "bae_run %s stop"%bae_app_conf.model.solution
            else:
                cmd = "bae_run %s stop"%bae_app_conf.model.lang_type
            os.system(cmd)

    def log_list(self, parser):
        
        data  = {}
        app_id       = self._get_app_id(parser)
        bae_app_conf = self._get_cur_bae_conf(app_id, parser)

        if not bae_app_conf:
            g_messager.error("Can't found your bae app or not set bae appid")
            sys.exit(-1)
        fid = parser.instanceid  
        if not fid:
            self.instance_list(parser,flag=False) 
            fid = g_messager.input("pleae input the instance id : ")

        data["app_id"]    = app_id
        data["bae_appid"] = bae_app_conf.model.appid
        data["fid"]       = fid
        data["log_type"]  = "local"

        ret = self.rest.get(API_ENTRY + "/bae/farsee/log/filelist", data = data)
        
        if 0 == len(ret["files"]):
            g_message.warning("no log file in container now")
        else:
            g_messager.output("log file names in container(%d) :" %(len(ret["files"])))
            g_messager.output("\n".join(ret["files"]))
            g_messager.warning("You can check the detail messages of every file by using the command  bae log tail/ bae log head ")
        
    def log_tail(self, parser):
        self._query_log(parser, "tail")

    def log_head(self, parser):
        self._query_log(parser, "head")

    def _query_log(self, parser, method):
        data = {}
        app_id       = self._get_app_id(parser)
        bae_app_conf = self._get_cur_bae_conf(app_id, parser)
        fid = parser.instanceid  
        if not bae_app_conf:
            g_messager.error("Can't found your bae app or not set bae appid")
            sys.exit(-1)
        if not fid:
            self.instance_list(parser,flag=False) 
            fid = g_messager.input("pleae input the instance id : ")  
        filename=parser.file
        if not filename:
            filename = g_messager.input("pleae input the filename you want to check : ") 

        data["app_id"]    = app_id
        data["bae_appid"] = bae_app_conf.model.appid
        data["fid"]       = fid
        data["filename"]  = filename
        data["limit"]     = parser.max or 50
        data["log_type"]  = "local"

        ret = self.rest.get(API_ENTRY + "/bae/farsee/log/%s" %(method), data = data)
        
        if 0 == len(ret["contents"]):
            g_messager.warning("no log in %s now" %(parser.file))
        else:
            g_messager.output("\n".join(ret["contents"]))
        
    def _get_app_id(self, parser):
        appid        = None

        if parser.appid:
            appid = parser.appid
        elif self.appconfig and self.appconfig.model.app_id:
            appid = self.appconfig.model.app_id
        return appid

    def _get_cur_bae_conf(self, appid, parser):
        appid = self._get_app_id(parser)
        baeappid = None
        conf     = None
        if self.appconfig and self.appconfig.cur_bae_app:
            baeappid = self.appconfig.cur_bae_app.model.appid
            conf     = self.appconfig.cur_bae_app
            if parser.force:
                conf = self._app_cat_bae(appid, conf.model.appid)
        
        if parser.baeappid:
            baeappid = parser.baeappid
            try:
                conf     = self._app_cat_bae(appid, baeappid)
            except BaeRestError as e:
                #try get conf from localdir
                if self.appconfig.bae_app_configs:
                    for bae_app_conf in self.appconfig.bae_app_configs:
                        if os.path.basename(bae_app_conf.dirname()) == parser.baeappid:
                            return bae_app_conf
                raise e
        if not conf:
            return None

        return conf

    def _get_bae_confs(self, appid, parser):
        confs = []

        if parser.baeappids:
            if parser.force:
                    confs = self._app_cat_bae(appid, parser.baeappids)
            elif self.appconfig:
                 confs = [conf for conf in self.appconfig.bae_app_configs if conf.model.appid in parser.baeappids]
        else:
            if self.appconfig:
                if self.appconfig.cur_bae_app:
                    confs = self._app_cat_bae(appid, [self.appconfig.cur_bae_app.model.appid])
                else:
                    if parser.force:
                        confs =  self._app_cat(self.appconfig.model.app_id)
                        self.appconfig.bae_app_configs = confs
                        self.appconfig.save()
                    else:
                        confs = self.appconfig.bae_app_configs

        return confs
               
    def _app_cat_bae(self, app_id, bae_appids):
        if not bae_appids:
            return []
        if not isinstance(bae_appids, list):
            bae_appids = [bae_appids]
            issingle   = True
        else:
            issingle   = False

        data = {}
        data["bae_appids"] = json.dumps(bae_appids)
        data["app_id"]     = app_id
        ret = self.rest.get(API_ENTRY + "/bae/bce/app/catCodeBatch", data = data)
        bae_app_configs = []

        for bae_app_conf in ret["appinfo"]:
            new_bae_app = BaeApp(bae_app_conf)
            g_messager.trace("Loading config for {0}".format(new_bae_app.name))
            if self.appconfig:
                app_dir    = self.appconfig.appdir()
                local_dir  = os.path.join(app_dir, new_bae_app.name)
                local_conf = os.path.join(local_dir, BAE_APP_CONFIG) 
                bae_config = BaeAppConfig(local_conf)

                if not os.path.exists(local_dir):
                    import distutils
                    import distutils.dir_util
                    distutils.dir_util.mkpath(local_dir)
                elif not os.path.isdir(local_dir):
                    g_messager.error(local_dir + "exists and it's not a dir")
                    sys.exit(-1)
            else:
                bae_config = BaeAppConfig()
            bae_config.model = new_bae_app       
            bae_app_configs.append(bae_config)

        if issingle:
            return bae_app_configs[0]
        else:
            return bae_app_configs

    def _app_setup_bae(self, bae_app_conf):
        bae_app = bae_app_conf.model

        g_messager.trace("begin setup {0}".format(bae_app.appid))
        try:
            tool = code_tool.get_tool(bae_app.version_type, bae_app.repos_url, bae_app_conf.dirname())
            tool.pull()
        except NotImplementError, e:
            g_messager.bug("Bae App {0} Tool not supported".format(str(bae_app)))

    def _app_cat(self, app_id = None):
        g_messager.trace("Loading Configs for Developer Application {appid}".format(appid = app_id))
        data = {}
        data["app_id"]   = app_id
        data["status"]   = "all"
        data["limit"]    = "10000"
        data["start"]    = "0"
        ret = self.rest.get(API_ENTRY + "/bae/bce/app/list", data = data)

        bae_app_ids = [bae_app_conf["appid"] for bae_app_conf in ret["app_list"]]
        bae_app_conf_list = self._app_cat_bae(app_id, bae_app_ids)
        
        return bae_app_conf_list

    def _gen_request_id(self):
        import uuid
        return uuid.uuid4()

    
    def _format_operation_log(self, log_json):
        END     = 0
        ERROR   = 1
        WARNING = 2
        TRACE   = 3

        try:
            import json
            log = json.loads(log_json)

	    tm =  log["timestamp"]
            date  = time.strftime("%T", time.localtime(tm))
            logfmt = "{0} : {1}".format(date, log["log"])

            if log["status"] == 3:
                g_messager.trace(logfmt)
            elif log["status"] == 2:
                g_messager.warning(logfmt)
            elif log["status"] == 1:
                raise BaeCliError(logfmt)
            else:
                g_messager.success(logfmt)
                return True
        except KeyError:
            pass

        return False

    def _get_operation_log(self, requestid):
        TIMEOUT = 60
        start   = int(time.time())
        log_end = False
        data     = {}
        data["requestid"] = requestid
        
        while True:
            ret = self.rest.get(API_ENTRY + "/bae/bce/app/clilog", data, timeout =1 )

            for log in ret["logs"]:
                log_end =  self._format_operation_log(log)
                
            now = int(time.time())
            if log_end :
                break
            if now - start >= TIMEOUT:
                raise BaeCliError("get Server infomation error")
            else:
                time.sleep(1)
