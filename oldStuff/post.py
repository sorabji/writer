import xmlrpclib

class PostIt:
    """This class posts a blog.  constructor takes:
        user = username for the blog
        passwd = password for the blog
        xmlrpcUrl = the url for the xmlrpc on the wordpress blog
        blog_id = id for the blog to be posted
        title = title of the blog to be posted
        content = string containing the content of the post
        """
    #import xmlrpclib

    def __init__(self,user,passwd,xmlrpcUrl,blog_id,title,content):
        self.user = user
        self.passwd = passwd
        self.xmlrpcUrl = xmlrpcUrl
        self.blog_id = blog_id
        self.title = title
        self.content = content

    def post(self):
        server = xmlrpclib.ServerProxy(self.xmlrpcUrl)

        blog_content = { 'title' : self.title, 'description' : self.content }
        categories = [{'categoryId' : 'programming', 'isPrimary' : 1}]

        post_id = int(server.metaWeblog.newPost(self.blog_id, self.user, self.passwd, blog_content,0))
        server.mt.setPostCategories(post_id, self.user, self.passwd, categories) # not work
        server.mt.publishPost(post_id, self.user, self.passwd)

