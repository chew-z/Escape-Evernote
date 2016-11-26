# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET
import os
import argparse
import base64
from dateutil import parser
import logging
import urllib
import html2text


def getArgs(argv=None):
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-d', '--directory', nargs='?', dest="directory",
                        default=os.getcwd(),
                        help="directory in which you wish to work")
    parser.add_argument('-f', '--file', nargs='?', dest="file",
                        default='Test.enex',
                        help="Evernote archive file (.enex)")
    parser.add_argument('-a', '--split_attachments', action="store_true", dest="attachments",
                        default=False,
                        help="Create separate folder with attachments for each note\n\
                        or [default] put all attachments prefixed in /attachments folder")
    parser.add_argument('-r', '--relative_path', action="store_true",
                        default=True,
                        help="Relative (or absolute) path for images")
    parser.add_argument('-v', '--version', action='version',
                        version='%(prog)s 0.2')
    parser.add_argument("-q", "--quiet", action="store_false", dest="verbose",
                        default=True,
                        help="don't print status messages to stdout")
    parser.add_argument("-t", "--tidy", action="store_true", dest="tidy",
                        default=False,
                        help="remove temporary files (.xml, .tmp, .log)")
    parser.add_argument('-l', '--log', '--logfile', dest="log", default='parse_enex.log',
                        help="logs notes processing")

    return parser.parse_args(argv)

args = getArgs()

logfile = args.log
FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
logging.basicConfig(filename=logfile, level=logging.DEBUG,
                    format=FORMAT, datefmt='%a, %d %b %Y %H:%M:%S',)
logging.info('--- parse_enex logging started ---')

h = html2text.HTML2Text()
html2text.decode_errors = 'replace'
# h.ignore_links = True
h.skip_internal_links = True
h.ignore_anchors = True
h.ignore_images = True
h.body_width = 0
html2text.unifiable = True
html2text.unicode_snob = True
# html2text.escape_snob = True
# html2text.re_unescape = True

directory = args.directory
logging.info('--- working  folder is: ' + directory)
file = args.file
logging.info('--- .enex  file is: ' + file)

tree = ET.parse(file)
root = tree.getroot()

for note in root:
    dirname = None
    title = note[0].text.encode('utf-8').replace('/', '_')
    if args.verbose:
        print "Processing note {}".format(title)
    updated = note[3].text
    created = note[2].text
    source_url = None
    try:
        attrs = note[4].getchildren()
        source = [x for x in note[4].getchildren() if x.tag == "source-url"]
        if source:
            source_url = source[0].text
    except Exception as e:
        logging.exception("Exception processing note")
    # content_xml = note[1].text.encode('utf-8').replace('&mdash;', '').replace('&nbsp;', '')
    content_xml = note[1].text.encode('utf-8')
    # unifiable = {'&rsquo;': "'", '&lsquo;': "'", '&rdquo;': '"', '&ldquo;': '"', '&copy;': '(C)', '&mdash;': '--', '&nbsp;': ' ', '&rarr;': '->', '&larr;': '<-', '&middot;': '*', '&ndash;': '-', '&oelig;': 'oe', '&aelig;': 'ae', '&lrm;': '', '&rlm;': '', '&hellip;': '...', '&ndash;': '——' }
    unifiable = {'&rsquo;': "'", '&lsquo;': "'", '&rdquo;': '"', '&ldquo;': '"',
                 '&nbsp;': ' ', '&quot;': '`', '&hellip;': '...', '&mdash;': '--', '&ndash;': '——'}
    for k, v in unifiable.iteritems():
        content_xml = content_xml.replace(k, v)
    with open(title + ".xml", 'w') as x:
        x.write(content_xml)
    text = h.handle(content_xml.decode('utf-8'))
    with open(title + ".md", 'w') as m:
        m.write("# " + title)
        m.write(text.encode('utf-8'))
    content = ET.fromstring(content_xml)
    logging.log(logging.INFO, "Creating note {}".format(title))

    line_count = 0
    current_tag = None
    previous_tag = None
    with open(title + ".tmp", 'w') as f:
        if source_url:
            f.write("\n\n * * *\n\nSource URL --> [{}]({})\n\n".format(source_url.encode('utf-8'),
                                                                       source_url.encode('utf-8')))
        for line in content.iter():
            logging.log(logging.INFO, "LINE: {!r} TEXT: {!r}".format(
                line.tag, line.text))
            previous_tag = current_tag
            current_tag = line.tag

            if line.tag == "en-media":
                if line.get('type', '').startswith('image'):
                    # use reference style link and add links at end
                    link_hash = line.get('hash')
                    f.write("\nIMG:{}\n".format(link_hash))
                    logging.log(
                        logging.INFO, "ADDING IMAGE TAG for {}".format(link_hash))
                    continue

    if note.find('./resource') is not None:
        logging.log(logging.INFO, "Note '{}' has an attachment".format(title))
        resources = note.findall('./resource')
        logging.log(logging.INFO, "found {} resources".format(len(resources)))
        image_links = {}
        for resource in resources:
            logging.log(logging.INFO, "looking at resource")
            # Grab the object ID and append it to the file for the reference
            # links
            resource_xml = resource.find('./recognition')
            if resource_xml is not None:
                res_tree = ET.fromstring(resource_xml.text.encode('utf-8'))
                object_id = res_tree.get('objID')
                logging.info("Found object ID: {}".format(object_id))
                binary = resource.find('./data')
                if binary.text is not None:
                    filename_resource = resource.find(
                        './resource-attributes/file-name')
                    if filename_resource is None:
                        logging.log(
                            logging.WARN, "no filename found, using object_id")
                        filename = object_id
                        # continue
                    else:
                        filename = filename_resource.text.encode('utf-8')
                    # dirname = title + " attachments"
                    if args.attachments:
                        dirname = title
                        attachments_prefix = ""
                    else:
                        dirname = "attachments"
                        attachments_prefix = title + "_"
                    if not os.path.exists(dirname):
                        os.mkdir(dirname)
                    resource_path = dirname + os.sep + attachments_prefix + filename
                    logging.log(
                        logging.INFO, "Creating resource file {}".format(resource_path))
                    with open(resource_path, 'w') as r:
                        r.write(base64.decodestring(binary.text))
                    # append the reference link to the text file
                    logging.info(
                        "Adding link {} to link list".format(resource_path))
                    image_links[object_id] = resource_path

        if image_links:
            lines = []
            logging.info("replacing image links in file now")
            with open(title + ".tmp") as infile:
                for line in infile:
                    for objid, target in image_links.iteritems():
                        if line.startswith('IMG:'):
                            # need the right format and base href
                            # See
                            # http://brettterpstra.com/2012/09/27/quick-tip-images-in-nvalt/
                            target_path = urllib.quote(target)
                            # file:/// - macOS
                            target_caption = "![{}]".format(target)
                            # TODO - add option for uploading imgaes to Google Drive, Dropbox etc.
                            # so storing images in cloud is safer and more universal
                            if args.relative_path:
                                target_url = "({})".format(target_path)
                                # target_url = "({})".format(
                                #    target_path).replace("%20", " ")
                                # target_url = "(/{})".format(target_path).replace("%20", " ")
                            else:
                                target_url = "(file://" + directory + \
                                    "/{})".format(target_path).replace("%20", " ")
                                # target_url = "(file://" + directory + "/{})".format(target_path).replace("%20", "\ ")
                            target_link = target_caption + target_url
                            new_line = line.replace(
                                'IMG:{}'.format(objid), target_link)
                            if line != new_line:
                                # print "Replaced {} with {}".format(line,
                                # new_line)
                                logging.info("replaced {} with {}".format(objid,
                                                                          target_link,
                                                                          line))
                            line = new_line
                    lines.append(line)

            logging.info("appending links to images to markdown file")
            with open(title + ".md", 'a') as outfile:
                for line in lines:
                    outfile.write(line)

    atime = mtime = int(parser.parse(updated).strftime('%s'))
    modif = (atime, mtime)
    logging.log(logging.INFO, "setting modification date to {}".format(mtime))
    os.utime(title + ".md", modif)
    if dirname is not None:
        os.utime(dirname, modif)
        os.utime(title + ".md", modif)
    if args.verbose:
        print "Note '{}' created on {}".format(title, created)

# Clean up after yourself
if args.tidy:
    filelist = [f for f in os.listdir(directory) if f.endswith(".tmp")]
    for f in filelist:
        os.remove(f)
    filelist = [f for f in os.listdir(directory) if f.endswith(".xml")]
    for f in filelist:
        os.remove(f)
    os.remove(logfile)
