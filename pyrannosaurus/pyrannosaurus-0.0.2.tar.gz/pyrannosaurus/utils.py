import base64
from lxml import etree
import os
import zipfile

from pyrannosaurus.lib.metadata import Metadata

NS = "http://soap.sforce.com/2006/04/metadata"
NS_FULL = "{http://soap.sforce.com/2006/04/metadata}"
NAMESPACES = {"sf": NS}
METADATA_TYPE = {'object': 'CustomObject'}

def package_to_dict(file_path):
    parser = etree.XMLParser(remove_blank_text=True)
    meta_types = {}
    pkg_manifest = etree.parse(file_path,parser)
    root = pkg_manifest.getroot()
    #loop through each type node in the package
    for item in root.xpath("sf:types",namespaces=NAMESPACES):
        #get the meta name and create it in  the new package if it doesn't exist, using asterisk wildcard
        meta_name = item.xpath("sf:name/text()", namespaces=NAMESPACES)[0]
        meta_types[meta_name] = []
        for mem in item.xpath("sf:members/text()", namespaces=NAMESPACES):
            meta_types[meta_name].append(mem)

    return meta_types

def zip(src):
    zf = zipfile.ZipFile("deploy.zip" , "w")
    abs_src = os.path.abspath(src)
    for dirname, subdirs, files in os.walk(src):
        for filename in files:
            absname = os.path.abspath(os.path.join(dirname, filename))
            arcname = absname[len(abs_src) + 1:]
            print 'zipping %s as %s' % (os.path.join(dirname, filename),
                                        arcname)
            zf.write(absname, arcname)
    zf.close()

def binary_to_zip(zip_response):
    ''' Handle the SF Metadata API checkRetrieveStatus zip file response '''

    decoded_file = base64.b64decode(zip_response)
    zip_file = open('retrieve.zip', 'w')
    zip_file.write(decoded_file)
    zip_file.close()

def zip_to_binary(file_path):
    #TODO: make this absolute
    zip_file = open(file_path)
    zip_contents = zip_file.read()
    encoded_file = base64.b64encode(zip_contents)
    zip_file.close()
    return encoded_file

def get_object(file_name='Account.object'):
    parser = etree.XMLParser(remove_blank_text=True)
    x = etree.parse(file_name).getroot()
    primary_nodes = []
    name = file_name.split(".", 1)[0]
    obj_type = file_name.split(".", 1)[1]
    meta = Metadata(name=file_name, obj_type=obj_type)

    for node in x.getchildren():
        node_tag = node.tag.replace(NS_FULL,"")
        if node_tag not in primary_nodes:
            meta.add_child(node_tag)
            primary_nodes.append(node_tag)

    for node in primary_nodes:
        for child_node in x.xpath("sf:" + node, namespaces=NAMESPACES):
            if not child_node.getchildren():
                meta.add_property(child_node.tag.replace(NS_FULL, ""), child_node.text)
            else:
                cm = Metadata(name=child_node.tag.replace(NS_FULL, ""))
                for pr in child_node.getchildren():
                    if not pr.getchildren():
                        cm.add_property(pr.tag.replace(NS_FULL, ""), pr.text)
                    else:
                        name, sub_meta = get_child_node(pr)
                        cm.add_child(pr.tag.replace(NS_FULL, ""), value=sub_meta)

                (meta.__dict__[node]).append(cm)

    return meta

def get_child_node(node):
    sub_meta = []
    name = ""
    for pr in node.getchildren():
        name = pr.tag.replace(NS_FULL, "")
        sm = Metadata()
        has_children = False
        for check_children in pr.getchildren():
            if check_children.getchildren():
                has_children = True
                break

        if pr.getchildren() and has_children:
            r_name, r_meta = get_child_node(pr)
            sm.add_child(name, value=r_meta)
        elif pr.getchildren and not has_children:
            for sv in pr.getchildren():
                sm.add_property(sv.tag.replace(NS_FULL, ""), sv.text)
        else:
            sm.add_property(sv.tag.replace(NS_FULL, ""), sv.text)

        sub_meta.append(sm)

    return name, sub_meta


