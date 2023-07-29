## Welcome Tana user!

If you are here you are possibly an user of Tana. Tana has a lot of features currently supported and its evolving faster. I already build another products around Tana, but this one is probably more useful because let's us extract information from the Tana json data.

## The problem

In Tana its extremely useful to create different objects using nodes. For example, you can customize a tag to be used as a simple application that makes something with AI or make an API request. You can have different commands to work with. Also you can use the tags to add a node as a piece of knowledge to work schema. A tag can be used to store pieces of structured information.

But the problem comes when we want to use that data away from Tana. You will see a very long json where each node is treated separately. A node has different properties as: id, props, children, created (in a human non-readable format). And in this properties we have information about each node, but we don't have information from the tag that the node uses. That why extracting informartion can be difficult, because we need to walk though the json searching something, but we just find singles nodes.

## The solution

I notice the structure of the json, basically, it is like a very big graph of nodes that are built using the Depth First Search (**DFS**) algorithm. So, we can use the information of the node to explore the graph. For example, I can walk from a parent node to their children nodes. And this is when we get a solution. We can have a similar child in each node, and we can use that child to extract information from the parent, so we can be sure that we extract information from the correct parent.

With this document, you will learn how to work with this script to extract useful information from the Tana JSON.

## 1. Create a field: The **extraction_slug**

The secret of this functionality is to have a field in the nodes we want to extract information, this needs to be a field that is related  to the tag, and this field must be unique for the kind of data we want to extract. 

For example, if I want to extract information from the movies i watched, maybe I want to know the review I leave and stuff like that present in the node, I can add a field to the tag movies, a field called, for example: **extraction_slug**, or any name that can help you undestand the extracting purpose of the field.

## 2. Fill the information in the field: How to add an **extraction_slug**

This is simple, what think can be unique for each tag and can be used to extract information? Well, its just the tag name followed by another unique set of characters. In my case, I add the tag name followed by **_extractor**.

For example:
```%%Tana%%
Barbie #movie
- extraction_slug::movie_extractor
```

## 3. That all, now extract information.


