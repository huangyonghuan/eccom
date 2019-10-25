constants = ['logintimeout','passwordprompts','enablecmd','enableneedpass','successprompts','superprompts','more','more_enters','ter_len_0','getprompts','errorlist','specialprompts','logoutcmd']
deviceshell={
	'1.3.6.1.4.1.9':{#cisco
		'passwordprompts':['assword:']
		,'enablecmd':'en'
		,'enableneedpass' : ['assword:','#:','(enable)']
		,'successprompts':['>']
		,'superprompts' : ['#']
		,'more':['--More--','<--- More --->','Press Enter to continue or <ctrl-z> to abort','Press Enter to continue or <Ctrl-Z> to abort...','--More or \(q\)uit current module or <ctrl-z> to abort']
		,'more_enters':[' ',' ',' ',' ',' ']
		,'ter_len_0' : ['ter len 0']
		,'getprompts' : ['conf t','config t','^interface.*','ter len 0']
		,'errorlist' : ['Invalid input detected','^','Unknown command or computer name']
	},
        '1.3.6.1.4.1.9.1.0':{#wlc
                'passwordprompts':['assword:']
                ,'enablecmd':''
                ,'enableneedpass' : ['assword:','#:','(enable)']
                ,'successprompts':['#','>']
                ,'more':['--More--','<--- More --->','Press Enter to continue or <ctrl-z> to abort','Press Enter to continue or <Ctrl-Z> to abort...','--More or \(q\)uit current module or <ctrl-z> to abort']
                ,'more_enters':[' ',' ',' ',' ',' ']
                ,'ter_len_0' : []
                ,'getprompts' : ['conf t','config t','^interface.*','ter len 0']
                ,'errorlist' : ['Invalid input detected','^','Unknown command or computer name']
        },
	'1.3.6.1.4.1.4881':{#ruijie
		'passwordprompts':['assword:']
		,'enablecmd':'en'
		,'enableneedpass' : ['assword:','#:','(enable)']
		,'successprompts':['>']
		,'superprompts' : ['#']
		,'more':['--More--','<--- More --->']
		,'more_enters':[' ',' ']
		,'ter_len_0' : ['ter len 0']
		,'getprompts' : ['conf t','config t','^interface.*','ter len 0']
		,'errorlist' : ['Invalid input detected','^','Unknown command or computer name']
	},
	'1.3.6.1.4.1.9.1.119':{#ciscoasa
		'extend' : '1.3.6.1.4.1.9'
		,'ter_len_0' : ['ter pager 0']
		,'getprompts' : ['conf t','config t','^interface.*','ter len 0','changeto']
	},
	'1.3.6.1.4.1.14331.1.4' : {#topsec
		'passwordprompts':['assword:']
		,'enablecmd':''
		,'enableneedpass' : ['assword:','#:','(enable)']
		,'successprompts':['#','>','%']
		,'more':['--More--']
		,'more_enters':[' ']
		,'ter_len_0' : ['terminal len 0']
		,'getprompts' : ['terminal len 0']
		,'errorlist' : ['8010']
		,'waitcmds' : {'ha sync to-peer':30}
	},
	'1.3.6.1.4.1.27971' : {#infosec
		'logintimeout':120
		,'passwordprompts':['assword:']
		,'enablecmd':'enable'
		,'enableneedpass' : ['assword:']
		,'more':['--More--']
		,'more_enters':[' ']
		,'ter_len_0' : []
		,'getprompts' : []
		,'errorlist' : []
	},
	'1.3.6.1.4.1.2011':{#huawei
		'passwordprompts':['assword:']
		,'enablecmd':''
		,'enableneedpass' : []
		,'successprompts':['#','>',']']
		,'more':['---- More ----']
		,'more_enters':[' ']
		,'ter_len_0' : ['screen-length 0 temporary']
		,'getprompts' : ['quit','sys','save','acl name.*','route-policy.*','ospf.*','user-interface.*','undo.*']
		,'errorlist' : ['Unrecognized command found at','Wrong parameter found at','Incomplete command found at','Too many parameters found at','Ambiguous command found at']
		,'logoutcmd' : ['quit']
	},
	'1.3.6.1.4.1.25506' : {
		'passwordprompts':['assword:']
		,'enablecmd':''
		,'enableneedpass' : []
		,'successprompts':['#','>',']']
		,'more':['---- More ----']
		,'more_enters':[' ']
		,'ter_len_0' : ['screen-length disable']
		,'getprompts' : ['quit','system-view']
		,'errorlist' : []
		,'logoutcmd':['quit']
	},
	'1.3.6.1.4.1.2636': {
		'passwordprompts':['assword:']
		,'enablecmd':''
		,'enableneedpass' : []
		,'successprompts':['#','>',']']
		,'more':['\[edit\]','---\(more\)---','--\(more \d+%\)---']
		,'more_enters':[' ',' ',' ']
		,'ter_len_0' : []
		,'getprompts' : ['configure']
		,'errorlist' : []
	},
	'1.3.6.1.4.1.3375': {
		'more':['y/n','---\(less \d+%\)---']
                ,'more_enters':['y',' ']
		,'specialprompts':['\(END\)']
	},
	'1.3.6.1.4.1.5651': {
		'enablecmd' : 'en'
		,'more':['---MORE---']
		,'more_enters':[' ']
		,'getprompts' : ['logout']
		,'logoutcmd' : ['logout']
	},
	'1.3.6.1.4.1.1872': {#Radware
                'more':['\[y/n\]']
                ,'more_enters':['n\n']
		,'ter_len_0' : ['/cfg']
		,'getprompts' : ['/cfg']
		,'successprompts':['#']
        },
	'default':{
		'logintimeout':10
		,'userprompts':['sername:','ogin:','ser:']
		,'enablecmd' : ''
		,'passwordprompts':['assword:']
		,'enableneedpass' : ['assword:','#:','(enable)']
		,'successprompts':['>']
		,'superprompts': ['#']
		,'more':['--More--']
		,'more_enters':[' ']
		,'ter_len_0' : ['ter len 0']
		,'getprompts' : ['config t']
		,'errorlist' : []
		,'waitcmds' : {}
		,'specialprompts':[]
		,'logoutcmd':['exit']
	}
}

def getModuleById(oid):
    longest_key = ''
    for key in deviceshell.keys():
        if oid.startswith(key):
            if len(key) > len(longest_key):
                longest_key = key
    if longest_key == '':
        return deviceshell['default']
    else:
        default_module = deviceshell['default']
        key_module = deviceshell[longest_key]
        if key_module.has_key('extend'):
        	return_module = getModuleById(key_module['extend'])
        else:
        	return_module = default_module
        for module in constants:
            if key_module.has_key(module):
                return_module[module]=key_module[module]
        return return_module

if __name__ == '__main__':
    print getModuleById('1.3.6.1.4.1.9')
