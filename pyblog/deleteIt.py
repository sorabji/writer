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
parser.add_option("--postid",
        action="store",
        type="int",
        dest="postid",
        help="id of the post to be deleted")

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
if (options.postid!=None):
    postid = options.postid
else:
    postid = 0

#blogID = ""

status_draft = 0
status_published = 1

blog = pyblog.MetaWeblog(url,user,pwd)

#date_created = xmlrpclib.DateTime(datetime.datetime.strptime("2020-10-20 21:08", "%Y-%m-%d %H:%M"))

post_id = blog.delete_post(postid)
print post_id
print "post was...deleted"
