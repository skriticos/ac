import os
import distutils.dir_util

from wx.lib.pubsub import Publisher

from AniChou import service, preferences

# Plugin.
import AniChou.mal

prefs = preferences.Defaults()

# Global.
sites = {}
for service in service.SiteProvider.plugins:
    sites[service.name] = service()
# Global.
accounts = {}
# Array.
for account in prefs["accounts"]:
    accounts[account["handle"]] = sites[account["site"]].account(account)

print sites["myal"].search("Ichigo Mashimaro")

#accounts["A"].model = accounts["A"].pull()
#accounts["A"].save()
print accounts["A"].model

Publisher().sendMessage("save")