import requests
import re
import xarray as xr
import os
import time
# what was in get_data , bad_inst=''
def get_data(url):
  '''Function to grab all data from specified directory'''
  tds_url = 'https://opendap-west.oceanobservatories.org/thredds/dodsC'
  datasets = requests.get(url).text
  urls = re.findall(r'href=[\'"]?([^\'" >]+)', datasets)
  x = re.findall(r'(ooi/.*?.nc)', datasets)
  for i in x:
    if i.endswith('.nc') == False:
      x.remove(i)
  for i in x:
    try:
      float(i[-4])
    except:
      x.remove(i)
  datasets = [os.path.join(tds_url, i) for i in x]
  
  # Remove extraneous files if necessary
  #selected_datasets = []
  #for d in datasets:
    #if (bad_inst) and bad_inst in d:
     # pass
   # elif 'ENG000' in d: #Remove engineering streams for gliders
 #     pass
#    else:
#      selected_datasets.append(d)
#   print(selected_datasets)
  
  # Load in dataset
  ds = xr.open_mfdataset(selected_datasets)
  ds = ds.swap_dims({'obs': 'time'}) # Swap the primary dimension
  # ds = ds.chunk({'time': 100}) # Used for optimization
  ds = ds.sortby('time') # Data from different deployments can overlap so we want to sort all data by time stamp.
 
  return ds

def make_url(site,node,instrument,method,stream,API_USERNAME,API_TOKEN):
    """Function for generating meta and data request urls"""

    SENSOR_BASE_URL = 'https://ooinet.oceanobservatories.org/api/m2m/12576/sensor/inv/'
    VOCAB_BASE_URL = 'https://ooinet.oceanobservatories.org/api/m2m/12586/vocab/inv'
    meta_request_url ='/'.join((VOCAB_BASE_URL,site,node,instrument)) # Python wizard best
    data_request_url ='/'.join((SENSOR_BASE_URL,site,node,instrument,method,stream))

    # Retrieve vocabulary information for a given instrument
    r = requests.get(meta_request_url, auth=(API_USERNAME, API_TOKEN))
    meta_data = r.json()

    return (data_request_url,meta_data)

def make_data_request(data_request_url,params,API_USERNAME,API_TOKEN,check_status=True):
    """Function for making data request"""

    # Makes data request to OOI server
    r = requests.get(data_request_url, params=params, auth=(API_USERNAME, API_TOKEN))
    data = r.json()

    try:
        check_complete = data['allURLs'][1] + '/status.json'
    except KeyError:
        raise Exception('No data found in specified date range')

    # Checks each second to see if complete
    if check_status==True:
        for i in range(1000):
            r = requests.get(check_complete)
            if r.status_code == requests.codes.ok:
                print('request completed')
                break
            else:
                time.sleep(1)

    # Grab urls
    url_thredds = data['allURLs'][0]
    url_netcdf = data['allURLs'][1]

    return (url_thredds, url_netcdf, data)

def list_thredds_datasets(catalog_url,pattern_str='',append_str='',tds_url=None):
    """Return a list of NetCDF datasets from an OOI THREDDS catalog.
    catalog_url - string containing full url for the catalog, ending with /catalog.html
    pattern_str - string containing a pattern that must be in the dataset name (default '')
    append_str - string that will be appended to the end of each filename (default '')
    tds_url - the base OpenDAP url for the datasets
              (default: https://opendap-west.oceanobservatories.org/thredds/dodsC)
    """

    # set default tds_url if none provided
    if tds_url is None:
        tds_url = 'https://opendap-west.oceanobservatories.org/thredds/dodsC'

    # parse datasets in catalog
    datasets = requests.get(catalog_url).text
    urls = re.findall(r'href=[\'"]?([^\'" >]+)', datasets)
    x = re.findall(r'(ooi/.*?'+pattern_str+'.*?.nc)', datasets)
    for i in x:
        if i.endswith('.nc') == False:
            x.remove(i)
    for i in x:
        try:
            float(i[-4])
        except:
            x.remove(i)

    # create list of datasets
    dataset_list = [os.path.join(tds_url, i)+append_str for i in x]
    return dataset_list
