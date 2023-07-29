from typing import List, Dict, Any, Optional,Tuple
import json
import csv
from pathlib import Path
import datetime


def search_file(directory: str, filename: str) -> Optional[str]:
    """
    Search for a specific file within a directory and its subdirectories.

    Args:
        directory: The directory to search in.
        filename: The name of the file to search for.

    Returns:
        The full path of the file if found, otherwise None.
    """
    for file in Path(directory).rglob(filename):
        return str(file)
    return None

def search_nodes_with_extractors(path: str, extractors: List[str]) -> None:
    """
    Search for specific nodes in a JSON file.

    Args:
        path: The path to the JSON file.
        extractors: A list of extractors to search for.
    """
    # Load the JSON data
    data = load_json_file(path)

    # If data loading fails or 'docs' key doesn't exist
    if not data or "docs" not in data:
        return

    found_tuples = find_tuples(data, extractors)
    parent_nodes = map_parent_nodes(data, found_tuples)
    found_nodes = find_nodes(data, parent_nodes, found_tuples)

    return found_nodes, data["docs"]

def load_json_file(path: str) -> Optional[Dict[str, Any]]:
    """
    Load JSON data from a file.

    Args:
        path: The path to the JSON file.

    Returns:
        A dictionary containing the JSON data if successful, otherwise None.
    """
    if not Path(path).is_file():
        print(f"File {path} not found.")
        return None

    with open(path, 'r', encoding='utf-8') as f:  # Specify the 'utf-8' encoding here
        return json.load(f)
    


def find_tuples(data: Dict[str, Any], extractors: List[str], extraction_sequence: str = '_extractor') -> Dict[str, str]:
    """
    Find tuples in the data that match the specified extractors.

    Args:
        data: The JSON data.
        extractors: A list of extractors to search for.

    Returns:
        A dictionary mapping tuple IDs to their corresponding extractor names.
    """
    if len(extractors) == 0:
        return {node["props"]["_ownerId"]: node["props"]["name"] 
                for node in data['docs'] 
                if "name" in node["props"] and extraction_sequence in node["props"]["name"]}

    else:
        return {node["props"]["_ownerId"]: node["props"]["name"] 
                for node in data['docs'] 
                if "name" in node["props"] and node["props"]["name"] in extractors}

def map_parent_nodes(data: Dict[str, Any], found_tuples: Dict[str, str]) -> Dict[str, str]:
    """
    Map parent nodes to the corresponding tuple IDs.

    Args:
        data: The JSON data.
        found_tuples: A dictionary mapping tuple IDs to extractor names.

    Returns:
        A dictionary mapping parent node IDs to tuple IDs.
    """
    return {node["props"]["_ownerId"]: node["id"] 
            for node in data['docs'] 
            if node["id"] in found_tuples}

def find_nodes(data: Dict[str, Any], parent_nodes: Dict[str, str], found_tuples: Dict[str, str]) -> List[Tuple[str, Any, str]]:
    """
    Find nodes that match the parent node IDs.

    Args:
        data: The JSON data.
        parent_nodes: A dictionary mapping parent node IDs to tuple IDs.
        found_tuples: A dictionary mapping tuple IDs to extractor names.

    Returns:
        A list of tuples where each tuple contains the node name, its data, and the corresponding extractor name.
    """
    return [(node["props"]["name"], node, found_tuples[parent_nodes[node["id"]]])
            for node in data['docs']
            if "props" in node and "name" in node["props"] and node["id"] in parent_nodes.keys()]

def find_children_objects(parent_objects, docs):
    children_objects = {}

    # Convert the docs into a dictionary for faster lookup
    docs_dict = {doc['id']: doc for doc in docs}

    for parent in parent_objects:
        if 'children' in parent:
            children_objects[parent['id']] = [docs_dict[child_id] for child_id in parent['children'] if child_id in docs_dict]
    
    return children_objects

def find_tuple_fields(docs, child_objects):
    fields = {}

    # Convert the docs into a dictionary for faster lookup
    docs_dict = {doc['id']: doc for doc in docs}

    for parent_id, children in child_objects.items():
        temp_list = []
        for child in children:
            if '_docType' in child['props'] and child['props']['_docType'] == 'tuple':
                if 'children' in child:
                    for grandchild_id in child['children']:
                        grandchild_props = docs_dict.get(grandchild_id, {}).get('props', {})
                        name = grandchild_props.get('name')
                        if name is not None:
                            temp_list.append(name)

        # Convert list to list of key-value pair dictionaries
        if len(temp_list) % 2 == 1:  # If the list length is odd, discard the last element
            temp_list = temp_list[:-1]

        fields[parent_id] = [{temp_list[i]: temp_list[i + 1]} for i in range(0, len(temp_list), 2)] if temp_list else []

    return fields

def find_children_nodes_for_parent(docs, child_objects):
    children_for_nodes = {}

    # Convert the docs into a dictionary for faster lookup
    docs_dict = {doc['id']: doc for doc in docs}

    for parent_id, children in child_objects.items():
        temp_list = []
        for child in children:
            # If '_docType' is not in the props of the child, but 'name' is, we add this child to our list
            if '_docType' not in child['props'] and 'name' in child['props']:
                temp_list.append(child['props']['name'])
        # Assign the list of child names to the corresponding parent id in the result dict
        if temp_list:
            children_for_nodes[parent_id] = temp_list

    return children_for_nodes


def remove_extractor_prefix(word:str):
    modified_word = word.replace('_extractor', '')
    return modified_word


def format_tags(tags_csv: str, extraction_keyword:str) -> List[str]:
    '''
    tags_csv is something like: 'tags_to_extract, another_tag, something_else'
    This indicates the tags you want to extract from the json file
    '''
    if not tags_csv.strip():
        return []
    list_of_tags = tags_csv.split(',') 
    list_of_extractors = [(tag.strip()) + extraction_keyword for tag in list_of_tags]
    return list_of_extractors


def main(directory: str, filename: str, extraction_keyword: str, tags_to_extract: str):

    extractors = format_tags(tags_csv=tags_to_extract, extraction_keyword=extraction_keyword)
    json_path = search_file(directory, filename)

    if json_path:
        found_nodes_with_tags, docs = search_nodes_with_extractors(path=json_path, extractors=extractors)
    
    children_objects = find_children_objects(parent_objects=[node[1] for node in found_nodes_with_tags], docs=docs)

    node_fields = find_tuple_fields(docs, children_objects)

    children_nodes = find_children_nodes_for_parent(docs, children_objects)

    result = []

    # Iterate through objects with tag
    for name, obj, extractor in found_nodes_with_tags:
        result.append({
            'name': name,
            'tag': remove_extractor_prefix(extractor),
            'fields': node_fields.get(obj['id'], []),
            'children': children_nodes.get(obj['id'], []),
            'created_at': datetime.datetime.fromtimestamp(obj['props']['created'] / 1000).strftime('%Y-%m-%d %H:%M:%S')
        })

    with open(f'results_{filename}.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['name', 'tag', 'fields','children', 'created_at'])
        writer.writeheader()
        for res in result:
           
            res['fields'] = ', '.join(map(str, res['fields']))
            res['children'] = ', '.join(map(str, res['children']))
            writer.writerow(res)


if __name__ == "__main__":

    directory = "tana_info_jsons"
    filename = "charlytoc.json"
    extraction_keyword = '_extractor'
    tags_to_extract = 'movie, idea'

    main(directory=directory, 
         filename=filename, 
         extraction_keyword=extraction_keyword, 
         tags_to_extract=tags_to_extract
         )
