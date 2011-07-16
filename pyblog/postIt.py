#!/usr/bin/python
import pyblog
from optparse import OptionParser

parser = OptionParser()
parser.add_option("--url",
        action="store",
        type="string",
        dest="url",
        help="url to the xmlrpc on the blog")
parser.add_option("--user","-u",
        action="store",
        type="string",
        dest="user",
        help="username for the blog")
parser.add_option("--pwd","-p",
        action="store",
        type="string",
        dest="pwd",
        help="password for the blog")

(options,args) = parser.parse_args()

if (options.url!=None):
    url = options.url
else:
    url = "http://ratio.devvz.com/wordpress/blog/xmlrpc.php"
    #print "you must give a url"
    #exit(0)
if (options.user!=None):
    user = options.user
else:
    user = "admin"
    #print "you must give a username"
    #exit(0)
if (options.pwd!=None):
    pwd = options.pwd
else:
    pwd = "52cards"
    #print "you must give a password"
    #exit(0)

#blogID = ""

status_draft = 0
status_published = 1

blog = pyblog.MetaWeblog(url,user,pwd)

title = "Title with spaces"
content = """
here is a fair amount of content.
someday, this project will work itself out...i don't exactly know when, but
honestly, i wish it would just write itself.  lack of documentation really
blows sometime, you know?
<a href="http://www.google.com">and a link</a>
"""
#date_created = xmlrpclib.DateTime(datetime.datetime.strptime("2020-10-20 21:08", "%Y-%m-%d %H:%M"))
categories = ["tools","computers","totallynewcategory..."]
tags = ["sometag", "othertag"]
data = {'title': title, 'description': content, 'categories': categories, 'mt_keywords': tags}

post_id = blog.new_post(data)
print post_id
print "post was...posted"
