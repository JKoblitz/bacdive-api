'''
Using the BacDive API requires registration. Registrations is free but the 
usage of BacDive data is only permitted when in compliance with the BacDive 
terms of use. See https://bacdive.dsmz.de/about for details.

Please register at https://api.bacdive.dsmz.de/login.
'''

from keycloak.exceptions import KeycloakAuthenticationError
from keycloak import KeycloakOpenID
import requests
import json


class BacdiveClient():
    def __init__(self, user, password, public=True):
        ''' Initialize client and authenticate on the server '''
        self.result = {}
        self.public = public
        
        self.predictions = False

        client_id = "api.bacdive.public"
        if self.public:
            server_url = "https://sso.dsmz.de/auth/"
        else:
            server_url = "https://sso.dmz.dsmz.de/auth/"
        try:
            self.keycloak_openid = KeycloakOpenID(
                server_url=server_url,
                client_id=client_id,
                realm_name="dsmz")

            # Get tokens
            token = self.keycloak_openid.token(user, password)
            self.access_token = token['access_token']
            self.refresh_token = token['refresh_token']
            print("-- Authentication successful --")
        except KeycloakAuthenticationError as e:
            print("ERROR - Authentication failed:", e)

    def includePredictions(self):
        self.predictions = True

    def excludePredictions(self):
        self.predictions = False

    def do_api_call(self, url):
        ''' Initialize API call on given URL and returns result as json '''
        if self.public:
            baseurl = "https://api.bacdive.dsmz.de/"
        else:
            baseurl = "http://api.bacdive-dev.dsmz.local/"
        
        if not url.startswith("http"):
            # if base is missing add default:
            url = baseurl + url
        resp = self.do_request(url)

        if resp.status_code == 500 or resp.status_code == 400:
            return json.loads(resp.content)
        elif (resp.status_code == 401):
            msg = json.loads(resp.content)

            if msg['message'] == "Expired token":
                # Access token might have expired (15 minutes life time).
                # Get new tokens using refresh token and try again.
                token = self.keycloak_openid.refresh_token(self.refresh_token)
                self.access_token = token['access_token']
                self.refresh_token = token['refresh_token']
                return self.do_api_call(url)

            return msg
        else:
            return json.loads(resp.content)

    def do_request(self, url):
        ''' Perform request with authentication '''
        headers = {
            "Accept": "application/json",
            "Authorization": "Bearer {token}".format(token=self.access_token)
        }

        if self.predictions:
            if "?" in url:
                url += "&predictions=1"
            else:
                url += "?predictions=1"
        resp = requests.get(url, headers=headers)
        return resp


    def filterResult(self, d, keys):
        ''' Helper function to filter nested dict by keys '''
        if not isinstance(d, dict):
            yield None
        for k, v in d.items():
            if k in keys:
                yield {k: v}
            if isinstance(v, dict):
                yield from self.filterResult(v, keys)
            elif isinstance(v, list):
                for i in v:
                    if isinstance(i, dict):
                        yield from self.filterResult(i, keys)

    def retrieve(self, filter=None):
        ''' Yields all the received entries and does next call if result is incomplete '''
        ids = ";".join([str(i) for i in self.result['results']])
        entries = self.do_api_call('fetch/'+ids)['results']
        for el in entries:
            if isinstance(el, dict):
                entry = el
                el = entry.get("id")
            else:
                entry = entries[el]
            if filter:
                entry = {el: [i for i in self.filterResult(entry, filter)]}
            yield entry
        if self.result['next']:
            self.result = self.do_api_call(self.result['next'])
            yield from self.retrieve(filter)

    def getIDByCultureno(self, culturecolnumber):
        ''' Initialize search by culture collection number '''
        item = culturecolnumber.strip()
        result = self.do_api_call('culturecollectionno/'+str(item))
        return result

    def getIDsByTaxonomy(self, genus, species_epithet=None, subspecies_epithet=None):
        ''' Initialize search by taxonomic names '''
        item = genus.strip()
        if species_epithet:
            item += "/" + species_epithet
            if subspecies_epithet:
                item += "/" + subspecies_epithet
        result = self.do_api_call("taxon/"+item)
        return result

    def getIDsBy16S(self, seq_acc_num):
        ''' Initialize search by 16S sequence accession '''
        item = seq_acc_num.strip()
        result = self.do_api_call('sequence_16s/'+str(item))
        return result

    def getIDsByGenome(self, seq_acc_num):
        ''' Initialize search by genome sequence accession '''
        item = seq_acc_num.strip()
        result = self.do_api_call('sequence_genome/'+str(item))
        return result

    def search(self, **params):
        ''' Initialize search with *one* of the following parameters:
        
        id -- BacDive-IDs either as a semicolon seperated string or list
        taxonomy -- Taxonomic names either as string or list
        sequence -- Sequence accession number of unknown type
        genome -- Genome sequence accession number
        16s -- 16S sequence accession number
        culturecolno -- Culture collection number (mind the space!)
        '''
        params = list(params.items())
        allowed = ['id', 'taxonomy', 'sequence',
                   'genome', '16s', 'culturecolno']
        if len(params) != 1:
            print(
                "ERROR: Exacly one parameter is required. Please choose one of the following:")
            print(", ".join(allowed))
            return 0
        querytype, query = params[0]
        querytype = querytype.lower()
        if querytype not in allowed:
            print(
                "ERROR: The given query type is not allowed. Please choose one of the following:")
            print(", ".join(allowed))
            return 0
        if querytype == 'id':
            if type(query) == type(1):
                query = str(query)
            if type(query) == type(""):
                query = query.split(';')
            self.result = {'count': len(query), 'next': None,
                           'previous': None, 'results': query}
        elif querytype == 'taxonomy':
            if type(query) == type(""):
                query = [i for i in query.split(" ") if i != "subsp."]
            if len(query) > 3:
                print("Your query contains more than three taxonomical units.")
                print(
                    "This query supports only genus, species epithet (optional), and subspecies (optional).")
                print("They can be defined as list, tuple or string (space separated).")
                return 0
            self.result = self.getIDsByTaxonomy(*query)
        elif querytype == 'sequence':
            self.result = self.getIDsByGenome(query)
            if self.result['count'] == 0:
                self.result = self.getIDsBy16S(query)
        elif querytype == 'genome':
            self.result = self.getIDsByGenome(query)
        elif querytype == '16s':
            self.result = self.getIDsBy16S(query)
        elif querytype == 'culturecolno':
            self.result = self.getIDByCultureno(query)

        if not self.result:
            print("ERROR: Something went wrong. Please check your query and try again")
            return 0
        if not 'count' in self.result:
            print("ERROR:", self.result.get("title"))
            print(self.result.get("message"))
            return 0
        if self.result['count'] == 0:
            print("Your search did not receive any results.")
            return 0
        return self.result['count']




if __name__ == "__main__":
    client = BacdiveClient('mail.address@server.example', 'password')

    # the prepare method fetches all BacDive-IDs matching your query
    # and returns the number of IDs found
    count = client.search(taxonomy='Bacillus subtilis subtilis')
    print(count, 'entries found.')

    # The retrieve method lets you iterate over all entries
    # and returns the full entry as dict
    # Entries can be further filtered using a list of keys (e.g. ['keywords'])
    for entry in client.retrieve():
        print(entry)
