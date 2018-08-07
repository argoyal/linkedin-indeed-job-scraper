import os


CREDENTIALS_PATH = os.path.join(os.getcwd(), '.credentials.json')


config = {
    # website to scrape, only linkedin & indeed are supported now
    'website': 'linkedin',
    # path where program located
    'homePath': os.path.dirname(os.getcwd()),
    # specify username & password
    # or specify an authkey file
    "username":  "",
    "password":  "",
    "authkey":  CREDENTIALS_PATH,
    "keywords":  [
        # "Financial operations Specialist", "Financial accounting manager", "Financial planning and analysis",
        "Financial reporting analysis", "Treasury Ops manager", "Taxation manager", "Omni channel customer care specialist", "Collection specialist", "Customer engagement specialist", "Capabilities engineering and re engineering", "Corporate engagement specialist", "Digital acquisition specialist/manager", "Product manager", "Digital marketing specialist/manager", "Account/account development manager", "Sales manager", "Marketing manager", "Credit and fraud risk analytics", "Performance analytics", "Data analytics and business insights", "Operations risk management", "Data analytics and reporting", "Business enablement analytics"],
    "locations":  ["India"],

    # specify date range:
    # for linkedin: 'Past 24 hours', 'Past Week', 'Past Month', 'Any Time'
    # for indeed: 'any', '15', '7', '3', '1', 'last'
    "date_range":  {'linkedin': "All", 'indeed': "15"},

    # sort by either 'relevance' or 'post date'
    "sort_by":  "relevance",

    "database_config": {
        "DB_HOST": "localhost",
        "DB_PORT": 27017,
        "DB_NAME": "linkedin",
        "DB_USERNAME": "",
        "DB_PASSWORD": "",
    }
}
