"""
Your sources needs to be listed here to allow their discovery by SourceBase class
"""
from .analytics import GoogleAnalyticsSource
from .athena import AthenaSource
from .const import ConstSource
from .http.xpath import HttpXPathSource
from .jira import JiraSource
from .logstash import LogstashSource
from .mysql import MysqlSource
