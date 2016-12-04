import getopt
import sys
import OptionConfiguration


def prepareData(AllvalueData):
    """Prepara i dati per essere inviati"""
    for data in AllvalueData:
        try:
            temp = data.split("=")
            # splitto i valori composti da chiave = valore
            # e li metto in un dizionario
            OptionConfiguration.key.append(temp[0])
            OptionConfiguration.data[temp[0]] = temp[1]

        except:
            print(OptionConfiguration.bcolors.FAIL+" Errore" +OptionConfiguration.bcolors.ENDC)
            help()

def help():
    print ("")
    print "Usage: python TimeBlindSQLi_capu.py [options] <target url>"
    print """Options:

    Tool Time-Based blind SQLi
    DB MySQL only
    Options and fields to use it:


    -d :        search name of all DB

    --dbs    =  nameDB
                example:
                --dbs=DBpage

    -t :        search name of all Tables in Db
                required name of db


    --table =   nameTable
                example:
                --table=user

    -c :        search all the names of the columns in the Table
                required name of table

    --columns =  column name
                example:

                --column=password

    -a :        search all the values of the column
                in the selected column


    --method =  POST o GET
                example:
                --method = POST
                deafult -> POST

    --data   =  field and value injectable
                example:
                --data="email=ppino@gmail.com"
                --data="email=ppino@gmail.com&login=cioa"


    --fielInjectable = name of fiel injectable se conosciuto
                        example:
                        --fielInjectable=email
    --thread=YES o NO


    Example:

        //serch name of all db
        python TimeBlindSQLi_capu.py -d  --method=POST --data="email=ppino@gmail.com" http://192.168.33.10/sqli/time_based_blind.php


        //search all table name of information_schema db
        python TimeBlindSQLi_capu.py --dbs=information_schema -t --method=POST --data="email=ppino@gmail.com" http://192.168.33.10/sqli/time_based_blind.php


        //search all column name of user table
        python TimeBlindSQLi_capu.py --dbs=information_schema --table=user -c --method=POST --data="email=ppino@gmail.com" http://192.168.33.10/sqli/time_based_blind.php

        """

def parseOptions(args):

    attacco=False
    try:

        options,destination=getopt.getopt(args,"htcda",['method=','data=','columns=','table=','dbs=','fieldInjectable=','thread='],)
        if(destination):
            OptionConfiguration.destination=destination;
        else:
            print(OptionConfiguration.bcolors.FAIL+"[ERRORE] Insert a target"+OptionConfiguration.bcolors.ENDC)
            help()


        for opt in options:
            if(opt[0]=="-h"):
                help()

            elif (opt[0] == "-d"):
                # search name of all db
                if(attacco==False):
                    OptionConfiguration.typeOfAttack = "d"
                    attacco=True
            elif(opt[0] == "-t"):
                #search name of all tables from db select
                if(attacco==False):
                    OptionConfiguration.typeOfAttack = "t"
                    attacco=True

            elif(opt[0] == "-c"):
                #search all column name of table select
                if(attacco==False):
                    OptionConfiguration.typeOfAttack = "c"
                    attacco=True

            elif(opt[0] == "-a"):
                #searcg all value from colum name select
                if(attacco==False):

                    OptionConfiguration.typeOfAttack="a"
                    attacco=True

            elif (opt[0] == "--method"):
                OptionConfiguration.methodSentData=opt[1]


            elif (opt[0] == "--data"):
                #tutti i valori in una lista
                AllvalueData = str(opt[1]).split("&")
                prepareData(AllvalueData)

            elif (opt[0] == "--columns"):
                OptionConfiguration.nameColumn=opt[1]

            elif (opt[0] == "--table"):
                OptionConfiguration.nameTable=opt[1]


            elif (opt[0] == "--dbs"):
                OptionConfiguration.nameDb=opt[1]
            elif(opt[0]=="--thread"):
                if(opt[1]=="YES"):
                    OptionConfiguration.thread="YES"
                elif(opt[1]=="NO"):
                    OptionConfiguration.thread="NO"
                else:
                    print (help())
                    import sys
                    sys.exit(0)


            else:
                help()

    except:
        print(OptionConfiguration.bcolors.FAIL+OptionConfiguration.bcolors.BOLD+"Error options :"+OptionConfiguration.bcolors.ENDC)
        help()
        import sys
        sys.exit(0)