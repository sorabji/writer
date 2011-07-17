#!/usr/bin/python
import pyblog
from optparse import OptionParser

parser = OptionParser()
parser.add_option("--url",
        type="string",
        dest="url",
        help="url to the xmlrpc on the blog")
parser.add_option("--user","-u",
        type="string",
        dest="user",
        help="username for the blog")
parser.add_option("--pwd","-p",
        type="string",
        dest="pwd",
        help="password for the blog")
parser.add_option("--postid",
        type="int",
        dest="postid",
        help="id of the post to be edited")
parser.add_option("--post",
        action="store_true",
        dest="isPost",
        default=False,
        help="flag to indicate the posting of a new...post")
parser.add_option("--edit",
        action="store_true",
        dest="isEdit",
        default=False,
        help="flag to indicate the editing of an old post...requires the postid of the post to edit")
parser.add_option("--delete",
        action="store_true",
        dest="isDelete",
        default=False,
        help="flag to indicate the deletion of an old post...requires the postid of the post to delete")

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
if (options.isDelete or options.isEdit) and (options.postid == None):
    parser.error("i need a postid in order to edit/delete a post")

if (options.postid!=None):
    postid = options.postid

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
did you notice? i edited the post
"""
#date_created = xmlrpclib.DateTime(datetime.datetime.strptime("2020-10-20 21:08", "%Y-%m-%d %H:%M"))
categories = ["tools","computers","totallynewcategory..."]
tags = ["sometag", "othertag"]
data = {'title': title, 'description': content, 'categories': categories, 'mt_keywords': tags}

if options.isPost:
    postid = blog.new_post(data)
    print "the new post has an id of:%d" % postid
    exit(0)
elif options.isDelete:
    success = blog.delete_post(postid)
    if success:
        print "post %d was deleted!" % postid
        exit(0)
    else:
        print "post %d could not be deleted :<" % postid
        exit(1)
elif options.isEdit:
    success = blog.edit_post(postid,data)
    if success:
        print "post %d was edited!" % postid
        exit(0)
    else:
        print "post %d could not be edited :<" % postid
        exit(1)
