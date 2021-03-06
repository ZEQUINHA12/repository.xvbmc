# ===============================================================================
# Make global object available
# ===============================================================================
import chn_class
import mediaitem
# from parserdata import ParserData
from locker import LockWithDialog
from config import Config
from helpers.xmlhelper import XmlHelper
from helpers import subtitlehelper
from helpers.jsonhelper import JsonHelper
from helpers.languagehelper import LanguageHelper
from helpers.datehelper import DateHelper
from streams.f4m import F4m
from logger import Logger
from parserdata import ParserData
from regexer import Regexer
from urihandler import UriHandler
from xbmcwrapper import XbmcWrapper


class Channel(chn_class.Channel):
    def __init__(self, channelInfo):
        """Initialisation of the class.

        Arguments:
        channelInfo: ChannelInfo - The channel info object to base this channel on.

        All class variables should be instantiated here and this method should not
        be overridden by any derived classes.

        """

        chn_class.Channel.__init__(self, channelInfo)

        # ============== Actual channel setup STARTS here and should be overwritten from derived classes ===============
        self.liveUrl = None

        # set context menu items
        # self.contextMenuItems.append(contextmenu.ContextMenuItem("Test Proxy Server", "CtMnTestProxy"))

        # setup the urls
        self.baseUrl = "http://www.bbc.co.uk/"
        self.swfUrl = "http://emp.bbci.co.uk/emp/SMPf/1.13.13/StandardMediaPlayerChromelessFlash.swf"

        self.noImage = "bbciplayerimage.png"
        self.mainListUri = "http://www.bbc.co.uk/iplayer"

        # setup the main parsing data
        self.episodeItemRegex = '<a class="letter stat" href="(?<url>/iplayer/a-z/[^"]+)">(?<title>[^<]+)</a>'\
                                .replace("(?<", "(?P<")
        self._AddDataParser(self.mainListUri, matchType=ParserData.MatchExact,
                            preprocessor=self.AddLiveChannels,
                            parser=self.episodeItemRegex, creator=self.CreateEpisodeItem)

        # Standard items
        self._AddDataParser("*", preprocessor=self.PreProcessFolderList)
        self.folderItemRegex = '<a href="(?<url>/iplayer/brand/[^"]+)"[^>]*>\W+<i[^>]+></i>\W+<span[^>]+>' \
                               '(?<title>[^<]+)<'.replace("(?<", "(?P<")
        self._AddDataParser("*", parser=self.folderItemRegex, creator=self.CreateFolderItem)
        self.videoItemRegex = '<a\W+href="/iplayer/episode/(?<url>[^/]+)[^>]+>\W+<div[^>]+>[^>]+' \
                              '</div>\W+(?:<div[^>]+>[^>]+</div>\W+)?[\w\W]{0,500}?<source ' \
                              'srcset="(?<thumburl>[^"]+)"[\w\W]{0,500}?<div class="secondary">' \
                              '\W+<div[^>]+>(?<title>[^<]+)</div>\W+(?:<div[^>]+>(?<subtitle>' \
                              '[^<]+)</div>\W+)?<p[^>]*>(?<description>[^<]*)</p>[\w\W]{0,1000}?' \
                              '(?:<span class="release">\W+First shown: (?<day>\d+) (?<month>\w+) ' \
                              '(?<year>\d+)|<div class="period")'
        self.videoItemRegex = Regexer.FromExpresso(self.videoItemRegex)
        self._AddDataParser("*", parser=self.videoItemRegex, creator=self.CreateVideoItem)

        # Live channels
        self._AddDataParser("http://vs-hds-uk-live.edgesuite.net/", updater=self.UpdateLiveItem)
        self._AddDataParser("http://a.files.bbci.co.uk/media/live/manifesto/", updater=self.UpdateLiveItem)

        # Generic updater
        self._AddDataParser("*", updater=self.UpdateVideoItem)

        # ===============================================================================================================
        # non standard items
        # if self.proxy:
        #     self.proxy.Filter = ["mediaselector"]

        self.searchUrl = "http://feeds.bbc.co.uk/iplayer/search/tv/?q=%s"
        self.programs = dict()

        # ===============================================================================================================
        # Test cases:
        # http://open.live.bbc.co.uk/mediaselector/5/select/version/2.0/mediaset/pc/vpid/b04plqyv/atk/

        # ====================================== Actual channel setup STOPS here =======================================
        return

    # noinspection PyUnusedLocal
    @LockWithDialog(logger=Logger.Instance())
    def CtMnTestProxy(self, item):  # :@UnusedVariable
        """ Checks if the proxy is OK"""

        if not self.proxy:
            message = "Proxy not configured: %s" % (self.proxy,)
        else:
            url = Config.UpdateUrl + "proxy"
            data = UriHandler.Open(url, proxy=self.proxy)
            # Logger.Trace(data)
            if data == "1":
                message = LanguageHelper.GetLocalizedString(LanguageHelper.ProxyOkId) % (self.proxy,)
            else:
                message = LanguageHelper.GetLocalizedString(LanguageHelper.ProxyNokId) % (self.proxy,)

        Logger.Debug(message)

        XbmcWrapper.ShowDialog("", message)
        pass

    def CreateEpisodeItem(self, resultSet):
        """Creates a new MediaItem for an episode

        Arguments:
        resultSet : list[string] - the resultSet of the self.episodeItemRegex

        Returns:
        A new MediaItem of type 'folder'

        This method creates a new MediaItem from the Regular Expression or Json
        results <resultSet>. The method should be implemented by derived classes
        and are specific to the channel.

        """

        Logger.Trace(resultSet)
        item = chn_class.Channel.CreateEpisodeItem(self, resultSet)
        if item is not None:
            item.name = "Shows: %s" % (item.name.upper(),)
        return item

    def PreProcessFolderList(self, data):
        """Performs pre-process actions for data processing/

        Arguments:
        data : string - the retrieve data that was loaded for the current item and URL.

        Returns:
        A tuple of the data and a list of MediaItems that were generated.


        Accepts an data from the ProcessFolderList method, BEFORE the items are
        processed. Allows setting of parameters (like title etc) for the channel.
        Inside this method the <data> could be changed and additional items can
        be created.

        The return values should always be instantiated in at least ("", []).

        """

        Logger.Info("Performing Pre-Processing")
        items = []

        if "episode.json" in self.parentItem.url:
            Logger.Debug("Fetching Carousel data")
            json = JsonHelper(data)
            data = json.GetValue("carousel")

        Logger.Debug("Pre-Processing finished")
        return data, items

    def CreateFolderItem(self, resultSet):
        """Creates a MediaItem of type 'folder' using the resultSet from the regex.

        Arguments:
        resultSet : tuple(strig) - the resultSet of the self.folderItemRegex

        Returns:
        A new MediaItem of type 'folder'

        This method creates a new MediaItem from the Regular Expression or Json
        results <resultSet>. The method should be implemented by derived classes
        and are specific to the channel.

        """

        Logger.Trace(resultSet)

        item = chn_class.Channel.CreateFolderItem(self, resultSet)
        brand = item.url[item.url.rindex("/") + 1:]

        # to match the first video regex: item.url = "http://www.bbc.co.uk/programmes/%s/episodes/player" % (brand, )
        item.url = "http://www.bbc.co.uk/iplayer/episodes/%s" % (brand,)
        item.isGeoLocked = True
        return item

    def CreateVideoItem(self, resultSet):
        """Creates a MediaItem of type 'video' using the resultSet from the regex.

        Arguments:
        resultSet : tuple (string) - the resultSet of the self.videoItemRegex

        Returns:
        A new MediaItem of type 'video' or 'audio' (despite the method's name)

        This method creates a new MediaItem from the Regular Expression or Json
        results <resultSet>. The method should be implemented by derived classes
        and are specific to the channel.

        If the item is completely processed an no further data needs to be fetched
        the self.complete property should be set to True. If not set to True, the
        self.UpdateVideoItem method is called if the item is focussed or selected
        for playback.

        """

        if "subtitle" in resultSet and not resultSet["subtitle"]:
            del resultSet["subtitle"]

        item = chn_class.Channel.CreateVideoItem(self, resultSet)
        vid = item.url.replace(self.baseUrl, "")
        # item.thumb = item.thumb.replace("192x108", "%sx%s" % (192 * 2, 108 * 2))
        item.url = "http://www.bbc.co.uk/iplayer/episode/%s" % (vid,)
        if "year" in resultSet and resultSet["year"]:
            month = DateHelper.GetMonthFromName(resultSet["month"], "en", short=True)
            item.SetDate(resultSet["year"], month, resultSet["day"])

        item.isGeoLocked = True
        # item.url = "http://open.live.bbc.co.uk/mediaselector/5/select/version/2.0/mediaset/pc/vpid/%s/atk/" % (vid,)
        return item

    def UpdateVideoItem(self, item):
        """
        Accepts an item. It returns an updated item.
        """
        Logger.Debug('Starting UpdateVideoItem for %s (%s)', item.name, self.channelName)

        Logger.Trace(item.url)
        if not item.url.startswith("http://www.bbc.co.uk/mediaselector/"):
            Logger.Debug("Determining the stream URL")
            data = UriHandler.Open(item.url, proxy=self.proxy)
            needle = '"vpid"\W*"([^"]+)"'
            vid = Regexer.DoRegex(needle, data)[-1]
            # streamDataUrl = "http://open.live.bbc.co.uk/mediaselector/4/mtis/stream/%s/" % (vid,)
            streamDataUrl = "http://open.live.bbc.co.uk/mediaselector/5/select/version/2.0/mediaset/iptv-all/vpid/%s" % (vid,)
            # streamDataUrl = "http://open.live.bbc.co.uk/mediaselector/5/select/version/2.0/mediaset/pc/vpid/%s" % (vid,)
        else:
            streamDataUrl = item.url

        # this URL is one from the webbrowser but requires a security part. So NOT:
        # streamDataUrl = "http://open.live.bbc.co.uk/mediaselector/5/select/version
        # /2.0/mediaset/pc/vpid/%s" % (vid,)
        #
        # but:
        # streamDataUrl = "http://open.live.bbc.co.uk/mediaselector/5/select/version
        # /2.0/mediaset/pc/vpid/%s/atk/2214e42b5729dcdd012dfb61a3054d39309ccd31/asn/1/
        # And I don't know where that one comes from

        part = item.CreateNewEmptyMediaPart()

        if True:
            streamData = UriHandler.Open(streamDataUrl, proxy=self.proxy)
        else:
            from debug.router import Router
            streamData = Router.GetVia("uk", streamDataUrl, self.proxy)

        connectionDatas = Regexer.DoRegex(
            '<media bitrate="(\d+)"[^>]+>\W*'
            '(<connection[^>]+>\W*)'
            '(<connection[^>]+>\W*)?'
            '(<connection[^>]+>\W*)?'
            '(<connection[^>]+>\W*)?</media>', streamData)

        for connectionData in connectionDatas:
            # first the bitrate
            bitrate = connectionData[0]
            Logger.Trace("Found Media: %s", connectionData)

            # go through the available connections
            for connection in connectionData[1:]:
                if not connection:
                    continue

                connectionXml = XmlHelper(connection)
                Logger.Trace("Analyzing Connection: %s", connection)
                supplier = connectionXml.GetTagAttribute("connection", {"supplier": None})
                protocol = connectionXml.GetTagAttribute("connection", {"protocol": None})
                transferFormat = connectionXml.GetTagAttribute("connection", {"transferFormat": None})
                Logger.Debug("Found connection information:\n"
                             "Protocol:       %s\n"
                             "TransferFormat: %s\n"
                             "Supplier:       %s\n"
                             "Bitrate:        %s",
                             protocol, transferFormat, supplier, bitrate)

                if protocol.startswith("http"):
                    if transferFormat != "hls":
                        Logger.Debug("Ignoring TransferFormat: %s", transferFormat)
                        continue
                    if "lime" in supplier or "mf_akamai_uk" in supplier:
                        Logger.Debug("Ignoring Supplier: %s", supplier)
                        continue
                    url = connectionXml.GetTagAttribute("connection", {"href": None})
                elif protocol.startswith("rtmp"):
                    Logger.Warning("Ignoring RTMP for now")
                    continue
                else:
                    Logger.Warning("Unknown protocol: %s", protocol)
                    continue

                #
                # # port: we take the default one
                # # determine protocol
                # protocol = connectionXml.GetTagAttribute("connection", {"protocol": None})
                # if protocol == "http":
                #     Logger.Debug("Http stream found, skipping for now.")
                #     continue
                #
                # elif protocol == "":
                #     protocol = "rtmp"
                # Logger.Debug("Found protocol      : %s", protocol)
                #
                # # now for the non-http version, we need application, authentication, server, file and kind
                # application = connectionXml.GetTagAttribute("connection", {"application": None})
                # if application == "":
                #     application = "ondemand"
                # Logger.Debug("Found application   : %s", application)
                #
                # authentication = connectionXml.GetTagAttribute("connection", {"authString": None})
                # authentication = htmlentityhelper.HtmlEntityHelper.ConvertHTMLEntities(authentication)
                # Logger.Debug("Found authentication: %s", authentication)
                #
                # server = connectionXml.GetTagAttribute("connection", {"server": None})
                # Logger.Debug("Found server        : %s", server)
                #
                # fileName = connectionXml.GetTagAttribute("connection", {"identifier": None})
                # Logger.Debug("Found identifier    : %s", fileName)
                #
                # kind = connectionXml.GetTagAttribute("connection", {"kind": None})
                # Logger.Debug("Found kind          : %s", kind)
                #
                # Logger.Trace("XML: %s\nProtocol: %s, Server: %s, Application: %s, Authentication: %s, File: %s , Kind: %s", connection, protocol, server, application, authentication, fileName, kind)
                # if "akamai" in kind:
                #     Logger.Debug("Not including AKAMAI streams")
                #     continue
                #     # url = "%s://%s/%s?%s playpath=%s?%s" % (protocol, server, application, authentication, fileName, authentication)
                #     # Logger.Debug("Creating RTMP for Akamai type\n%s", url)
                #
                # elif kind == "limelight":
                #     # for limelight we need to be more specific on what to play
                #     url = "%s://%s/ app=%s?%s tcurl=%s://%s/%s?%s playpath=%s" % (
                #         protocol, server, application, authentication, protocol, server, application, authentication,
                #         fileName)
                #     Logger.Debug("Creating RTMP for LimeLight type\n%s", url)
                # else:
                #     # for a none-limelight we just compose a RTMP stream
                #     url = "%s://%s/%s?%s playpath=%s" % (protocol, server, application, authentication, fileName)
                #     Logger.Debug("Creating RTMP for a None-LimeLight type\n%s", url)
                # url = self.GetVerifiableVideoUrl(url)

                # if liveStream:
                #     url = "%s live=1" % (url, )
                part.AppendMediaStream(url, bitrate)

        # get the subtitle
        subtitles = Regexer.DoRegex('<connection href="(http://www.bbc.co.uk/iplayer/subtitles/[^"]+/)([^/]+.xml)"',
                                    streamData)
        if len(subtitles) > 0:
            subtitle = subtitles[0]
            subtitleUrl = "%s%s" % (subtitle[0], subtitle[1])
            part.Subtitle = subtitlehelper.SubtitleHelper.DownloadSubtitle(subtitleUrl, subtitle[1], "ttml",
                                                                           proxy=self.proxy)

        item.complete = True
        Logger.Trace('finishing UpdateVideoItem: %s.', item)
        return item

    def AddLiveChannels(self, data):
        """Performs pre-process actions for data processing/

        Arguments:
        data : string - the retrieve data that was loaded for the current item and URL.

        Returns:
        A tuple of the data and a list of MediaItems that were generated.


        Accepts an data from the ProcessFolderList method, BEFORE the items are
        processed. Allows setting of parameters (like title etc) for the channel.
        Inside this method the <data> could be changed and additional items can
        be created.

        The return values should always be instantiated in at least ("", []).

        """

        Logger.Info("Generating Live channels")

        liveChannels = [
            {"name": "BBC 1 HD", "code": "bbc_one_hd", "image": "bbc1large.png"},
            {"name": "BBC 2 HD", "code": "bbc_two_hd", "image": "bbc2large.png"},
            {"name": "BBC 3 HD", "code": "bbc_three_hd", "image": "bbc3large.png"},
            {"name": "BBC 4 HD", "code": "bbc_four_hd", "image": "bbc4large.png"},
            {"name": "CBBC", "code": "cbbc_hd", "image": "cbbclarge.png"},
            {"name": "CBeebies", "code": "cbeebies_hd", "image": "cbeebieslarge.png"},
            {"name": "BBC News Channel", "code": "bbc_news24", "image": "bbcnewslarge.png"},
            {"name": "BBC Parliament", "code": "bbc_parliament", "image": "bbcparliamentlarge.png"},
            {"name": "Alba", "code": "bbc_alba", "image": "bbcalbalarge.png"},

            {"name": "S4C", "code": "s4cpbs", "image": "bbchdlarge.png"},
            {"name": "BBC One London", "code": "bbc_one_london", "image": "bbchdlarge.png"},
            {"name": "BBC One Scotland", "code": "bbc_one_scotland_hd", "image": "bbchdlarge.png"},
            {"name": "BBC One Northern Ireland", "code": "bbc_one_northern_ireland_hd", "image": "bbchdlarge.png"},
            {"name": "BBC One Wales", "code": "bbc_one_wales_hd", "image": "bbchdlarge.png"},
            {"name": "BBC Two Scotland", "code": "bbc_two_scotland", "image": "bbchdlarge.png"},
            {"name": "BBC Two Northern Ireland", "code": "bbc_two_northern_ireland_digital", "image": "bbchdlarge.png"},
            {"name": "BBC Two Wales", "code": "bbc_two_wales_digital", "image": "bbchdlarge.png"},
        ]

        live = mediaitem.MediaItem("Live Channels", "")
        live.dontGroup = True
        live.type = "folder"

        for channel in liveChannels:
            url = "http://a.files.bbci.co.uk/media/live/manifesto/audio_video/simulcast/hds/uk/pc/ak/%(code)s.f4m" % channel
            item = mediaitem.MediaItem(channel["name"], url)
            item.isGeoLocked = True
            item.isLive = True
            item.type = "video"
            item.complete = False
            item.thumb = self.GetImageLocation(channel["image"])
            live.items.append(item)

        return data, [live, ]

    def UpdateLiveItem(self, item):
        """
        Accepts an item. It returns an updated item.
        """
        Logger.Debug('Starting UpdateLiveItem for %s (%s)', item.name, self.channelName)
        data = UriHandler.Open(item.url, proxy=self.proxy, additionalHeaders=self.httpHeaders)
        streamRoot = Regexer.DoRegex('<media href="([^"]+\.isml)', data)[0]
        Logger.Debug("Found Live stream root: %s", streamRoot)
        # url = "%s/master.m3u8" % (streamRoot, )
        #
        # part = item.CreateNewEmptyMediaPart()
        # for s, b in M3u8.GetStreamsFromM3u8(url, self.proxy):
        #     item.complete = True
        #     # s = self.GetVerifiableVideoUrl(s)
        #     part.AppendMediaStream(s, b)

        part = item.CreateNewEmptyMediaPart()
        for s, b in F4m.GetStreamsFromF4m(item.url, self.proxy):
            item.complete = True
            # s = self.GetVerifiableVideoUrl(s)
            s = s.replace(".f4m", ".m3u8")
            part.AppendMediaStream(s, b)

        return item

    def __GetDate(self, date):
        # actual_start=2014-12-07T10:03:56+0000
        datePart, timePart = date.split("T")
        year, month, day = datePart.split("-")
        hour, minute, ignore = timePart.split(":")
        # Logger.Trace((year, month, day, hour, minute, 0))
        return year, month, day, hour, minute, 0
