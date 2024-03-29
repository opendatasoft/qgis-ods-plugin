# qgis-ods-plugin

This repo contains the plugin to import an Opendatasoft dataset to [QGIS](http://www.qgis.org/).
If you want to contact Opendatasoft, don't hesitate to send a mail to support@opendatasoft.com !

If you want to explore the kind of datasets Opendatasoft manages, have a look at the [Data network](https://data.opendatasoft.com) which aggregates all public catalogs hosted on our platform.

Have a look at our [API documentation](https://help.opendatasoft.com/apis/ods-explore-v2/#section/Opendatasoft-Query-Language-(ODSQL)) in order to make more complex queries or filters inside this plugin.


## Install

In order to install the plugin, search for the "Opendatasoft" plugin in the plugin manager, then install it. More information on [QGIS official documentation](https://docs.qgis.org/latest/en/docs/user_manual/plugins/plugins.html).


## Tutorial

Welcome and bienvenue to a little tutorial that will explain the most basic usages of the Opendatasoft plugin.
Once you have installed and loaded the plugin, you can click on the ODS icon in the plugin list.
Such a window should appear.

![Your first steps](/Opendatasoft/documentation/Photo1.png "Your first steps")


Here, you can choose the domain address on which the dataset you are looking for is stored.
I choose to look up a dataset from documentation-resources.opendatasoft.com, where some good examples are stored.

![Choose a domain](/Opendatasoft/documentation/Photo2.png "Choose a domain")


Since there are a lot of datasets, I want to refine the list by searching for datasets that concerns one subject I like a lot : trees ! So I search for trees (arbres, in French) before updating my list.
I finally choose to load the dataset id list.
I must then select a dataset : it's the dataset I'm going to download as a layer into QGIS.

![Trees in Paris you say ? It's possible, I swear !](/Opendatasoft/documentation/Photo3.png "Trees in Paris you say ? It's possible, I swear !")


Since I like old trees, I choose a dataset about noticeable trees in Paris.
As I choose this dataset, a lot of information appears about it, noticeably its fields.

![Nice table](/Opendatasoft/documentation/Photo4.png "Nice table")


The plugin offers the possibility to add filters to your query, if you want to download only certain parts of a dataset.
One tree type that is very common in Paris is plane trees (Platanus, for botanists among us). So I want to know where are the most impressive plane trees in Paris by adding a filter.

![Queries are made in ODSQL !](/Opendatasoft/documentation/Photo5.png "Queries are made in ODSQL !")


Finally, I have the query I want. I press "Import dataset", and after a bit of loading...

![Gotta go fast](/Opendatasoft/documentation/Photo6.png "Gotta go fast")


Voilà ! You can see a layer has been loaded, with the full filtered dataset in it. Each point on the map represents a plane tree located in Paris.

![IT'S ALIIIIVE](/Opendatasoft/documentation/Photo7.png "IT'S ALIIIIVE")


But it's hard to visualize where those trees are located in Paris.
That's why I make another import, from the same domain, of another dataset with the arrondissements of Paris.
No filters this time, I want Paris as a whole.

![Told you there are some interesting trees in Paris !](/Opendatasoft/documentation/Photo8.png "Told you there are some interesting trees in Paris !")


The other dataset is imported, another layer is created. And after ordering my layers a bit, you can clearly see where the noticeable plane trees of Paris are. Well done !

![Now it's your turn to have fun !](/Opendatasoft/documentation/Photo9.png "Now it's your turn to have fun !")


## Features

In this list, we will try to resume all features the plugin offers.
Each time an import is made, information about it will be stored in a cache, itself being stored in QGIS settings (field `ods-cache` from QGIS settings).

| | |
| -- | -- |
| **Domain address** | Field where to enter domain address. In the domain's catalog will be all the datasets of this domain. |
| **Include non-geo datasets** | Default dataset id list will return only datasets with a geometry. One can add the datasets with no geometry to the list by checking this box. |
| **(Optional) API key** | In order to reach a private dataset from a domain, one can enter an API key permitting access to the domain. |
| **Store API key in secure cache** | As an API key is an important matter, it is never stored in the unsecure QGIS cache. Yet, it can be stored securely if one checks this box. The API key will be stored in secure part of QGIS (Settings > Options > Authentication) by creating an ESRI-Token containing the API Key. It will only be accessible if one is logged in with his QGIS master password. |
| **(Optional) Text search in the domain's catalog** | This field allows you to search for a specific dataset to import. It will search for the input in the dataset name, tags and description. It is important to notice that the results of a search will be sorted by relevance. |
| **Update dataset list** | Updates the dataset list according to the domain name, the non-geo option, the API key and the text search. It must be clicked when changes have been made to those parameters; the dataset list does not update automatically. |
| **Dataset identifier** | The unique identifier of a dataset. You can scroll in the alphabetically sorted list to find a dataset (sorted by relevance if result of a text search), or type in the beginning of a dataset's name. |
| **Dataset name, number of records and publisher** | The name of the dataset, its number of records, and the name of the publisher of the dataset. |
| **Table** | Resumes the dataset, where each column is a field, and each row is the field Label, its name, its type and its first record respectively. |
| **Add filters to your query** | Check this box if you want to show the UI concerning ODSQL filters. If this box is unchecked, no filters will be taken into account. |
| **Clear filters** | Clear all the typed in filters. |
| **Always add geometry column if not selected** | If this box is checked when selecting specific columns using the *Select* entry, the column containing the geometry will be automatically added. If you don't want it to be added, feel free to uncheck the box. |
| **Select, Where, Order_by** | Allows filters following the ODSQL rules, similar to SQL rules. Refer to [ODSQL documentation](https://help.opendatasoft.com/apis/ods-explore-v2/#section/Opendatasoft-Query-Language-(ODSQL)) for more details. |
| **Limit** | Allows to choose the number of lines one will import. |
| **(Optional) Full path to dataset** | By default, the imported datasets are stored in the *temp* folder of the user. Here you can choose to instead download it in another folder. |
| **Cancel** | Will close the plugin. |
| **Import dataset** | Starts the import of the plugin. Needs at least a domain address and a dataset identifier |


## License
qgis-ods-plugin is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; version 3 of the License.

