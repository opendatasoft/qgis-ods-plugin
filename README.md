# qgis-ods-plugin

This repo contains the plugin to import an Opendatasoft dataset to QGIS.
If you want to contact Opendatasoft, don't hesitate to send a mail to support@opendatasoft.com !

If you want to explore the kind of dataset Opendatasoft proposes : https://data.opendatasoft.com.

Here is a bit of documentation on how to make more complex queries : https://help.opendatasoft.com/apis/ods-search-v2/#odsql.


## Install

For installing, just clone this repo in your QGIS profile directory:
- Linux `~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/qgis-ods-plugin`
- Windows `C:\Users\USER\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\qgis-ods-plugin`
- Mac OS: `/Users/USER/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/qgis-ods-plugin`

Then start QGIS and enable the plugin (menu Plugins > Manager and Install Plugins...)

TODO CHANGE INSTALLER

## Tutorial

Welcome and bienvenue to a little tutorial that will explain the most basic usages of the Opendatasoft plugin.
Once you have installed and loaded the plugin, you can click on the ODS icon in the plugin list.
Such a window should appear.


![Your first steps](/documentation/Photo1.png "Your first steps")

Here, you can choose the domain address on which the dataset you are looking for is stored.
I choose to look up a dataset from data.opendatasoft.com, which holds all the public dataset published on Opendatasoft portals.

![Choose a domain](/documentation/Photo2.png "Choose a domain")

Since there are a lot of datasets, I want to refine the list by searching for dataset that concerns my favorite region of France, Brittany ! (Bretagne in French ;) )
I finally choose to load the dataset id list.
I must then select a dataset : it's the dataset I'm going to donwload as a layer on QGIS.

![Visit Brittany, it's great !](/documentation/Photo3.png "Visit Brittany, it's great !")

Since I like cinema a bit, I chose a dataset about cinema festivals in Brittany.
As I choose this dataset, a lot of information appears about it, noticeably its fields.

![Nice table](/documentation/Photo4.png "Nice table")

The plugin offers the possibility to add filters to your query, if you want to downlaod only certain parts of a dataset.
As I also have a favorite French département in Brittany, Finistère, I choose to filter my query by selecting only the festivals located in Finistère.

![Queries are made in ODSQL !](/documentation/Photo5.png "Queries are made in ODSQL !")

Finally, I have the query I want. I press "Import dataset", and after a bit of loading...

![Gotta go fast](/documentation/Photo6.png "Gotta go fast")

Voilà ! You can see a layer has been loaded, with the full dataset in it. Each point on the map represent a festival located in Finistère.

![IT'S ALIIIIVE](/documentation/Photo7.png "IT'S ALIIIIVE")

But it's hard to visualize where festivals are located in Finistère.
That's why I make another import, from my personal domain, of a datset with French départements.
I add a filter for Finistère, of course !

![Did I ever tell you I like Finistère ?](/documentation/Photo2.png "Did I ever tell you I like Finistère ?")

The other dataset is imported, another layer is created. And now, you can clearly the festivals located on the map. Well done !

![Now it's your turn to have fun !](/documentation/Photo2.png "Now it's your turn to have fun !")