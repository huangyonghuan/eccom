# -*- coding: UTF-8 -*- 
import mysqlconn,pexpect,sys,re,os,deviceshell,time,MySQLdb
DEVICE_NAMES=[]
LOGINCONTENT=''
TIMEOUTCONTENT=''

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
    i = ssh.expect(module['successprompts'] + module['superprompts'], timeout=5)
    if i < len(module['successprompts'] + module['superprompts']):
        before_str=ssh.before.lstrip()
        after_str=ssh.after
        devname = before_str.split('\r\n')[len(before_str.split('\r\n'))-1].replace('[','\\[').replace(']','\\]').replace('(','\\(').replace(')','\\)').replace('<','\\<').replace('>','\\>') + '[\\s\\S]{0,30}' + after_str
        DEVICE_NAMES.append(devname)
        devname = before_str.split('\r\n')[len(before_str.split('\r\n'))-1] + after_str
        DEVICE_NAMES.append(devname.replace('[','\\[').replace(']','\\]').replace('(','\\(').replace(')','\\)').replace('<','\\<').replace('>','\\>'))

'''
    输入命令,并获取返回结果
'''
def sendCommand(ssh,cmd,module):
    global TIMEOUTCONTENT
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
        prompts = prompts + module['successprompts'] + module['superprompts'] + module['specialprompts']
    else:
        prompts = prompts + DEVICE_NAMES + module['specialprompts']
    if cmd.endswith('?'):
        ssh.send(cmd)
    else:
        ssh.sendline(cmd)
    i = ssh.expect(prompts + module['more'],timeout=60)
    if i == 0:
        res += dealASCII(ssh.before)
    elif i == 1:
        TIMEOUTCONTENT += "====================\n"
        TIMEOUTCONTENT += "cmd:" +cmd + '\n'
        TIMEOUTCONTENT += "prompts:" + str(prompts + module['more']) + "\n"
        TIMEOUTCONTENT += "ssh.before:" + str(ssh.before) + "\n"
        TIMEOUTCONTENT += str(ssh)+'\n'
        TIMEOUTCONTENT += "====================\n"
        res += dealASCII(ssh.before)
    elif i < len(prompts):
        res += dealASCII(ssh.before) + ssh.after
        while (ssh.buffer.strip() != ''):
            i = ssh.expect(prompts,timeout=5)
            if i == 0:
                res += dealASCII(ssh.before)
                break
            elif i == 1:
                res += dealASCII(ssh.before)
                break
            elif i < len(prompts):
                res += dealASCII(ssh.before) + ssh.after
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
def login(ssh,username,assword,enablepass,module):
    global LOGINCONTENT
    i = ssh.expect([pexpect.EOF,pexpect.TIMEOUT,"Are you sure you want to continue connecting (yes/no)?"] + module['passwordprompts'], timeout=10)
    if i == 0:
        msg='ssh连接已关闭'
        LOGINCONTENT += ssh.before
        return "start login ssh closed" + ssh.before
    elif i == 1:
        msg='ssh登陆超时'
        LOGINCONTENT += ssh.before
        return "start login ssh timeout" + ssh.before
    elif i == 2:
        LOGINCONTENT += ssh.before + ssh.after
        ssh.sendline("yes")
        i = ssh.expect([pexpect.EOF,pexpect.TIMEOUT] + module['userprompts'] + module['passwordprompts'], timeout=5)
        if i == 0:
            msg='ssh连接已关闭'
            LOGINCONTENT += ssh.before
            return "ssh closed"
        elif i == 1:
            msg='ssh登陆超时'
            LOGINCONTENT += ssh.before
            return "ssh timeout"
        elif i>1 and i < 2+ len(module['userprompts']):
            LOGINCONTENT += ssh.before + ssh.after
            ssh.sendline(username)
            i = ssh.expect([pexpect.EOF,pexpect.TIMEOUT] + module['passwordprompts'], timeout=5)
            if i == 0:
                msg='ssh连接已关闭'
                LOGINCONTENT += ssh.before
                return "ssh closed"
            elif i == 1:
                msg='ssh登陆超时'
                LOGINCONTENT += ssh.before
                return "ssh timeout"
            elif i>1 and i < 2+ len(module['passwordprompts']):
                LOGINCONTENT += ssh.before + ssh.after
                msg='需要输入密码'
        elif i < 2+len(module['userprompts'])+len(module['passwordprompts']):
            LOGINCONTENT += ssh.before + ssh.after
            msg='需要输入密码'
        else:
            return "unkown error"
    elif i>2 and i < 3+len(module['passwordprompts']):
        LOGINCONTENT += ssh.before + ssh.after
        msg='需要输入密码'
    else:
        LOGINCONTENT += ssh.before
        return "unkown error"
    ssh.sendline(password)
    i = ssh.expect([pexpect.EOF,pexpect.TIMEOUT] + module['successprompts'] + module['superprompts'], timeout=module['logintimeout'])
    if i == 0:
        msg='ssh连接已关闭'
        LOGINCONTENT += ssh.before
        return "ssh closed"
    elif i == 1:
        msg='ssh登陆超时'        
        LOGINCONTENT += ssh.before
        return "ssh timeout"
    elif i>1 and i < 2+len(module['successprompts']+module['superprompts']):
        LOGINCONTENT += ssh.before + ssh.after
        ccc = ssh.before
        if 'Configuration Professional' in ccc:
            ssh.expect([pexpect.EOF,pexpect.TIMEOUT],timeout=1)
            cc = ssh.before
            ssh.buffer=''
        #enable
        encmd = module['enablecmd']
        if encmd != "" and enablepass != None:
            ssh.sendline(encmd)
            i = ssh.expect([pexpect.EOF,pexpect.TIMEOUT] + module['enableneedpass'] + module['successprompts'] + module['superprompts'], timeout=5)
            if i == 0:
                msg='ssh连接已关闭'
                LOGINCONTENT += ssh.before
                return "ssh closed"
            elif i == 1:
                msg='ssh登陆超时'
                LOGINCONTENT += ssh.before
                return "ssh timeout"
            elif i>1 and i < 2+len(module['enableneedpass']):
                LOGINCONTENT += ssh.before + ssh.after
                if enablepass == 'none':
                    ssh.sendline('')
                else:
                    ssh.sendline(enablepass)
                i = ssh.expect([pexpect.EOF,pexpect.TIMEOUT] + module['successprompts'] + module['superprompts'], timeout=5)
                if i == 0:
                    LOGINCONTENT += ssh.before
                    return "ssh closed"
                elif i == 1:
                    LOGINCONTENT += ssh.before
                    return "ssh timeout"
                elif i>1 and i < 2+len(module['successprompts']):
                    LOGINCONTENT += ssh.before + ssh.after
                    return "enter enable failed.enablepass error"
                elif i >= 2+len(module['successprompts']) and i < 2+len(module['successprompts'] + module['superprompts']):
                    LOGINCONTENT += ssh.before + ssh.after
                    getDeviceName(ssh,module)
                    return "success"
            elif i >= 2+len(module['enableneedpass']) and i < 2+len(module['enableneedpass'])+len(module['successprompts']):
                LOGINCONTENT += ssh.before + ssh.after
                return "enter enable failed.enablepass error"
            elif i >= 2+len(module['enableneedpass']+module['successprompts']) and i < 2+len(module['enableneedpass'])+len(module['successprompts'] + module['superprompts']):
                LOGINCONTENT += ssh.before + ssh.after
                getDeviceName(ssh,module)
                return "success"
            else:
                LOGINCONTENT += ssh.before
                return "unkown error"
        else:
            LOGINCONTENT += ssh.before + ssh.after
            getDeviceName(ssh,module)
            return "success"
    #elif i >= 2 + len(module['successprompts']) and i < 2 + len(module['successprompts'] + module['superprompts']):
        #LOGINCONTENT += ssh.before + ssh.after
        #getDeviceName(ssh,module)
        #return "success"
    else:
        LOGINCONTENT += ssh.before
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
    if '\\n' in cmds:
        for cmd in cmds.split('\\n'):
           if cmd != '':
             tmpstr = sendCommand(ssh,cmd,module)
             res = res + tmpstr
             waitcmds = module['waitcmds']
             for wait_cmd in waitcmds.keys():
                 if getStrMatch(cmd,wait_cmd):
                     time.sleep(waitcmds[wait_cmd])
    elif '\n' in cmds:
        for cmd in cmds.split('\n'):
           if cmd != '':
             tmpstr = sendCommand(ssh,cmd,module)
             res = res + tmpstr
             waitcmds = module['waitcmds']
             for wait_cmd in waitcmds.keys():
                 if getStrMatch(cmd,wait_cmd):
                     time.sleep(waitcmds[wait_cmd])
    else:
        for cmd in cmds.split('<br>'):
            if cmd != '':
                tmpstr = sendCommand(ssh,cmd,module)
                res = tmpstr
                #判断是否返回错误
                for errorstr in module['errorlist']:
                    if getStrMatch(tmpstr,errorstr):
                        return res
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

'''
    处理ASCII码提示符
'''
def dealASCII(result):
    temp_res=[]
    for line in result.split('\r\n'):
        if line.find('\x1b') != -1:
            line = re.sub('\\x1b\[\d+[D|m]','',line)
            line = re.sub('\\x1b\[K','',line)
            line = re.sub('\\x1b\[\d+;\d+H','',line)
            line = re.sub('\\x1b\[\?\d+h','',line)
            line = re.sub('\\x1b\[m','',line)
            line = re.sub('\\x1b=','',line)
            temp_res.append(line.strip())
        else:
            temp_res.append(line.strip())
    return "\r\n".join(temp_res)

if __name__ == '__main__':
    username = sys.argv[1]
    password = sys.argv[2]
    enablepw = sys.argv[3]
    ip = sys.argv[4]
    factory = sys.argv[5]
    cmd = sys.argv[6]
    module=deviceshell.getModuleById(factory)
    if username=="" or ip=="" or password == "" or cmd == "":
        result = 'error!user is null or ip is null or passwd is null.Please check!'
        exit
    if factory.startswith('1.3.6.1.4.1.5651'):
        time.sleep(5)
    os.system("sed -i '/" + ip + "/'d ~/.ssh/known_hosts")
    sql = "select sshversion from t_cmdb_ci_device where ipaddr=\'"+ip+"\'"
    sshversion = optionDatabase(sql)
    if sshversion is None:
        sshversion = [None]
    try:
      #sshcmd = "ssh " + username + "@" + ip
      #ssh = pexpect.spawn(sshcmd,timeout=180)
        if sshversion[0] is None:
            sshcmd = "ssh " + username + "@" + ip
            ssh = pexpect.spawn(sshcmd,timeout=180)
            res = login(ssh,username,password,enablepw,module)
            if res == "success":
                sendTerminal(ssh,module)
                result = sendCommands(ssh,module,cmd)
                print result
            elif res.find('start login ssh closed') != -1 or res.find('start login ssh timeout') != -1:
                sshcmd = "ssh -1 " + username + "@" + ip
                ssh = pexpect.spawn(sshcmd,timeout=180)
                res = login(ssh,username,password,enablepw,module)
                if res == "success":
                    sendTerminal(ssh,module)
                    result = sendCommands(ssh,module,cmd)
                    print result
                else:
                    print LOGINCONTENT
                    print 'login failed:' + res
            else:
                print LOGINCONTENT
                print 'unkown error'+ res
        else:
            if sshversion[0] == 1L:
                sshcmd = "ssh -1 " + username + "@" + ip
            else:
                sshcmd = "ssh " + username + "@" + ip
            ssh = pexpect.spawn(sshcmd,timeout=180)
            res = login(ssh,username,password,enablepw,module)
            if res == "success":
                sendTerminal(ssh,module)
                result = sendCommands(ssh,module,cmd)
                print result
            else:
                print LOGINCONTENT
                print 'login failed:' + res
    finally:
      ssh.close()
    if TIMEOUTCONTENT != '':
       f = open('/batch_log/'+ip + '_' + time.strftime("%Y%m%d%H%M%S",time.localtime()) +'.log','w')
       f.write(TIMEOUTCONTENT)
       f.close()
