#!/usr/bin/env python
# coding=utf8
from burp import IBurpExtender
from burp import IHttpListener
from burp import IHttpRequestResponse
from burp import IResponseInfo

import re
# Class BurpExtender (Required) contaning all functions used to interact with Burp Suite API
info='''author:stayliv3.github.io
modify:syunaht.com'''
print(info)


class BurpExtender(IBurpExtender, IHttpListener):

    # define registerExtenderCallbacks: From IBurpExtender Interface
    def registerExtenderCallbacks(self, callbacks):

        # keep a reference to our callbacks object (Burp Extensibility Feature)
        self._callbacks = callbacks
        # obtain an extension helpers object (Burp Extensibility Feature)
        # http://portswigger.net/burp/extender/api/burp/IExtensionHelpers.html
        self._helpers = callbacks.getHelpers()
        # set our extension name that will display in Extender Tab
        self._callbacks.setExtensionName("Unicode Auto Decode")
        # register ourselves as an HTTP listener
        callbacks.registerHttpListener(self)

    # define processHttpMessage: From IHttpListener Interface
    def processHttpMessage(self, toolFlag, messageIsRequest, messageInfo):

        # determine what tool we would like to pass though our extension:
        if toolFlag == 64 or toolFlag == 16 or toolFlag == 32:  # if tool is Proxy Tab or repeater
            # determine if request or response:
            if not messageIsRequest:  # only handle responses
                response = messageInfo.getResponse()
                # get Response from IHttpRequestResponse instance
                analyzedResponse = self._helpers.analyzeResponse(
                    response)  # returns IResponseInfo
                headers = analyzedResponse.getHeaders()
                # 替换iso8859-1
                # iterate though list of headers
                new_headers = []
                for header in headers:
                    # Look for Content-Type Header)
                    if header.startswith("Content-Type:"):
                        # Look for HTML response
                        new_headers.append(
                            header.replace('iso-8859-1', 'utf-8'))
                    else:
                        new_headers.append(header)

                body = response[analyzedResponse.getBodyOffset():]
                body_string = body.tostring()
                u_char_escape = re.findall(r'(?:\\u[\d\w]{4})+', body_string)
                if u_char_escape:
                    for i in u_char_escape:
                        u_char = i.decode('unicode_escape').encode('utf8')
                        body_string = body_string.replace(
                            i, '--u--'+u_char+'--u--')
                    new_body = self._helpers.bytesToString(body_string)
                    messageInfo.setResponse(
                        self._helpers.buildHttpMessage(new_headers, new_body))
