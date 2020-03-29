import pandas
from uszipcode import SearchEngine

search = SearchEngine(simple_zipcode=True)
covid = pandas.read_csv('covid.csv')

state_abbrev = {
    'AL': 'Alabama',
    'AK': 'Alaska',
    'AS': 'American Samoa',
    'AZ': 'Arizona',
    'AR': 'Arkansas',
    'CA': 'California',
    'CO': 'Colorado',
    'CT': 'Connecticut',
    'DE': 'Delaware',
    'DC': 'District of Columbia',
    'FL': 'Florida',
    'GA': 'Georgia',
    'GU': 'Guam',
    'HI': 'Hawaii',
    'ID': 'Idaho',
    'IL': 'Illinois',
    'IN': 'Indiana',
    'IA': 'Iowa',
    'KS': 'Kansas',
    'KY': 'Kentucky',
    'LA': 'Louisiana',
    'ME': 'Maine',
    'MD': 'Maryland',
    'MA': 'Massachusetts',
    'MI': 'Michigan',
    'MN': 'Minnesota',
    'MS': 'Mississippi',
    'MO': 'Missouri',
    'MT': 'Montana',
    'NE': 'Nebraska',
    'NV': 'Nevada',
    'NH': 'New Hampshire',
    'NJ': 'New Jersey',
    'NM': 'New Mexico',
    'NY': 'New York',
    'NC': 'North Carolina',
    'ND': 'North Dakota',
    'MP': 'Northern Mariana Islands',
    'OH': 'Ohio',
    'OK': 'Oklahoma',
    'OR': 'Oregon',
    'PA': 'Pennsylvania',
    'PR': 'Puerto Rico',
    'RI': 'Rhode Island',
    'SC': 'South Carolina',
    'SD': 'South Dakota',
    'TN': 'Tennessee',
    'TX': 'Texas',
    'UT': 'Utah',
    'VT': 'Vermont',
    'VI': 'Virgin Islands',
    'VA': 'Virginia',
    'WA': 'Washington',
    'WV': 'West Virginia',
    'WI': 'Wisconsin',
    'WY': 'Wyoming'
}

user_zip = input('\nPlease input zipcode: ')

casenum = {}
try:
    county_state = str(search.by_zipcode(user_zip).county).replace(' County', '') + \
        ', ' + state_abbrev[str(search.by_zipcode(user_zip).state)]

    print(county_state, '\n')

    for ind in covid.index:
        casenum[str(covid['Admin2'][ind]) + ', ' + str(covid['Province_State'][ind])] = {
            "cases": covid['Confirmed'][ind],
        }
    try:
        covid_num = casenum.get(county_state).get("cases")
        print('\n' + str(covid_num) + ' cases')
# Mild: 50-99, Moderate: 99-499, Urgent: 500-999, Very Urgent: 1000-2499, Extremely Urgent: 2500+
        if covid_num < 100:
            severity = 0
        elif covid_num < 499:
            severity = 1
        elif covid_num < 1000:
            severity = 2
        elif covid_num < 2500:
            severity = 3
        else:
            severity = 4

    except:
        print('\nUnfortunately, data on cases could not be found')

except:
    print('\nZipcode could not be obtained')
