#!/bin/python
import datetime, xmlrpclib

wp_url = "http://ratio.devvz.com/wordpress/blog/xmlrpc.php"
wp_username = "admin"
wp_password = "52cards"
wp_blogid = ""

status_draft = 0
status_published = 1

server = xmlrpclib.ServerProxy(wp_url)

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

post_id = server.metaWeblog.newPost(wp_blogid, wp_username, wp_password, data, 1)
