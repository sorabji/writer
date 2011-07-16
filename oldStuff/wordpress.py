"""
	wordpresslib.py

	WordPress xml-rpc client library

	Copyright (C) 2005 Michele Ferretti
	black.bird@tiscali.it
	http://www.blackbirdblog.it

	Copyright (C) 2008 Daniel Martin Yerga
	dyerga@gmail.com
	http://www.yerga.net

	Some code from wordmoby: http://code.google.com/p/wordmobi/
	Copyright (C) Marcelo Barros

	This program is free software; you can redistribute it and/or
	modify it under the terms of the GNU General Public License
	as published by the Free Software Foundation; either version 2
	of the License, or any later version.

	This program is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
	GNU General Public License for more details.

	You should have received a copy of the GNU General Public License
	along with this program; if not, write to the Free Software
	Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA	02111-1307, USA.

	Daniel Martin Yerga <dyerga@gmail.org> has modified this library
	for add diverse functions as to post trackbacks, choose if allow
	pings and comments, post advanced entries, optional excerpt, tags, etc.

	XML-RPC supported methods:
		* getUserInfo
		* getUsersBlogs
		* getAuthors
		* getRecentPosts
		* getRecentPostTitles
        * getPost
		* newPost
		* editPost
		* deletePost
		* publishPost
		* getPostCategories
		* setPostCategories
        * newCategory
        * deleteCategory
        * getCategories
		* getCategoryList
		* supportedMethods
        * getPostStatusList
        * getPageTemplates
		* getTrackbackPings
		* getPingbacks
		* newMediaObject
		* getCommentCount
		* getComments
		* getComment

	References:
		* http://codex.wordpress.org/XML-RPC_Support
		* http://www.sixapart.com/movabletype/docs/mtmanual_programmatic.html
		* http://docs.python.org/lib/module-xmlrpclib.html

"""

__author__ = "Daniel Martin Yerga <dyerga@gmail.com>"
__version__ = "$Revision: 1.3 $"
__date__ = "$Date: 2009/12/21 $"
__copyright__ = "Copyright (c) 2009 Daniel Martin Yerga"
__license__ = "LGPL"

import exceptions
import re
import os
import xmlrpclib
import time

def create_wordpress_client(url, user, password):
    """Quick helper routine used to create the wordpress
    client"""
    # prepare client object
    try:
        wp = WordPressClient(url, user, password)
    except:
        return None

    # select blog id
    wp.selectBlog(0)

    return wp

def get_post_filtered(url, user, password, postid):
    wp = create_wordpress_client(url, user, password)
    wp.selectBlog(0)
    post = wp.getPost(postid)
    title = post.title
    content = post.description
    ttags = ''
    tracks = ''
    if content.find("Technorati Tags:") >= 0:
        techno_tags = []
        hele = re.compile(r'"http://technorati.com/tag/[^$%]+"')
        a = hele.findall(content)
        b = a[0].split('"')
        for j in range(len(b)):
            if b[j].find("http://technorati.com/tag/") >=0:
                c = b[j].replace('http://technorati.com/tag/', '')
                techno_tags.append(c)

        ttags = (', ').join(techno_tags)

        if content.find("<small>Technorati Tags:") >= 0:
            descr = content.partition('<br /><br /><p style="text-align: right"><small>Technorati Tags:')
        else:
            descr = content.partition('<br /><br /><p style="text-align:right;">Technorati Tags:')

        content = descr[0]

    extended = post.textMore
    extended = extended.replace('<br />', '')
    excerpt = post.excerpt
    tags = post.tags
    edit_cats = post.categories
    cats = []
    for i in edit_cats:
        cat_id = wp.getCategoryIdFromName(i)
        one_cat = [cat_id, i]
        cats.append(one_cat)
    postdate = post.date
    date = []
    for i in range(len(postdate)):
        if i < 5:
            date.append(postdate[i])
    slug = post.name
    pssword = post.password
    comments = post.allowComments
    pings = post.allowPings
    status = post.status
    postid = post.id

    return (title, content, extended, excerpt, ttags, tracks, tags, cats, date, \
            slug, pssword, comments, pings, status, postid)

def get_posts_with_status(url, user, password, numposts):
    wp = create_wordpress_client(url, user, password)
    wp.selectBlog(0)
    posts = []
    recentposts = wp.getRecentPosts(numposts)
    for i in recentposts:
        title = i.title
        postid = i.id
        status = i.status
        post = [title, postid, status]
        posts.append(post)

    return posts

def get_comments_filtered(url, user, password, postid, numcomm):
    wp = create_wordpress_client(url, user, password)
    wp.selectBlog(0)
    wpc = WordPressComment()
    wpc.post_id = postid
    wpc.number = numcomm
    comm = wp.getComments(wpc)
    comments = []

    for i in comm:
        adate = time.strptime(str(i['date_created_gmt']), "%Y%m%dT%H:%M:%S")
        date = "%s-%s-%s" % (adate[0], adate[1], adate[2])
        comments.append([i['comment_id'], i['content'], date, i['author'],
                i['author_email'], i['author_url'], i['status']])

    return comments

def new_comment(url, user, password, postid, content):
    wp = create_wordpress_client(url, user, password)
    wp.selectBlog(0)
    wpc = WordPressNewComment()
    #wpc.status = ''
    wpc.content = content
    #wpc.author = author
    #wpc.author_url = ''
    #wpc.author_email = ''
    comment = wp.newComment(postid, wpc)
    wpc = wp.getComment(comment)

    return wpc

def edit_comment(url, user, password, commid, data):
    wp = create_wordpress_client(url, user, password)
    wp.selectBlog(0)
    #data = [content, author, autemail, auturl, status]
    wpc = WordPressEditComment()
    wpc.status = data[5]
    #wpc.date_created_gmt =
    wpc.content = data[0]
    wpc.author = data[1]
    wpc.author_url = data[4]
    wpc.author_email = data[3]
    comment = wp.editComment(commid, wpc)
    return comment

class WordPressException(exceptions.Exception):
    """Custom exception for WordPress client operations
    """
    def __init__(self, obj):
        if isinstance(obj, xmlrpclib.Fault):
            self.id = obj.faultCode
            self.message = obj.faultString
        else:
            self.id = 0
            self.message = obj

    def __str__(self):
        return '<%s %d: \'%s\'>' % (self.__class__.__name__, self.id, self.message)

class WordPressComment:
    """Represents comment item
    """
    def __init__(self):
        self.post_id = ''
        self.status = ''
        self.offset = 0
        self.number = 10

class WordPressEditComment:
    """Represents comment item for editing
    """
    def __init__(self):
        self.status = ''
        self.date_created_gmt = ''
        self.content = ''
        self.author = ''
        self.author_url = ''
        self.author_email = ''

class WordPressNewComment:
    """Represents a new comment
    """
    def __init__(self):
        self.status = ''
        self.content = ''
        self.author = ''
        self.author_url = ''
        self.author_email = ''

class WordPressBlog:
    """Represents blog item
    """
    def __init__(self):
        self.id = ''
        self.name = ''
        self.url = ''
        self.isAdmin = False

class WordPressAuthor:
    def __init__(self):
        self.user_id = ''
        self.user_login = ''
        self.display_name = ''

class WordPressUser:
    """Represents user item
    """
    def __init__(self):
        self.id = ''
        self.firstName = ''
        self.lastName = ''
        self.nickname = ''
        self.url = ''

class WordPressNewCategory:
    def __init__(self):
        self.name = ''
        self.slug = ''
        self.parent_id = ''
        self.description = ''

class WordPressCategory:
    """Represents category item
    """
    def __init__(self):
        self.id = 0
        self.name = ''
        self.isPrimary = False

class MetaWeblogCategory:
    def __init__(self):
        self.id = 0
        self.parentId = ''
        self.description = ''
        self.name = ''
        self.htmlurl = ''
        self.rssurl = ''

class WordPressPost:
    """Represents post item
    """
    def __init__(self):
        self.id = 0
        self.title = ''
        self.date = None
        self.permaLink = ''
        self.description = ''
        self.textMore = ''
        self.excerpt = ''
        self.link = ''
        self.categories = []
        self.user = ''
        self.trackbacks = ''
        self.allowPings	= False
        self.allowComments = False
        self.password = ''
        self.tags = ''
        self.name = ''

class WordPressClient:
    """Client for connect to WordPress XML-RPC interface
    """

    def __init__(self, url, user, password):
        self.url = url
        self.user = user
        self.password = password
        self.blogId = 0
        self.categories = None
        self._server = xmlrpclib.ServerProxy(self.url)

    def _filterPost(self, post):
        """Transform post struct in WordPressPost instance
        """
        postObj = WordPressPost()
        postObj.permaLink 		= post['permaLink']
        postObj.description 	= post['description']
        postObj.title 			= post['title']
        postObj.excerpt 		= post['mt_excerpt']
        postObj.user 			= post['userid']
        postObj.date 			= time.strptime(str(post['dateCreated']), \
                                                "%Y%m%dT%H:%M:%S")
        postObj.link 			= post['link']
        postObj.textMore 		= post['mt_text_more']
        postObj.allowComments 	= post['mt_allow_comments']
        postObj.id 				= int(post['postid'])
        postObj.categories 		= post['categories']
        postObj.allowPings 		= post['mt_allow_pings']
        postObj.password 		= post['wp_password']
        postObj.tags            = post['mt_keywords']
        postObj.status          = post['post_status']
        postObj.name            = post['wp_slug']

        return postObj

    def _filterNewCategory(self, category):
        NewCatObj = WordpressNewCategory()
        NewCatObj.name = category['name']
        NewCatObj.slug = category['slug']
        NewCatObj.parent_id = category['parent_id']
        NewCatObj.description = category['description']
        return NewCatObj

    def _filterCategory(self, cat):
        """Transform category struct in WordPressCategory instance
        """
        catObj = WordPressCategory()
        catObj.id 			= int(cat['categoryId'])
        catObj.name 		= cat['categoryName']
        if cat.has_key('isPrimary'):
            catObj.isPrimary 	= cat['isPrimary']
        return catObj

    def selectBlog(self, blogId):
        self.blogId = blogId

    ###################################
    ##                               ##
    ##      Blog functions           ##
    ##                               ##
    ###################################

    def getUserInfo(self):
        """Get user info
        """
        try:
            userinfo = self._server.blogger.getUserInfo('', self.user, \
                                                        self.password)
            userObj = WordPressUser()
            userObj.id = userinfo['userid']
            userObj.firstName = userinfo['firstname']
            userObj.lastName = userinfo['lastname']
            userObj.nickname = userinfo['nickname']
            userObj.url = userinfo['url']
            return userObj
        except xmlrpclib.Fault, fault:
            raise WordPressException(fault)

    def getUsersBlogs(self):
        """Get blog's users info
        """
        try:
            blogs = self._server.wp.getUsersBlogs(self.user, self.password)
            for blog in blogs:
                blogObj = WordPressBlog()
                blogObj.id = blog['blogid']
                blogObj.name = blog['blogName']
                blogObj.isAdmin = blog['isAdmin']
                blogObj.url = blog['url']
                yield blogObj
        except xmlrpclib.Fault, fault:
            raise WordPressException(fault)

    def getAuthors(self):
        """Get authors from the selected blog
        """
        try:
            authors = self._server.wp.getAuthors(self.blogId, self.user, \
                                                    self.password)
            for author in authors:
                userObj = WordPressAuthor()
                userObj.user_id = author['user_id']
                userObj.user_login = author['user_login']
                userObj.display_name = author['display_name']
                yield userObj
        except xmlrpclib.Fault, fault:
            raise WordPressException(fault)

    ###################################
    ##                               ##
    ##     Posting functions         ##
    ##                               ##
    ###################################

    def getLastPost(self):
        """Get last post
        """
        return tuple(self.getRecentPosts(1))[0]

    def getRecentPosts(self, numPosts=5):
        """Get recent posts
        """
        try:
            posts = self._server.metaWeblog.getRecentPosts(self.blogId, \
                                            self.user, self.password, numPosts)
            for post in posts:
                yield self._filterPost(post)
        except xmlrpclib.Fault, fault:
            raise WordPressException(fault)

    def getRecentPostTitles(self, numPosts=5):
        posts = self._server.mt.getRecentPostTitles(self.blogId, self.user, \
                                                    self.password, numPosts)
        for post in posts:
            postObj = WordPressPost()
            postObj.title = post['title']
            postObj.user = post['userid']
            postObj.date = time.strptime(str(post['dateCreated']), "%Y%m%dT%H:%M:%S")
            postObj.id = int(post['postid'])
            yield postObj

    def getPost(self, postId):
        """Get post item
        """
        try:
            return self._filterPost(self._server.metaWeblog.getPost(str(postId), \
                                    self.user, self.password))
        except xmlrpclib.Fault, fault:
            raise WordPressException(fault)

    def newPost(self, post):
        """Insert new post
        """
        blogContent = {
            'title' : post.title,
            'description' : post.description,
            'mt_tb_ping_urls' : post.trackbacks,
            'mt_allow_comments' : post.allowComments,
            'mt_text_more' : post.textMore,
            'mt_excerpt' : post.excerpt,
            'mt_allow_pings' : post.allowPings,
            'wp_password' : post.password,
            'mt_keywords' : post.tags,
            'post_status' : post.status,
            'wp_slug': post.name
        }

        if post.date:
            blogContent['dateCreated'] = xmlrpclib.DateTime(post.date)

        # add categories
        i = 0
        categories = []
        for cat in post.categories:
            if i == 0:
                categories.append({'categoryId' : cat, 'isPrimary' : 1})
            else:
                categories.append({'categoryId' : cat, 'isPrimary' : 0})
            i += 1

        # insert new post
        idNewPost = int(self._server.metaWeblog.newPost(self.blogId, self.user, \
                                                self.password, blogContent, 0))

        # set categories for new post
        self.setPostCategories(idNewPost, categories)

        lastpost = self.getLastPost().link
        return lastpost

    def editPost(self, postId, post):
        """Edit post
        """
        blogcontent = {
            'title' : post.title,
            'description' : post.description,
            'mt_allow_comments' : post.allowComments,
            'permaLink' : post.permaLink,
            'mt_allow_pings' : post.allowPings,
            'mt_text_more' : post.textMore,
            'mt_excerpt' : post.excerpt,
            'mt_tb_ping_urls' : post.trackbacks,
            'post_status' : post.status,
            'wp_password' : post.password,
            'mt_keywords' : post.tags,
            'wp_slug' : post.name
        }

        if post.date:
            blogcontent['dateCreated'] = xmlrpclib.DateTime(post.date)

        # add categories
        i = 0
        categories = []
        for cat in post.categories:
            if i == 0:
                categories.append({'categoryId' : cat, 'isPrimary' : 1})
            else:
                categories.append({'categoryId' : cat, 'isPrimary' : 0})
            i += 1

        result = self._server.metaWeblog.editPost(postId, self.user, \
                                                self.password, blogcontent, 0)
        if result == 0:
            raise WordPressException('Post edit failed')

        # set categories for new post
        self.setPostCategories(postId, categories)

        return result

    def deletePost(self, postId):
        """Delete post
        """
        try:
            return self._server.blogger.deletePost('', postId, self.user, \
                                                    self.password)
        except xmlrpclib.Fault, fault:
            raise WordPressException(fault)

    def publishPost(self, postId):
        """Publish post
        """
        try:
            return (self._server.mt.publishPost(postId, self.user, self.password) == 1)
        except xmlrpclib.Fault, fault:
            raise WordPressException(fault)

    def getPostCategories(self, postId):
        """Get post's categories
        """
        try:
            categories = self._server.mt.getPostCategories(postId, self.user, \
                                                            self.password)
            for cat in categories:
                yield self._filterCategory(cat)
        except xmlrpclib.Fault, fault:
            raise WordPressException(fault)

    def setPostCategories(self, postId, categories):
        """Set post's categories
        """
        self._server.mt.setPostCategories(postId, self.user, self.password, categories)

    ###################################
    ##                               ##
    ##     Categories functions      ##
    ##                               ##
    ###################################

    def newCategory(self, category):
        newcat = {
            'name' : category.name,
            'slug' : category.slug,
            'parent_id' : category.parent_id,
            'description' : category.description
        }
        catid = self._server.wp.newCategory(self.blogId, self.user, self.password, newcat)
        return catid

    def deleteCategory(self, cat_name):
        try:
            catid = self.getCategoryIdFromName(cat_name)
            self._server.wp.deleteCategory(self.blogId, self.user, \
                                            self.password, catid)
        except xmlrpclib.Fault, fault:
            raise WordPressException(fault)

    def getCategories(self):
        try:
            categories = self._server.metaWeblog.getCategories(self.blogId, \
                                                    self.user, self.password)
            for cat in categories:
                catObj = MetaWeblogCategory()
                catObj.id = cat['categoryId']
                catObj.parentId = cat['parentId']
                catObj.description = cat['description']
                catObj.name = cat['categoryName']
                catObj.htmlurl = cat['htmlUrl']
                catObj.rssurl = cat['rssUrl']
                yield catObj
        except xmlrpclib.Fault, fault:
            raise WordPressException(fault)

    def getCategoryList(self):
        """Get blog's categories list
        """
        try:
            if not self.categories:
                self.categories = []
                categories = self._server.mt.getCategoryList(self.blogId,
                                                    self.user, self.password)
                for cat in categories:
                    self.categories.append(self._filterCategory(cat))
            return self.categories
        except xmlrpclib.Fault, fault:
            raise WordPressException(fault)

    def getCategoryIdFromName(self, name):
        """Get category id from category name
        """
        for c in self.getCategoryList():
            if c.name == name:
                return c.id

    def getTags(self):
        """Get all tags
        """
        tags = []
        try:
            tags = self._server.wp.getTags(self.blogId, self.user,
                                            self.password)
        except xmlrpclib.Fault, fault:
            raise WordPressException(fault)

        return tags


    ###################################
    ##                               ##
    ##      Comments functions       ##
    ##                               ##
    ###################################

    def getCommentCount(self, post_id = ''):
        """Get the number of comm for a post or for the blog ( post_id = '' )
        """
        try:
            comments_cnt = self._server.wp.getCommentCount(self.blogId,
                                        self.user, self.password, post_id)
        except xmlrpclib.Fault, fault:
            raise WordPressException(fault)

        return comments_cnt


    def getComment(self, commentId):
        """Get a comment
        """
        try:
            comment = self._server.wp.getComment(self.blogId, self.user,
                                                self.password, commentId)
        except xmlrpclib.Fault, fault:
            raise WordPressException(fault)

        return comment

    def getComments(self, commInfo):
        """Get comments for a given post. Use WordPressComment
        """
        try:
            comments = self._server.wp.getComments(self.blogId, self.user,
                                                    self.password, commInfo)
        except xmlrpclib.Fault, fault:
            raise WordPressException(fault)

        return comments

    def editComment(self, commentId, commEdit):
        """Get comments for a given post. Use WordPressCommentEdit
        """
        try:
            resp = self._server.wp.editComment(self.blogId, self.user,
                                            self.password, commentId, commEdit)
        except xmlrpclib.Fault, fault:
            raise WordPressException(fault)

        return resp

    def deleteComment(self, commentId):
        """Delete a comment
        """
        try:
            resp = self._server.wp.deleteComment(self.blogId, self.user,
                                                    self.password, commentId)
        except xmlrpclib.Fault, fault:
            raise WordPressException(fault)

        return resp

    def newComment(self, postId, commentNew):
        """Insert a new comment
        """
        try:
            comment = self._server.wp.newComment(self.blogId, self.user,
                                            self.password, postId, commentNew)
        except xmlrpclib.Fault, fault:
            raise WordPressException(fault)

        return comment

    ###################################
    ##                               ##
    ##      Other functions          ##
    ##                               ##
    ###################################

    def supportedMethods(self):
        """Get supported methods list
        """
        return self._server.mt.supportedMethods()

    def getPostStatusList(self):
        status_list = self._server.wp.getPostStatusList(self.blogId, self.user, \
                                                    self.password)
        return status_list

    def getPageTemplates(self):
        tmpl = self._server.wp.getPageTemplates(self.blogId, self.user, \
                                                self.password)
        return tmpl

    def getTrackbackPings(self, postId):
        """Get trackback pings of post
        """
        try:
            return self._server.mt.getTrackbackPings(postId)
        except xmlrpclib.Fault, fault:
            raise WordPressException(fault)

    def getPingbacks(self, postUrl):
        """Get pingbacks of post
        """
        try:
            return self._server.pingback.extensions.getPingbacks(postUrl)
        except xmlrpclib.Fault, fault:
            raise WordPressException(fault)

    def newMediaObject(self, mediaFileName):
        """Add new media object (image, movie, etc...)
        """
        try:
            f = file(mediaFileName, 'rb')
            mediaBits = f.read()
            f.close()

            mediaStruct = {
                'name' : os.path.basename(mediaFileName),
                'bits' : xmlrpclib.Binary(mediaBits)
            }

            result = self._server.metaWeblog.newMediaObject(self.blogId, \
                                        self.user, self.password, mediaStruct)
            return result['url']

        except xmlrpclib.Fault, fault:
            raise WordPressException(fault)

