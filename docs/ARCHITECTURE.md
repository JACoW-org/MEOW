# Architecture


## JPSP-NG

### JPSP-API-TASK

Applicazione di calcolo: espone task via api websocket (o rest)

- verrà creata un web-app con un sistema per l'esecuzione asincrona di task di calcolo
- verrà esposta un'api di calcolo mediante canale web-socket
- i task verranno invocati e saranno: accodati, avviati, terminati o falliti
- al termine del task verranno forniti i risultati
- nel caso di risultati di tipo file potranno essere forniti in stream o posizionati in
  un'area di memoria temporanea per poter essere successivamente scaricati (con una scadenza)
- non verranno memorizzate informazioni locali a meno di dati temporanei utili al calcolo
- i task saranno sviluppati in async-python e non saranno bloccanti
- i task saranno eseguiti su thread separati (o processi) usando un pool per limitare la concorrenza
- i task saranno accodati e successivamente eseguiti non appena un worker sarà disponibile
- i task non saranno tracciati in modo persistente
- i task saranno invocabili con un semplice sistema di sicurezza basata su api-key
- l'api-key abilita o meno l'esecuzione di tutti i task senza gestione permessi
- i task riceveranno in input le tutte le informazioni necessarie al calcolo

  - es. per ab-task riceverà in input il json dell'evento e produrrà in output l'odt
        non ha senso che venga invocato il task ab con il solo parametro event_id 
        e che poi il task recuperi il json dell'evento accedendo ad indico
  - es. per task futuri che manipolano ed accedono a contenuti binary (es. file pdf)
        sarà necessario fornire in input al task anche le informazioni necessari per il 
        recupero di tali contenuti (es. url della risorsa, header http con token di auth, ...)    


### JPSP-PLUGIN-CONF

Plugin di indico per la conf del servizio di calcolo

 - verrà creato un plugin indico di configurazione per il servizio jpsp-ng
 - tale plugin verrà collegato all'evento
 - in fase di collegamento verranno definiti parametri come l'url di jpsp-ng ed il token di auth
 - ogni evento avrà la propria configurazione


## JPSP-PLUGIN-AB

Plugin di indico per l'estensione della web-ui di indico (parte amministrativa) 
per aggiungere il bottone che scatenerà la creazione dell'abstract_booklet

 - verrà creato un plugin indico per l'integrazione con jpsp-api-task nello use case abstract_booklet
 - tale plugin estenderà la web interface di indico aggiungendo un'area per la generazione dell'ab
 - verrà creato un widget che conterrà del testo ed un bottone 
 - premuto il bottone verrà:
   - recuperata la conf di jpsp-api-task per l'evento corrente
   - recuperate le informazioni dell'evento corrente con sessioni incluse
   - invocato il task in jpsp-api-task per la generazione dell'ab (bottone che si disabilita)
   - verificato lo stato di avanzamento dell'operazione (rotellina sul bottone)
   - al termine dell'operazione verrà scatenato il download del file odf (riabilitato il bottone)

