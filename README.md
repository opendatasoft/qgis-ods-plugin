# qgis-ods-plugin

This repo contains the plugin to import an Opendatasoft dataset to QGIS.
If you want to contact Opendatasoft, don't hesitate to send a mail to support@opendatasoft.com !

If you want to explore the kind of dataset Opendatasoft proposes : https://data.opendatasoft.com.

Here is a bit of documentation on how to make more complex queries : https://help.opendatasoft.com/apis/ods-search-v2/#odsql.


## Install

In order to install the plugin, search for the "Opendatsoft" plugin in the plugin manager, then install it.

## Tutorial

Welcome and bienvenue to a little tutorial that will explain the most basic usages of the Opendatasoft plugin.
Once you have installed and loaded the plugin, you can click on the ODS icon in the plugin list.
Such a window should appear.

![Your first steps](/documentation/Photo1.png "Your first steps")

Here, you can choose the domain address on which the dataset you are looking for is stored.
I choose to look up a dataset from documentation-resources.opendatasoft.com, where some good examples are stored.

![Choose a domain](/documentation/Photo2.png "Choose a domain")

Since there are a lot of datasets, I want to refine the list by searching for dataset that concerns one subject I like a lot : trees ! So I search for trees (arbres, in French) before updating my list.
I finally choose to load the dataset id list.
I must then select a dataset : it's the dataset I'm going to donwload as a layer on QGIS.

![Trees in Paris you say ? It's possible, I swear !](/documentation/Photo3.png "Trees in Paris you say ? It's possible, I swear !")

Since I like old trees, I chose a dataset about noticable trees in Paris.
As I choose this dataset, a lot of information appears about it, noticeably its fields.

![Nice table](/documentation/Photo4.png "Nice table")

The plugin offers the possibility to add filters to your query, if you want to download only certain parts of a dataset.
One tree that is very common in Paris are plane trees (Platanus, for botanists among us). So I want to know where are the most impressive plane trees in Paris by adding a filter.

![Queries are made in ODSQL !](/documentation/Photo5.png "Queries are made in ODSQL !")

Finally, I have the query I want. I press "Import dataset", and after a bit of loading...

![Gotta go fast](/documentation/Photo6.png "Gotta go fast")

Voilà ! You can see a layer has been loaded, with the full filtered dataset in it. Each point on the map represent a plane tree located in Paris.

![IT'S ALIIIIVE](/documentation/Photo7.png "IT'S ALIIIIVE")

But it's hard to visualize where those trees are located in Paris.
That's why I make another import, from the same domain, of another dataset with the arrondissements of Paris.
No filters this time, I want Paris as a whole.

![Told you there are some interesting trees in Paris !](/documentation/Photo2.png "Told you there are some interesting trees in Paris !")

The other dataset is imported, another layer is created. And after ordering my layers a bit, you can clearly see where the noticable plane trees of Paris are. Well done !

![Now it's your turn to have fun !](/documentation/Photo2.png "Now it's your turn to have fun !")