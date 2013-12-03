# Copyright, John Rusnak, 2012
    # This code binding is available under the license agreement of the LGPL with
    # an additional constraint described below,
    # and with the understanding that the webkit API is copyright protected
    # by Apple Computer, Inc. (see below).
    # There is an  additional constraint that any derivatives of this work aimed
    # at providing bindings to GObject, GTK, GDK, or WebKit be strictly
    # python-only bindings with no native code.
    # * THIS SOFTWARE IS PROVIDED ``AS IS'' AND ANY
    # * EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
    # * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
    # * PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL APPLE COMPUTER, INC. OR
    # * CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
    # * EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
    # * PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
    # * PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY
    # * OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
    # * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
    # * OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
    #
    # ******************************************************
    # For the API:
    # /*
    # * Copyright (C) 2006 Apple Computer, Inc.  All rights reserved.
    # *
    # * Redistribution and use in source and binary forms, with or without
    # * modification, are permitted provided that the following conditions
    # * are met:
    # * 1. Redistributions of source code must retain the above copyright
    # *    notice, this list of conditions and the following disclaimer.
    # * 2. Redistributions in binary form must reproduce the above copyright
    # *    notice, this list of conditions and the following disclaimer in the
    # *    documentation and/or other materials provided with the distribution.
    # *
    # * THIS SOFTWARE IS PROVIDED BY APPLE COMPUTER, INC. ``AS IS'' AND ANY
    # * EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
    # * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
    # * PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL APPLE COMPUTER, INC. OR
    # * CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
    # * EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
    # * PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
    # * PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY
    # * OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
    # * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
    # * OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
    # */
from ctypes import *
from gtk3_types import *
from gtk3_enums import *
from gobject_types import *
from gobject_enums import *

    
"""Derived Pointer Types"""
_GtkRcStyle = POINTER(c_int)
_GdkGeometry = POINTER(c_int)
_PangoFont = POINTER(c_int)
_WebKitNetworkResponse = POINTER(c_int)
_GInterface = POINTER(c_int)
_GdkPixbuf = POINTER(c_int)
_GtkBin = POINTER(c_int)
_GtkRequisition = POINTER(c_int)
_GtkRcStyle = POINTER(c_int)
_WebKitWebPolicyDecision = POINTER(c_int)
_PangoEngineShape = POINTER(c_int)
_GtkRegionFlags = POINTER(c_int)
_cairo_surface_t = POINTER(c_int)
_WebKitDOMNode = POINTER(c_int)
_GtkWindow = POINTER(c_int)
_cairo_font_options_t = POINTER(c_int)
_JSValue = POINTER(c_int)
_JSContext = POINTER(c_int)
_GtkIconFactory = POINTER(c_int)
_GdkAtom = POINTER(c_int)
_GMainLoop = POINTER(c_int)
_GdkTimeCoord = POINTER(c_int)
_GdkColor = POINTER(c_int)
_GtkWidgetPath = POINTER(c_int)
_GtkContainer = POINTER(c_int)
_PangoItem = POINTER(c_int)
_GClosure = POINTER(c_int)
_GAppInfo = POINTER(c_int)
_GMainContext = POINTER(c_int)
_GdkDisplay = POINTER(c_int)
_GtkStyleProvider = POINTER(c_int)
_GtkScrolledWindow = POINTER(c_int)
_GFileEnumerator = POINTER(c_int)
_GtkDialog = POINTER(c_int)
_WebKitWebWindowFeatures = POINTER(c_int)
_GInputStream = POINTER(c_int)
_JSObject = POINTER(c_int)
_WebKitWebResource = POINTER(c_int)
_GBytes = POINTER(c_int)
_GScanner = POINTER(c_int)
_PangoFont = POINTER(c_int)
_GtkStyleContext = POINTER(c_int)
_GMainContext = POINTER(c_int)
_GtkTextBuffer = POINTER(c_int)
_GtkTargetList = POINTER(c_int)
_WebKitWebSettings = POINTER(c_int)
_GdkAppLaunchContext = POINTER(c_int)
_GObject = POINTER(c_int)
_PangoLayout = POINTER(c_int)
_WebKitWebBackForwardList = POINTER(c_int)
_GtkOffscreenWindow = POINTER(c_int)
_GParamSpec = POINTER(c_int)
_GAppLaunchContext = POINTER(c_int)
_PangoAttrIterator = POINTER(c_int)
_GtkRequisition = POINTER(c_int)
_GtkIconSet = POINTER(c_int)
_GtkSelectionData = POINTER(c_int)
_GtkWindowGroup = POINTER(c_int)
_GtkAdjustment = POINTER(c_int)
_JSGlobalContext = POINTER(c_int)
_GApplication = POINTER(c_int)
_GFileMonitor = POINTER(c_int)
_PangoLogAttr = POINTER(c_int)
_GString = POINTER(c_int)
_GFileAttributeMatcher = POINTER(c_int)
_PangoContext = POINTER(c_int)
_JSPropertyNameArray = POINTER(c_int)
_WebKitWebSettings = POINTER(c_int)
_GBoxed = POINTER(c_int)
_GtkPathPriorityType = POINTER(c_int)
_JSClass = POINTER(c_int)
_WebKitWebHistoryItem = POINTER(c_int)
_JSValue = POINTER(c_int)
_GAppInfo = POINTER(c_int)
_GtkSettings = POINTER(c_int)
_GSource = POINTER(c_int)
_PangoFontMap = POINTER(c_int)
_GIOStream = POINTER(c_int)
_GIOStream = POINTER(c_int)
_JSString = POINTER(c_int)
_PangoAttrList = POINTER(c_int)
_GOutputStream = POINTER(c_int)
_PangoMatrix = POINTER(c_int)
_GSource = POINTER(c_int)
_GtkApplication = POINTER(c_int)
_PangoAnalysis = POINTER(c_int)
_GMutex = POINTER(c_int)
_PangoFontDescription = POINTER(c_int)
_GdkGeometry = POINTER(c_int)
_GAppLauncContext = POINTER(c_int)
_GdkCursor = POINTER(c_int)
_GtkBorder = POINTER(c_int)
_WebKitWebInspector = POINTER(c_int)
_GdkWindowAttr = POINTER(c_int)
_GOptionGroup = POINTER(c_int)
_GScanner = POINTER(c_int)
_GFileAttributeInfoList = POINTER(c_int)
_GCancellable = POINTER(c_int)
_GtkWidgetClass = POINTER(c_int)
_GtkContainerClass = POINTER(c_int)
_GdkEventKey = POINTER(c_int)
_GtkAdjustment = POINTER(c_int)
_GdkDragContext = POINTER(c_int)
_GtkAssistant = POINTER(c_int)
_GdkDisplay = POINTER(c_int)
_GtkCssProvider = POINTER(c_int)
_GAppLaunchContext = POINTER(c_int)
_GtkWidgetPath = POINTER(c_int)
_GdkScreen = POINTER(c_int)
_PangoFontMetrics = POINTER(c_int)
_GCond = POINTER(c_int)
_GtkIconSource = POINTER(c_int)
_GAsyncResult = POINTER(c_int)
_GdkVisual = POINTER(c_int)
_PangoFontMap = POINTER(c_int)
_GSList = POINTER(c_int)
_WebKitWebFrame = POINTER(c_int)
_JSString = POINTER(c_int)
_GActionGroup = POINTER(c_int)
_GtkWidget = POINTER(c_int)
_WebKitNetworkRequest = POINTER(c_int)
_GdkWindow = POINTER(c_int)
_PangoFontFamily = POINTER(c_int)
_JSContextGroup = POINTER(c_int)
_GFile = POINTER(c_int)
_PangoLayoutIter = POINTER(c_int)
_cairo_region_t = POINTER(c_int)
_GFileInputStream = POINTER(c_int)
_PangoFontset = POINTER(c_int)
_GdkWindow = POINTER(c_int)
_PangoFontDescription = POINTER(c_int)
_GtkBorder = POINTER(c_int)
_JSPropertyNameArray = POINTER(c_int)
_GError = POINTER(c_int)
_PangoCoverage = POINTER(c_int)
_GIcon = POINTER(c_int)
_WebKitViewportAttributes = POINTER(c_int)
_JSClass = POINTER(c_int)
_WebKitWebHistoryItem = POINTER(c_int)
_PangoFontFamily = POINTER(c_int)
_cairo_t = POINTER(c_int)
_GWeakRef = POINTER(c_int)
_GtkAboutDialog = POINTER(c_int)
_GdkVisual = POINTER(c_int)
_GdkEventButton = POINTER(c_int)
_GCancellable = POINTER(c_int)
_GdkDevice = POINTER(c_int)
_GMount = POINTER(c_int)
_PangoRectangle = POINTER(c_int)
_GtkAccelGroup = POINTER(c_int)
_GObject = POINTER(c_int)
_GPollFD = POINTER(c_int)
_GtkIconSource = POINTER(c_int)
_GFile = POINTER(c_int)
_JSContext = POINTER(c_int)
_GFileOutputStream = POINTER(c_int)
_PangoFontsetSimple = POINTER(c_int)
_GtkAllocation = POINTER(c_int)
_GtkWidget = POINTER(c_int)
_PangoLayoutLine = POINTER(c_int)
_GtkIconSet = POINTER(c_int)
_WebKitWebView = POINTER(c_int)
_PangoTabArray = POINTER(c_int)
_WebKitHitTestResult = POINTER(c_int)
_GValue = POINTER(c_int)
_GdkDeviceManager = POINTER(c_int)
_GdkCursor = POINTER(c_int)
_WebKitDOMDocument = POINTER(c_int)
_PangoMatrix = POINTER(c_int)
_GtkPrintOperation = POINTER(c_int)
_GString = POINTER(c_int)
_PangoContext = POINTER(c_int)
_GtkTargetList = POINTER(c_int)
_GFileInfo = POINTER(c_int)
_GList = POINTER(c_int)
_WebKitWebView = POINTER(c_int)
_WebKitWebWindowFeatures = POINTER(c_int)
_PangoCoverage = POINTER(c_int)
_GParamSpec = POINTER(c_int)
_GList = POINTER(c_int)
_GdkRGBA = POINTER(c_int)
_GTimeVal = POINTER(c_int)
_GtkInvisible = POINTER(c_int)
_GSourceFuncs = POINTER(c_int)
_JSPropertyNameAccumulator = POINTER(c_int)
_PangoGlyphString = POINTER(c_int)
_JSGlobalContext = POINTER(c_int)
_GFileIOStream = POINTER(c_int)
_WebKitSecurityOrigin = POINTER(c_int)
_GObjectClass = POINTER(c_int)
_GSList = POINTER(c_int)
_PangoAnalysis = POINTER(c_int)
_GdkWindowAttr = POINTER(c_int)
_SoupMessage = POINTER(c_int)
_WebKitWebDataSource = POINTER(c_int)
_GdkAtom = POINTER(c_int)
_GdkColor = POINTER(c_int)
_JSContextGroup = POINTER(c_int)
_GdkRectangle = POINTER(c_int)
_PangoLanguage = POINTER(c_int)
_PangoAttrList = POINTER(c_int)
_gunichar = POINTER(c_int)
_GFileAttributeMatcher = POINTER(c_int)
_GdkWMDecoration = POINTER(c_int)
_PangoLogAttr = POINTER(c_int)
_PangoLayout = POINTER(c_int)
_GPollFD = POINTER(c_int)
_JSObject = POINTER(c_int)
_GdkDragContext = POINTER(c_int)
_GInputStream = POINTER(c_int)
_GFileIOStream = POINTER(c_int)
_WebKitWebNavigationAction = POINTER(c_int)
_GtkStyle = POINTER(c_int)
_GParameter = POINTER(c_int)
_GtkStyle = POINTER(c_int)
_GIcon = POINTER(c_int)
_GtkWindow = POINTER(c_int)
_PangoLayoutRun = POINTER(c_int)
_cairo_pattern_t = POINTER(c_int)
_GdkPixbuf = POINTER(c_int)
_WebKitGeolocationPolicyDecision = POINTER(c_int)
_GMountOperation = POINTER(c_int)
_GtkSettings = POINTER(c_int)
_GSourceCallbackFuncs = POINTER(c_int)
_GtkCssSection = POINTER(c_int)
_PangoFontFace = POINTER(c_int)
_GtkTargetEntry = POINTER(c_int)
_GtkApplication = POINTER(c_int)
_GtkClipboard = POINTER(c_int)
_GFileInfo = POINTER(c_int)
_GByteArray = POINTER(c_int)
_GdkScreen = POINTER(c_int)
_PangoLanguage = POINTER(c_int)
_GdkDevice = POINTER(c_int)
_PangoTabArray = POINTER(c_int)
"""Enumerations"""
GtkWidgetHelpType = c_int
GtkTextDirection = c_int
GtkSizeRequestMode = c_int
GtkAlign = c_int
GdkPixbufError = c_int
GdkColorspace = c_int
GdkPixbufAlphaMode = c_int
GtkIconSize = c_int
GdkWindowType = c_int
GdkWindowWindowClass = c_int
GdkWindowHints = c_int
GdkGravity = c_int
GdkWindowEdgeh = c_int
GdkWindowTypeHint = c_int
GdkWindowAttributesType = c_int
GdkFilterReturn = c_int
GdkModifierType = c_int
GdkWMDecoration = c_int
GdkWMFunction = c_int
GdkInputSource = c_int
GdkInputMode = c_int
GdkAxisUse = c_int
GdkDeviceType = c_int
GdkGrabOwnership = c_int
GdkCursorType = c_int
GdkVisualType = c_int
GdkByteOrder = c_int
PangoStyle = c_int
PangoWeight = c_int
PangoVariant = c_int
PangoStretch = c_int
PangoFontMask = c_int
GtkRcFlags = c_int
GtkRcTokenType = c_int
PangoWrapMode = c_int
PangoEllipsizeMode = c_int
PangoAlignment = c_int
WebKitLoadStatus = c_int
WebKitNavigationResponse = c_int
WebKitWebViewTargetInfo = c_int
WebKitWebViewViewMode = c_int
WebKitEditingBehavior = c_int
GdkInputSource = c_int
GdkInputMode = c_int
GdkAxisUse = c_int
GdkDeviceType = c_int
GdkGrabOwnership = c_int
GApplicationFlags = c_int
GtkDialogFlags = c_int
GtkResponseType = c_int
WebKitWebNavigationReason = c_int
PangoWrapMode = c_int
PangoEllipsizeMode = c_int
PangoAlignment = c_int
GdkPixbufError = c_int
GdkColorspace = c_int
GdkPixbufAlphaMode = c_int
GtkLicense = c_int
GtkIconSize = c_int
GtkAssistantPageType = c_int
GtkRcFlags = c_int
GtkRcTokenType = c_int
GtkDestDefaults = c_int
GtkTargetFlags = c_int

try:
   libgobject.g_cancellable_is_cancelled.restype = gboolean
libgobject.g_cancellable_is_cancelled.argtypes = [_GCancellable]
except:
   pass
try:
   libgobject.g_cancellable_source_new.restype = _GSource
libgobject.g_cancellable_source_new.argtypes = [_GCancellable]
except:
   pass
try:
   libgobject.g_cancellable_release_fd.restype = None
libgobject.g_cancellable_release_fd.argtypes = [_GCancellable]
except:
   pass
try:
   libgobject.g_cancellable_connect.restype = gulong
libgobject.g_cancellable_connect.argtypes = [_GCancellable,GCallback,gpointer,GDestroyNotify]
except:
   pass
try:
   libgobject.g_cancellable_get_fd.restype = int
libgobject.g_cancellable_get_fd.argtypes = [_GCancellable]
except:
   pass
try:
   libgobject.g_cancellable_make_pollfd.restype = gboolean
libgobject.g_cancellable_make_pollfd.argtypes = [_GCancellable,_GPollFD]
except:
   pass
try:
   libgobject.g_cancellable_cancel.restype = None
libgobject.g_cancellable_cancel.argtypes = [_GCancellable]
except:
   pass
try:
   libgobject.g_cancellable_pop_current.restype = None
libgobject.g_cancellable_pop_current.argtypes = [_GCancellable]
except:
   pass
try:
   libgobject.g_cancellable_push_current.restype = None
libgobject.g_cancellable_push_current.argtypes = [_GCancellable]
except:
   pass
try:
   libgobject.g_cancellable_disconnect.restype = None
libgobject.g_cancellable_disconnect.argtypes = [_GCancellable,gulong]
except:
   pass
try:
   libgobject.g_cancellable_reset.restype = None
libgobject.g_cancellable_reset.argtypes = [_GCancellable]
except:
   pass
try:
   libgobject.g_cancellable_set_error_if_cancelled.restype = gboolean
libgobject.g_cancellable_set_error_if_cancelled.argtypes = [_GCancellable,_GError]
except:
   pass
try:
libgobject.g_cancellable_get_current.restype = _GCancellable
libgobject.g_cancellable_get_current.argtypes = []
except:
   pass
import gobject__GObject
class GCancellable( gobject__GObject.GObject):
    """Class GCancellable Constructors"""
    def __init__( self,  obj = None):
        if obj: self._object = obj
        else:
            libgobject.g_cancellable_new.restype = POINTER(c_int)
            
            libgobject.g_cancellable_new.argtypes = []
            self._object = libgobject.g_cancellable_new()

    """Methods"""
    def is_cancelled(  self, ):

        
        return libgobject.g_cancellable_is_cancelled( self._object )

    def source_new(  self, ):

        from gobject import GSource
        return GSource(None,None, obj=libgobject.g_cancellable_source_new( self._object ) or POINTER(c_int)())

    def release_fd(  self, ):

        
        libgobject.g_cancellable_release_fd( self._object )

    def connect(  self, callback, data, data_destroy_func, ):
        if callback: callback = callback._object
        else: callback = POINTER(c_int)()

        
        return libgobject.g_cancellable_connect( self._object,callback,data,data_destroy_func )

    def get_fd(  self, ):

        
        return libgobject.g_cancellable_get_fd( self._object )

    def make_pollfd(  self, pollfd, ):
        if pollfd: pollfd = pollfd._object
        else: pollfd = POINTER(c_int)()

        
        return libgobject.g_cancellable_make_pollfd( self._object,pollfd )

    def cancel(  self, ):

        
        libgobject.g_cancellable_cancel( self._object )

    def pop_current(  self, ):

        
        libgobject.g_cancellable_pop_current( self._object )

    def push_current(  self, ):

        
        libgobject.g_cancellable_push_current( self._object )

    def disconnect(  self, handler_id, ):

        
        libgobject.g_cancellable_disconnect( self._object,handler_id )

    def reset(  self, ):

        
        libgobject.g_cancellable_reset( self._object )

    def set_error_if_cancelled(  self, error, ):
        if error: error = error._object
        else: error = POINTER(c_int)()

        
        return libgobject.g_cancellable_set_error_if_cancelled( self._object,error )

    @staticmethod
    def get_current():
        from gobject import GCancellable
        return GCancellable( obj=    libgobject.g_cancellable_get_current()
 or POINTER(c_int)())
