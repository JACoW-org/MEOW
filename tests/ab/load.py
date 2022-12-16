
import json
from odf.opendocument import load
from itertools import groupby
from operator import itemgetter


async def async_load():

    contribution_primary_authors_list = [
        {'id': '17655', 'first': 'Matteo', 'last': 'Pancaldi',
            'affiliation': 'Elettra-Sincrotrone Trieste S.C.p.A.', 'email': 'matteo.pancaldi@elettra.eu'},
        {'id': '17652', 'first': 'Arun', 'last': 'Ravindran',
            'affiliation': 'University of Nova Gorica', 'email': 'arun.ravindran@ung.si'},
        {'id': '17645', 'first': 'Charles S.', 'last': 'Bevis',
            'affiliation': 'University of Pavia', 'email': 'charles.bevis@unipv.it'},
        {'id': '17654', 'first': 'Dario', 'last': 'De Angelis',
            'affiliation': 'Elettra-Sincrotrone Trieste S.C.p.A.', 'email': 'dario.deangelis@elettra.eu'},
        {'id': '17648', 'first': 'Emanuele', 'last': 'Pedersoli',
            'affiliation': 'Elettra-Sincrotrone Trieste S.C.p.A.', 'email': 'emanuele.pedersoli@elettra.eu'},
        {'id': '17644', 'first': 'Flavio', 'last': 'Capotondi',
            'affiliation': 'Elettra-Sincrotrone Trieste S.C.p.A.', 'email': 'flavio.capotondi@elettra.eu'},
        {'id': '17646', 'first': 'Francesco', 'last': 'Guzzi',
            'affiliation': 'Elettra-Sincrotrone Trieste S.C.p.A.', 'email': 'francesco.guzzi@elettra.eu'},
        {'id': '17649', 'first': 'Georgios', 'last': 'Kourousias',
            'affiliation': 'Elettra-Sincrotrone Trieste S.C.p.A.', 'email': 'george.kourousias@elettra.eu'},
        {'id': '17659', 'first': 'Giovanni', 'last': 'De Ninno',
            'affiliation': 'Elettra-Sincrotrone Trieste S.C.p.A.', 'email': 'giovanni.deninno@elettra.eu'},
        {'id': '17643', 'first': 'Giulia F.', 'last': 'Mancini',
            'affiliation': 'University of Pavia', 'email': 'giuliafulvia.mancini@unipv.it'},
        {'id': '17650', 'first': 'Iuliia', 'last': 'Bykova',
            'affiliation': 'Paul Scherrer Institut', 'email': 'iuliia.bykova@psi.ch'},
        {'id': '17657', 'first': 'Maurizio', 'last': 'Sacchi',
            'affiliation': 'Synchrotron SOLEIL', 'email': 'maurizio.sacchi@synchrotron-soleil.fr'},
        {'id': '17658', 'first': 'Mauro', 'last': 'Fanciulli',
            'affiliation': 'Lab. de Physique des Materiaux et Surfaces, CY Cergy Paris Université', 'email': 'mauro.fanciulli@u-cergy.fr'},
        {'id': '17651', 'first': 'Michele', 'last': 'Manfredda',
            'affiliation': 'Elettra-Sincrotrone Trieste S.C.p.A.', 'email': 'michele.manfredda@elettra.eu'},
        {'id': '17660', 'first': 'Paolo', 'last': 'Vavassori',
            'affiliation': 'CIC nanoGUNE BRTA', 'email': 'p.vavassori@nanogune.eu'},
        {'id': '17656', 'first': 'Stefano', 'last': 'Bonetti',
            'affiliation': "Stockholm University and Ca' Foscari University of Venice", 'email': 'stefano.bonetti@unive.it'},
        {'id': '17653', 'first': 'Thierry', 'last': 'Ruchon',
            'affiliation': 'Université Paris-Saclay, CEA, CNRS, LIDYL', 'email': 'thierry.ruchon@cea.fr'},
        {'id': '17647', 'first': 'Benedikt', 'last': 'Roesner',
            'affiliation': 'Paul Scherrer Institut', 'email': 'benedikt.roesner@psi.ch'},
    ]

    print(json.dumps(contribution_primary_authors_list, indent=2, sort_keys=True))
    print()
    
   
    contribution_primary_authors_dict: dict[str, list] = {}
       
    for item in contribution_primary_authors_list:
        key = item.get('affiliation', '')
        
        if not key in contribution_primary_authors_dict:
            contribution_primary_authors_dict[key] = []
        
        contribution_primary_authors_dict[key].append(item)
               
    contribution_primary_authors_groups: list[dict] = []
    
    main = False
    
    for (key, items) in contribution_primary_authors_dict.items():
        
        sorted_items = items
    
        if main is False:
            first = items.pop(0)
            sorted_items = sorted(items, key = itemgetter('first', 'last'))
            sorted_items = [first] + items
            main= True
        else:
            sorted_items = sorted(items, key = itemgetter('first', 'last'))        
        
        contribution_primary_authors_groups.append({'key': key, 'items': sorted_items})
    
    print(json.dumps(contribution_primary_authors_groups, indent=2, sort_keys=True))
    print()

    contribution_primary_authors_values = [
        (
            f"{item.get('first', '')} {item.get('last')} ({item.get('affiliation')})"
            if index == len(g.get('items', []))-1 else f"{item.get('first')} {item.get('last')}"
        )
        for g in contribution_primary_authors_groups
        for index, item in enumerate(g.get('items', []))
    ]

    print(json.dumps(contribution_primary_authors_values, indent=2, sort_keys=True))
    print()

    contribution_primary_authors_value = ', '.join(
        contribution_primary_authors_values)

    print(json.dumps(contribution_primary_authors_value, indent=2, sort_keys=True))
