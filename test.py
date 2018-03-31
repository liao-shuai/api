#  _*_ coding:utf-8  _*_

import requests

adcode = raw_input('城市编码：460106')
AMapWeatherKey = "baba7d7841eb38eb35cd0dcf9cd41cbf"
value = {
    'city': adcode,
    'key': AMapWeatherKey,
    'extensions': 'all',
    'output': 'JSON'
}
url = 'http://restapi.amap.com/v3/weather/weatherInfo?parameters'
weather_data = requests.get(url, params=value)
weather = weather_data.json()["forecasts"][0]
# weatherData['city'] = weather['city']
# weatherData['reporttime'] = weather['reporttime']
city = weather['city']
reporttime = weather['reporttime']
casts = weather['casts'][0]
# weatherData['dayweather'] = casts['dayweather']
# weatherData['daytemp'] = casts['daytemp']
# weatherData['daywind'] = casts['daywind']
# weatherData['daypower'] = casts['daypower']
dayweather = casts['dayweather']
daytemp = casts['daytemp']
daywind = casts['daywind']
daypower = casts['daypower']
# "深圳市,多云,-27度,西风,1级,2016-11-14 10:00:00更新"
# weather_str = "{},{},{},{},{},{}".format(city, dayweather, daytemp, daywind, daypower, reporttime)
weather_str = u"%s,%s,%s,%s,%s,%s 更新" % (city, dayweather, daytemp, daywind, daypower, reporttime)
print url
print weather_str
# print city,dayweather,daytemp,daypower,daywind




# 获取字典中的lon和lat对应的值，适用于字典嵌套
    # dict:字典
    # lon/lat:目标key
    # default:找不到时返回的默认值


    # @classmethod
    # def dict_get(self, dict, objkey, default):
    #     tmp = dict
    #     for k, v in tmp.items():
    #         if k == objkey:
    #             return v
    #         else:
    #             if type(v) is types.DictType:
    #                 ret = self.dict_get(v, objkey, default)
    #                 if ret is not default:
    #                     return ret
    #     return default
    #
    # def dict_get_key(self, dict):
    #     for k,v in dict.items():
    #         return k