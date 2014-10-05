TITLE  = 'Finkammat'
PREFIX = '/video/finkammat'

ICON  = 'icon-default.png'

USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/600.1.17 (KHTML, like Gecko) Version/7.1 Safari/537.85.10'
BASE_URL = 'http://finkammat.se/'

###################################################################################################
def Start():

    ObjectContainer.title1 = TITLE
    
    DirectoryObject.thumb = R(ICON)
    
    HTTP.CacheTime = CACHE_1HOUR
    HTTP.Headers['User-agent'] = USER_AGENT

###################################################################################################
@handler(PREFIX, TITLE, thumb = ICON)
def MainMenu():

    oc = ObjectContainer()

    title = 'Nykammat - Senaste'
    oc.add(
        DirectoryObject(
            key =
                Callback(
                    Articles,
                    title = title,
                    url = BASE_URL + 'nykammat'
                ),
            title = title
        )
    )

    title = unicode('Välkammat - Mest sedda')
    oc.add(
        DirectoryObject(
            key =
                Callback(
                    Articles,
                    title = title,
                    url = BASE_URL + 'valkammat'
                ),
            title = title
        )
    )
    
    title = unicode('Okammat - Mer!')
    oc.add(
        DirectoryObject(
            key =
                Callback(
                    Articles,
                    title = title,
                    url = BASE_URL + 'okammat'
                ),
            title = title
        )
    )
    
    title = unicode('Kategorier')
    oc.add(
        DirectoryObject(
            key =
                Callback(
                    Categories,
                    title = title,
                    url = BASE_URL
                ),
            title = title
        )
    )

    return oc

####################################################################################################
@route(PREFIX + '/Categories')
def Categories(title, url):

    oc = ObjectContainer(title2 = unicode(title))

    pageElement = HTML.ElementFromURL(url)

    for item in pageElement.xpath("//*[@class='submenu']//a"):
        title = unicode(item.xpath("./text()")[0])
        url   = item.xpath("./@href")[0]
        
        if not url.startswith('http'):
            url = BASE_URL + url
        
        oc.add(
            DirectoryObject(
                key = Callback(Articles, title = title, url = url),
                title = title
            )
        )
        
    return oc

####################################################################################################
@route(PREFIX + '/Articles', page = int)
def Articles(title, url, page = 0):

    oc = ObjectContainer(title2 = unicode(title))

    pageElement = HTML.ElementFromURL(url + '/page/%s' % page)

    for item in pageElement.xpath("//article"):
        try:
            articleURL = item.xpath(".//a/@href")[0].replace("..", "")
        except:
            continue

        if not articleURL.startswith('http'):
            articleURL = url + articleURL
        
        articleTitle   = unicode(item.xpath(".//img/@alt")[0].strip().lower().replace(".jpg", "").replace(".png", "").title())
        articleSummary = unicode(item.xpath(".//h2/text()")[0].strip())
        
        articleThumb = item.xpath(".//img/@src")[0]

        if not articleThumb.startswith('http'):
            articleThumb = BASE_URL + articleThumb

        isVideo = len(item.xpath(".//*[@class='playButton']//*[contains(@class,'youtube')]")) > 0
        
        if isVideo:
            oc.add(
                DirectoryObject(
                    key =
                        Callback(
                            Video,
                            title = articleTitle,
                            url = articleURL
                        ),
                    title = articleTitle,
                    summary = articleSummary,
                    thumb = articleThumb
                )
            )
        else:
            oc.add(
                PhotoAlbumObject(
                    key =
                        Callback(
                            Photo,
                            title = articleTitle,
                            url = articleURL
                        ),
                    rating_key = articleTitle,
                    title = articleTitle,
                    summary = articleSummary,
                    thumb = articleThumb
                )
            )
    
    if len(oc) < 1:
        oc.header  = "Oops"
        oc.message = unicode("Kunde inte hitta några fler videos")
    else:
        oc.add(
            NextPageObject(
                key = Callback(Articles, title = title, url = url, page = page + 1),
                title = 'Fler ...'
            )
        )

    return oc

####################################################################################################
@route(PREFIX + '/Video')
def Video(title, url):

    oc = ObjectContainer(title2 = unicode(title))
    
    pageElement = HTML.ElementFromURL(url)

    for link in pageElement.xpath("//*[contains(@src, 'youtube.com/embed')]"):
        url = 'http:' + link.xpath("./@src")[0]
        
        oc.add(
            URLService.MetadataObjectForURL(url)
        )
        
        break

    return oc
    
####################################################################################################
@route(PREFIX + '/Photo')
def Photo(title, url):

    oc = ObjectContainer(title2 = unicode(title))
    
    pageElement = HTML.ElementFromURL(url)
    
    photos = []
    photo = {}
    
    for item in pageElement.xpath("//*[@class='mediaText']//*[@class='descriptionText']//following-sibling::*"):
        if item.xpath("name()")[0] == 'h':
            try:
                text = item.xpath("./text()")[0]
            except:
                text = None
            
            if text:
                # Start of a new image section
                if photo:
                    photos.append(photo)

                photo = {}
                photo['title'] = unicode(text)
                photo['images'] = []
                photo['summary'] = None
        
        if photo:
            try:
                photo['images'].append(item.xpath(".//img/@data-src")[0])
            except:
                pass
            
            if not photo['summary'] and item.xpath("name()")[0] == 'p':
                try:
                    photo['summary'] = item.xpath("./text()")[0]
                except:
                    pass
                    
    if not photos:
        # Page with no text just images
        images = pageElement.xpath("//*[@class='mediaText']//*[@class='descriptionText']//following-sibling::*//img/@data-src")
        
        for image in images:
            oc.add(
                PhotoObject(
                    key = image,
                    rating_key = image,
                    title = title,
                    thumb = image
                )
            )
        
    else:       
        for photo in photos:
            for image in photo['images']:
                oc.add(
                    PhotoObject(
                        key = image,
                        rating_key = image,
                        title = photo['title'],
                        summary = photo['summary'],
                        thumb = image
                    )
                )
        
    return oc

