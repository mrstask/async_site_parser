import os
auth_login = 'ksnsuomi'
auth_password = 'ssksnnnmi'
start_url = 'http://xn--90abjzldcl.xn--p1ai' # url without ending slash
project_directory = os.getcwd() + '/'


USELESS_APPLICATIONS_TYPES = """application/epub+zip
application/java-archive
application/ld+json
application/msword
application/octet-stream
application/ogg
application/pdf
application/rtf
application/vnd.amazon.ebook
application/vnd.apple.installer+xml
application/vnd.mozilla.xul+xml
application/vnd.ms-excel
application/vnd.ms-fontobject
application/vnd.ms-powerpoint
application/vnd.oasis.opendocument.presentation
application/vnd.oasis.opendocument.spreadsheet
application/vnd.oasis.opendocument.text
application/vnd.openxmlformats-officedocument.presentationml.presentation
application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
application/vnd.openxmlformats-officedocument.wordprocessingml.document
application/vnd.visio
application/x-7z-compressed
application/x-abiword
application/x-bzip
application/x-bzip2
application/x-csh
application/x-freearc
application/x-rar-compressed
application/x-sh
application/x-shockwave-flash
application/x-tar
application/xhtml+xml
application/xml if not readable from casual users (RFC 3023, section 3)
application/zip""".splitlines()
USELESS_VIDEO_TYPES = """video/3gpp
video/3gpp2
video/mpeg
video/ogg
video/webm
video/x-msvideo
""".splitlines()
USELESS_AUDIO_TYPES = """audio/3gpp
audio/3gpp2
audio/aac
audio/midi
audio/midi
audio/mpeg
audio/ogg
audio/wav
audio/webm""".splitlines()
USELESS_TEXT_TYPES = """text/calendar
text/csv
text/plain
""".splitlines()

IMAGE_TYPES = """image/bmp
image/gif
image/jpeg
image/jpeg
image/png
image/svg+xml
image/tiff
image/tiff
image/vnd.microsoft.icon
image/webp""".splitlines()
FONT_TYPES = """font/otf
font/ttf
font/woff
font/woff2""".splitlines()

USELESS_TYPES = USELESS_APPLICATIONS_TYPES + USELESS_AUDIO_TYPES + USELESS_VIDEO_TYPES + USELESS_TEXT_TYPES
TO_SAVE_TYPES = IMAGE_TYPES + FONT_TYPES