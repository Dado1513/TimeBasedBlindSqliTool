
#Setting 

# nome db da interrogare
nameDb=""
# nome tabella da interrogare
nameTable=""
# nome colonna da interrogare
nameColumn=""
# metodo di incvio dei dati
methodSentData=""
#chiavi e valori
data={}
#chiavi
key=[]

destination=""
dbms="MySQL"

#tipo di attacco
typeOfAttack=""
# valori iniettavile
valueInjectable=""
# tipo del valore iniettabile
typeOfValue=""
# tempo standard time wait
timeToWait=5

thread="NO"

tempoMedioConnessione=0


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
