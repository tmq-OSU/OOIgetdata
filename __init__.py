{
  "nbformat": 4,
  "nbformat_minor": 0,
  "metadata": {
    "colab": {
      "name": "__init__.py",
      "provenance": [],
      "authorship_tag": "ABX9TyMUc899vQ9FaadxCaDTXoIb",
      "include_colab_link": true
    },
    "kernelspec": {
      "name": "python3",
      "display_name": "Python 3"
    }
  },
  "cells": [
    {
      "cell_type": "markdown",
      "metadata": {
        "id": "view-in-github",
        "colab_type": "text"
      },
      "source": [
        "<a href=\"https://colab.research.google.com/github/OSU-Endyr/OOIgetdata/blob/master/__init__.py\" target=\"_parent\"><img src=\"https://colab.research.google.com/assets/colab-badge.svg\" alt=\"Open In Colab\"/></a>"
      ]
    },
    {
      "cell_type": "code",
      "metadata": {
        "id": "-gQuhju_jQTt",
        "colab_type": "code",
        "colab": {}
      },
      "source": [
        "import requests\n",
        "import re\n",
        "import xarray as xr\n",
        "import os"
      ],
      "execution_count": 0,
      "outputs": []
    },
    {
      "cell_type": "code",
      "metadata": {
        "id": "86SYLYPQhXeF",
        "colab_type": "code",
        "colab": {}
      },
      "source": [
        "def get_data(url,bad_inst=''):\n",
        "  '''Function to grab all data from specified directory'''\n",
        "  tds_url = 'https://opendap.oceanobservatories.org/thredds/dodsC'\n",
        "  datasets = requests.get(url).text\n",
        "  urls = re.findall(r'href=[\\'\"]?([^\\'\" >]+)', datasets)\n",
        "  x = re.findall(r'(ooi/.*?.nc)', datasets)\n",
        "  for i in x:\n",
        "    if i.endswith('.nc') == False:\n",
        "      x.remove(i)\n",
        "  for i in x:\n",
        "    try:\n",
        "      float(i[-4])\n",
        "    except:\n",
        "      x.remove(i)\n",
        "  datasets = [os.path.join(tds_url, i) for i in x]\n",
        "  \n",
        "  # Remove extraneous files if necessary\n",
        "  selected_datasets = []\n",
        "  for d in datasets:\n",
        "    if (bad_inst) and bad_inst in d:\n",
        "      pass\n",
        "    elif 'ENG000' in d: #Remove engineering streams for gliders\n",
        "      pass\n",
        "    else:\n",
        "      selected_datasets.append(d)\n",
        "#   print(selected_datasets)\n",
        "  \n",
        "  # Load in dataset\n",
        "  ds = xr.open_mfdataset(selected_datasets)\n",
        "  ds = ds.swap_dims({'obs': 'time'}) # Swap the primary dimension\n",
        "  # ds = ds.chunk({'time': 100}) # Used for optimization\n",
        "  ds = ds.sortby('time') # Data from different deployments can overlap so we want to sort all data by time stamp.\n",
        " \n",
        "  return ds\n",
        "\n"
      ],
      "execution_count": 0,
      "outputs": []
    }
  ]
}