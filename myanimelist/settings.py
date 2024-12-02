# -*- coding: utf-8 -*-

# Scrapy settings for myanimelist project

BOT_NAME = 'myanimelist'

SPIDER_MODULES = ['myanimelist.spiders']
NEWSPIDER_MODULE = 'myanimelist.spiders'

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# User-Agent setup
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'

# Configure a delay for requests for the same website (default: 0)
DOWNLOAD_DELAY = 1  # Adjust delay to avoid rate-limiting
RANDOMIZE_DOWNLOAD_DELAY = True  # Randomize the download delay for more natural requests

# Enable AutoThrottle
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 0.5  # Initial delay
AUTOTHROTTLE_MAX_DELAY = 10     # Maximum delay (increase for slow responses)
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0  # Number of concurrent requests Scrapy sends
AUTOTHROTTLE_DEBUG = False  # Show throttling stats (set to True for debugging)

# Retry settings
RETRY_ENABLED = True
RETRY_TIMES = 8  # Number of times to retry before failing
RETRY_HTTP_CODES = [500, 502, 503, 504, 408, 429]  # HTTP codes to retry
RETRY_PRIORITY_ADJUST = -1  # Lower priority for retried requests

# Enable HTTP Cache (optional, useful for debugging and testing)
HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 3600  # Cache expiration in seconds
HTTPCACHE_DIR = 'httpcache'
HTTPCACHE_IGNORE_HTTP_CODES = [401, 403, 404, 500]
HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

# Enable cookies
COOKIES_ENABLED = False

# Configure concurrent requests (reduce if throttled)
CONCURRENT_REQUESTS = 16
CONCURRENT_REQUESTS_PER_DOMAIN = 8
CONCURRENT_REQUESTS_PER_IP = 4  # Reduce if throttled or blocked

# Pipelines
ITEM_PIPELINES = {
   'myanimelist.pipelines.ProcessPipeline': 300,
   'myanimelist.pipelines.SaveLocalPipeline': 301,
   # 'myanimelist.pipelines.SaveMongoPipeline': 302,  # Uncomment if using MongoDB
}

# HTTP Error codes to allow
HTTPERROR_ALLOWED_CODES = [405]  # Allow 405 HTTP response for processing

# Log level
LOG_LEVEL = 'INFO'

# Timeout settings
DOWNLOAD_TIMEOUT = 60  # Timeout in seconds (increase for slow websites)

# Enable DNS cache for better performance
DNSCACHE_ENABLED = True

# Disable Telnet Console (enabled by default)
TELNETCONSOLE_ENABLED = False

# Handle response data loss gracefully
DOWNLOAD_FAIL_ON_DATALOSS = False  # Prevent crashes on partial/broken responses
