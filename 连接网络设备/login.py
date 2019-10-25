# -*- coding: UTF-8 -*- 
import mysqlconn,pexpect,sys,re,os,deviceshell,time,MySQLdb
DEVICE_NAMES=[]

'''
    比较字符串是否满足条件
    str:传入字符串
    matchstr:需要匹配的字符串,可以是正则表达式
'''
def getStrMatch(str,matchstr):
    if str.lower().find(matchstr.lower()) != -1:
        return True
    elif re.match(matchstr.lower(),str.lower()) != None:
        return True
    else:
        return False

'''
    获取设备登陆提示符
    获取到passwordprompts时认为结束
'''
def getDeviceName(ssh,module):
    ssh.sendline('')
    i = ssh.expect(module['successprompts']+module['superprompts'], timeout=5)
    if i < len(module['successprompts']+module['superprompts']):
        devname = ssh.before.lstrip() + ssh.after
        DEVICE_NAMES.append(devname.replace('[','\\[').replace(']','\\]'))

'''
    输入命令,并获取返回结果
'''
def sendCommand(ssh,cmd,module):
    res = ''
    #判断是否需要重新获取提示符
    getprompt_flag = False
    for getprompt in module['getprompts']:
        #if cmd.find(getprompt) != -1:
        if getStrMatch(cmd,getprompt):
            getprompt_flag = True
            break
    prompts = [pexpect.EOF,pexpect.TIMEOUT]
    if getprompt_flag == True:
        prompts = prompts + module['successprompts']+module['superprompts']
    else:
        prompts = prompts + DEVICE_NAMES
    ssh.sendline(cmd)
    i = ssh.expect(prompts + module['more'],timeout=10)
    if i == 0:
        res += dealASCII(ssh.before)
    elif i == 1:
        res += dealASCII(ssh.before)
    elif i < len(prompts):
        res = dealASCII(ssh.before) + ssh.after
    elif i >= len(prompts) and i < len(prompts) + len(module['more']):
        #more处理
        while (i >= len(prompts)):
            tmp = dealASCII(ssh.before)
            res += tmp
            ssh.send(module['more_enters'][i-len(prompts)])
            i = ssh.expect(prompts + module['more'],timeout=10)
        res += dealASCII(ssh.before) + str(ssh.after)
    else:
        res+="unkown error"
    if getprompt_flag == True:
        getDeviceName(ssh,module)
    return res


'''
    登陆设备
'''
def login(ssh,username,password,enablepass,module):
    logincontent = ''
    i = ssh.expect([pexpect.EOF,pexpect.TIMEOUT,"Are you sure you want to continue connecting (yes/no)?"] + module['passwordprompts'], timeout=20)
    if i == 0:
        msg='ssh连接已关闭'
        print ssh.before
        return "start login ssh closed"
    elif i == 1:
        msg='ssh登陆超时'
        print ssh.before
        return "start login ssh timeout"
    elif i == 2:
        logincontent += ssh.before + ssh.after
        ssh.sendline("yes")
        i = ssh.expect([pexpect.EOF,pexpect.TIMEOUT] + module['userprompts'] + module['passwordprompts'], timeout=5)
        if i == 0:
            msg='ssh连接已关闭'
            print logincontent + ssh.before
            return " start login ssh closed"
        elif i == 1:
            msg='ssh登陆超时'
            print logincontent + ssh.before
            return "start login ssh timeout"
        elif i>1 and i < 2+ len(module['userprompts']):
            logincontent += ssh.before + ssh.after
            ssh.sendline(username)
            i = ssh.expect([pexpect.EOF,pexpect.TIMEOUT] + module['passwordprompts'], timeout=5)
            if i == 0:
                msg='ssh连接已关闭'
                print logincontent + ssh.before
                return "ssh closed"
            elif i == 1:
                msg='ssh登陆超时'
                print logincontent + ssh.before
                return "ssh timeout"
            elif i>1 and i < 2+ len(module['passwordprompts']):
                logincontent += ssh.before + ssh.after
                msg='需要输入密码'
        elif i < 2+len(module['userprompts'])+len(module['passwordprompts']):
            logincontent += ssh.before + ssh.after
            msg='需要输入密码'
        else:
            return "unkown error"
    elif i>2 and i < 3+len(module['passwordprompts']):
        logincontent += ssh.before + ssh.after
        msg='需要输入密码'
    else:
        return "unkown error"
    ssh.sendline(password)
    i = ssh.expect([pexpect.EOF,pexpect.TIMEOUT] + module['successprompts'] + module['superprompts'], timeout=module['logintimeout'])
    if i == 0:
        msg='ssh连接已关闭'
        print logincontent + ssh.before
        return "ssh closed"
    elif i == 1:
        msg='ssh登陆超时'
        print logincontent + ssh.before  
        return "ssh timeout"
    elif i>1 and i < 2+len(module['successprompts']+module['superprompts']):
        logincontent += ssh.before + ssh.after
        while ssh.buffer.strip() != '':
            ssh.expect([pexpect.EOF,pexpect.TIMEOUT] + module['successprompts'] + module['superprompts'],timeout=1)
            if i == 0:
                msg='ssh连接已关闭'
                print logincontent + ssh.before
                return "ssh closed"
            elif i == 1:
                msg='ssh登陆超时'
                print logincontent + ssh.before
                return "ssh timeout"
            else:
                logincontent += ssh.before + ssh.after
        #for i in range(0,2):
            #ssh.expect([pexpect.EOF,pexpect.TIMEOUT],timeout=1)
            #cc = ssh.before
            #ssh.buffer=''
            #if cc =='':
            #    break
            #else:
            #    logincontent += ssh.before
        #enable
        encmd = module['enablecmd']
        if encmd != "" and enablepass != None:
            ssh.sendline(encmd)
            i = ssh.expect([pexpect.EOF,pexpect.TIMEOUT] + module['enableneedpass'] + module['successprompts'] + module['superprompts'], timeout=5)
            if i == 0:
                msg='ssh连接已关闭'
                print logincontent + ssh.before
                return "ssh closed"
            elif i == 1:
                msg='ssh登陆超时'
                print logincontent + ssh.before
                return "ssh timeout"
            elif i>1 and i < 2+len(module['enableneedpass']):
                logincontent += ssh.before + ssh.after
                if enablepass == 'none':
                    ssh.sendline('')
                else:
                    ssh.sendline(enablepass)
                i = ssh.expect([pexpect.EOF,pexpect.TIMEOUT] + module['successprompts'] + module['superprompts'], timeout=5)
                if i == 0:
                    print logincontent + ssh.before
                    return "ssh closed.enablepass error"
                elif i == 1:
                    print logincontent + ssh.before
                    return "ssh timeout.enablepass error"
                elif i>1 and i < 2+len(module['successprompts']):
                    print logincontent + ssh.before + ssh.after
                    return "enter enable failed,enablepass error"
                elif i >= 2+len(module['successprompts']) and i < 2 + len(module['successprompts'] + module['superprompts']):
                    logincontent += ssh.before + ssh.after
                    if ssh.before.find('Access denied') != -1:
                        print "enablepass error"
                        print logincontent
                        return 'enablepass error'
                    else:
                        getDeviceName(ssh,module)
                        print logincontent
                        return "success"
            elif i >= 2+len(module['enableneedpass']) and i < 2+len(module['enableneedpass'])+len(module['successprompts']):
                print logincontent + ssh.before + ssh.after
                return "enter enable failed,enablepass error"
            elif i >= 2+len(module['enableneedpass'])+len(module['successprompts']) and i < 2+len(module['enableneedpass'])+len(module['successprompts'] + module['superprompts']):
                logincontent += ssh.before + ssh.after
                getDeviceName(ssh,module)
                print logincontent
                return "success"
            else:
                return "unkown error"
        else:
            logincontent += str(ssh.before)
            getDeviceName(ssh,module)
            print logincontent
            return "success"
    #elif i >= 2+len(module['successprompts']) and i<2+len(module['successprompts'] + module['superprompts']):
        #logincontent += str(ssh.before) + str(ssh.after)
        #getDeviceName(ssh,module)
        #print logincontent
        #return "success"
    else:
        return "unkown error"

'''
    输入一屏显示命令
'''
def sendTerminal(ssh,module):
    ter_cmds = module['ter_len_0']
    if len(ter_cmds)>0:
        for cmd in ter_cmds:
            sendCommand(ssh,cmd,module)

'''
    批量执行命令
'''
def sendCommands(ssh,module,cmds):
    res = ''
    for cmd in cmds.split(';'):
        if cmd != '':
            tmpstr = sendCommand(ssh,cmd,module)
            res += tmpstr
            #判断是否返回错误
            #for errorstr in module['errorlist']:
                #if getStrMatch(tmpstr,errorstr):
                    #return res
            waitcmds = module['waitcmds']
            for wait_cmd in waitcmds.keys():
                if getStrMatch(cmd,wait_cmd):
                    time.sleep(waitcmds[wait_cmd])
    return res

'''
    数据库操作
'''
def optionDatabase(sql):
    try:
       db = MySQLdb.connect(mysqlconn.mysqlip,'eccom','eccom','neteagle3')
       cursor = db.cursor()
       cursor.execute(sql)
       result = cursor.fetchone()
       db.commit()
       return result
    except:
       db.rollback()
    finally:
       db.close()

def sendLogoutcmd(ssh,module):
    res = ''
    logout_cmds = module['logoutcmd']
    if len(logout_cmds)>0:
        for cmd in logout_cmds:
            prompts = [pexpect.EOF,pexpect.TIMEOUT]
            prompts = prompts + module['successprompts']
            ssh.sendline(cmd)
            i = ssh.expect(prompts + module['more'],timeout=10)
            if i == 0:
                res += dealASCII(ssh.before)
            elif i == 1:
                res += dealASCII(ssh.before)
            elif i < len(prompts):
                res = dealASCII(ssh.before) + ssh.after
            else:
                res += dealASCII(ssh.before)
    print res

'''
    处理ASCII码提示符
'''
def dealASCII(result):
    temp_res=[]
    for line in result.split('\r\n'):
        if line.find('\x1b') != -1:
            temp_res.append(re.sub('\\x1b\[\d+D','',line).strip())
        else:
            temp_res.append(line.strip())
    return "\r\n".join(temp_res)

if __name__ == '__main__':
    username = sys.argv[1]
    password = sys.argv[2]
    enablepw = sys.argv[3]
    ip = sys.argv[4]
    factory = sys.argv[5]
    module=deviceshell.getModuleById(factory)
    if username=="" or ip=="" or password == "":
        result = 'error!user is null or ip is null or passwd is null.Please check!'
        exit
    os.system("sed -i '/" + ip + "/'d ~/.ssh/known_hosts")
    sshflag = 1
    sshcmd = "ssh "+username+"@"+ip
    sql = "select sshversion from t_cmdb_ci_device where ipaddr=\'"+ip+"\'"
    sshversion = optionDatabase(sql)
    if sshversion is None:
      sshversion = [None]
    if sshversion[0] is None:
        try :
            ssh = pexpect.spawn(sshcmd,timeout=180)
            i = ssh.expect([pexpect.EOF,pexpect.TIMEOUT,"Are you sure you want to continue connecting (yes/no)?"], timeout=5)
            if i == 0:
                sshflag = 1
            elif i == 1:
                print 'logintimeout'
                exit
            else:
                sshflag = 2
        finally:
            ssh.close()
        if sshflag == 1:
            sshcmd = "ssh -1 "+username+"@"+ip
            ssh = pexpect.spawn(sshcmd,timeout=180)
            updateSql = "update t_cmdb_ci_device set sshversion=1 where ipaddr=\'"+ip+"\'"
            optionDatabase(updateSql)
            updateSql = "update t_cmdb_ci_hardware set sshversion=1 where ipaddr=\'"+ip+"\'"
            optionDatabase(updateSql)
        else:
            sshcmd = "ssh "+username+"@"+ip
            ssh = pexpect.spawn(sshcmd,timeout=180)
            updateSql = "update t_cmdb_ci_device set sshversion=2 where ipaddr=\'"+ip+"\'"
            optionDatabase(updateSql)
            updateSql = "update t_cmdb_ci_hardware set sshversion=2 where ipaddr=\'"+ip+"\'"
            optionDatabase(updateSql)
        try:
            res = login(ssh,username,password,enablepw,module)
            if res == "success":
                sendLogoutcmd(ssh,module)
                print 'login success'
            else:
                print 'login failed:' + res
        finally:
            ssh.close()
    else:
        if sshversion[0] == 1L:
           try:
              sshcmd = "ssh -1 "+username+"@"+ip
              ssh = pexpect.spawn(sshcmd,timeout=180)
              res = login(ssh,username,password,enablepw,module)
              if res == "success":
                  sendLogoutcmd(ssh,module)
                  print 'login success'
              else:
                  if res == "start login ssh timeout" or res == "start login ssh closed" :
                      sshcmd = "ssh "+username+"@"+ip
                      ssh = pexpect.spawn(sshcmd,timeout=180)
                      res = login(ssh,username,password,enablepw,module)
                      if res == "success":
                          updateSql = "update t_cmdb_ci_device set sshversion=2 where ipaddr=\'"+ip+"\'"
                          optionDatabase(updateSql)
                          updateSql = "update t_cmdb_ci_hardware set sshversion=2 where ipaddr=\'"+ip+"\'"
                          optionDatabase(updateSql)
                          sendLogoutcmd(ssh,module)
                          print "login success"
                      else:
                          print 'login failed:' + res
                  else:
                      print 'login failed:' + res
           finally:
              ssh.close()
        else:
           try:
              sshcmd = "ssh "+username+"@"+ip
              ssh = pexpect.spawn(sshcmd,timeout=180)
              res = login(ssh,username,password,enablepw,module)
              if res == "success":
                  sendLogoutcmd(ssh,module)
                  print 'login success'
              else:
                  if res == "start login ssh timeout" or res == "start login ssh closed" :
                      sshcmd = "ssh -1 "+username+"@"+ip
                      ssh = pexpect.spawn(sshcmd,timeout=180)
                      res = login(ssh,username,password,enablepw,module)
                      if res == "success":
                          updateSql = "update t_cmdb_ci_device set sshversion=1 where ipaddr=\'"+ip+"\'"
                          optionDatabase(updateSql)  
                          updateSql = "update t_cmdb_ci_hardware set sshversion=1 where ipaddr=\'"+ip+"\'"
                          optionDatabase(updateSql)  
                          sendLogoutcmd(ssh,module)
                          print "login success"
                      else:
                          print 'login failed:' + res
                  else:
                      print 'login failed:' + res
           finally:
              ssh.close()
